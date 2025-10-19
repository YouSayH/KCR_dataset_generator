import os
import time
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# --- リトライ機能のために追加 ---
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# ------------------------------

load_dotenv()


class JStageClient:
    """
    J-STAGEからの論文ダウンロードを管理するクライアント。
    自動リトライ機能（エクスポネンシャル・バックオフ）を実装。
    """

    def __init__(self):
        self.request_interval = float(os.getenv("JSTAGE_REQUEST_INTERVAL", 1.5))
        self.headers = {
            "User-Agent": "DatasetGenerator/1.0 (https://github.com/YouSayH/kcr_Rehab-Plan-Generator; mailto:your-email@example.com)"
        }
        self.base_url = "https://api.jstage.jst.go.jp/searchapi/do"
        self.last_request_time = 0

        # --- ★ BAN対策：リトライ戦略の定義 ---
        retry_strategy = Retry(
            total=3,  # 合計リトライ回数
            status_forcelist=[429, 500, 502, 503, 504],  # リトライするHTTPステータスコード
            backoff_factor=1,  # バックオフ係数 (待機時間 = {backoff_factor} * (2 ** ({リトライ回数} - 1)))
            # 1回目: 0s, 2回目: 2s, 3回目: 4s
            allowed_methods=["HEAD", "GET", "OPTIONS"],  # リトライを許可するメソッド
        )

        # --- ★ BAN対策：セッションの構築 ---
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()  # requests.get() の代わりにセッションオブジェクトを使う

        # httpとhttpsの両方にアダプタとヘッダーを適用
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update(self.headers)  # デフォルトヘッダーをセッションに設定

    def _wait_for_interval(self):
        """
        前回のアクセスから指定した間隔が経過するまで待機する。
        """
        elapsed_time = time.time() - self.last_request_time
        wait_time = self.request_interval - elapsed_time
        if wait_time > 0:
            print(f"    -> (待機: {wait_time:.2f}秒)")
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def download_article_content(self, url: str) -> tuple[bytes | None, str | None]:
        """
        指定されたURLから論文のコンテンツをダウンロードする。
        """
        self._wait_for_interval()
        try:
            print(f"[JStageClient] URLからコンテンツをダウンロード中: {url}")
            # ★ requests.get() -> self.session.get() に変更
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()

            if "application/pdf" in content_type or response.headers.get("Content-Disposition", "").endswith(".pdf"):
                return response.content, "application/pdf"
            elif "text/html" in content_type:
                return response.content, "text/html"
            else:
                if response.content.strip().startswith(b"%PDF"):
                    return response.content, "application/pdf"
                else:
                    return response.content, "text/html"
        except requests.exceptions.RequestException as e:
            print(f"[JStageClient] ダウンロード中にエラーが発生しました: {e}")
            return None, None

    def search_articles(self, keyword: str, count: int = 10) -> list:
        """
        J-STAGEの論文検索APIを叩き、論文メタデータのリストを返す。
        """
        self._wait_for_interval()

        params = {"service": "3", "keyword": keyword, "count": count}

        print(f"[JStageClient] APIで論文を検索中 (keyword): '{keyword}'")
        try:
            # ★ requests.get() -> self.session.get() に変更
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            root = ET.fromstring(response.content)

            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "prism": "http://www.w3.org/2005/Atom",  # 修正：prismのURIをマニュアル通りに
                "prism": "http://prismstandard.org/namespaces/basic/2.0/",
            }

            articles = []
            for entry in root.findall("atom:entry", ns):
                # 論文タイトル (日本語) の正しいパス
                title_elem = entry.find(".//atom:article_title/atom:ja", ns)
                if title_elem is None:
                    title_elem = entry.find(".//atom:article_title/atom:en", ns)
                if title_elem is None:
                    title_elem = entry.find("atom:title", ns)

                title = title_elem.text.strip() if title_elem is not None and title_elem.text else "N/A"

                doi_elem = entry.find("prism:doi", ns)
                doi = doi_elem.text if doi_elem is not None else None

                # PDFリンクを優先して検索
                link_url = None
                pdf_link_elem = entry.find('atom:link[@type="application/pdf"]', ns)
                if pdf_link_elem is not None:
                    link_url = pdf_link_elem.get("href")

                if link_url is None:
                    html_link_elem = entry.find('atom:link[@type="text/html"]', ns)
                    if html_link_elem is not None:
                        html_url = html_link_elem.get("href")
                        if html_url:
                            link_url = html_url.replace("/_article/", "/_pdf/").replace("-char/ja", "")

                if link_url is None:
                    fallback_link_elem = entry.find("atom:link", ns)
                    if fallback_link_elem is not None:
                        link_url = fallback_link_elem.get("href")

                if doi and link_url:
                    articles.append(
                        {
                            "title": title,
                            "doi": doi,
                            "url": link_url,
                        }
                    )

            print(f"  -> {len(articles)} 件の論文メタデータを取得しました。")
            return articles

        except requests.exceptions.RequestException as e:
            # リトライしても失敗した場合
            print(f"[JStageClient] 論文検索APIへのリクエスト中にエラーが発生しました（リトライ後）: {e}")
            return []
        except ET.ParseError as e:
            print(f"[JStageClient] 論文検索APIの応答XMLの解析に失敗しました: {e}")
            print(f"  -> 受信したテキスト: {response.text[:500]}")
            return []
