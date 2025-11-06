import os
import time
import re
# import requests
import httpx
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# --- リトライ機能のために追加 ---
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# ------------------------------

load_dotenv()


class JStageClient:
    """
    J-STAGEからの論文ダウンロードを管理するクライアント。
    自動リトライ機能（エクスポネンシャル・バックオフ）を実装。
    """

    def __init__(self):
        self.request_interval = float(os.getenv("JSTAGE_REQUEST_INTERVAL", 10))
        self.headers = {
            "User-Agent": "DatasetGenerator/1.0 (https://github.com/YouSayH/kcr_Rehab-Plan-Generator; mailto:your-email@example.com)"
        }
        self.base_url = "https://api.jstage.jst.go.jp/searchapi/do"
        self.last_request_time = 0

        # # BAN対策：リトライ戦略の定義
        # retry_strategy = Retry(
        #     total=3,  # 合計リトライ回数
        #     status_forcelist=[429, 500, 502, 503, 504],  # リトライするHTTPステータスコード
        #     backoff_factor=1,  # バックオフ係数 (待機時間 = {backoff_factor} * (2 ** ({リトライ回数} - 1)))
        #     allowed_methods=["HEAD", "GET", "OPTIONS"],  # リトライを許可するメソッド
        # )

        # # BAN対策：セッションの構築
        # adapter = HTTPAdapter(max_retries=retry_strategy)
        # self.session = requests.Session()
        # self.session.mount("https://", adapter)
        # self.session.mount("http://", adapter)
        # self.session.headers.update(self.headers)

        # httpx のリトライ設定
        retries = 3
        
        # BAN対策：セッションの構築 (httpx版)
        self.client = httpx.Client(
            headers=self.headers,
            follow_redirects=True, # リダイレクトを許可 (重要)
            timeout=30.0,
            transport=httpx.HTTPTransport(retries=retries) # シンプルなリトライ設定
        )

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
            # response = self.session.get(url, timeout=30, allow_redirects=True)
            response = self.client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()

            if "application/pdf" in content_type or response.headers.get("Content-Disposition", "").endswith(".pdf"):
                return response.content, "application/pdf"
            elif "text/html" in content_type:
                return response.content, "text/html"
            else:
                # PDFかHTMLか不明な場合、内容で判断する簡易チェック
                if response.content.strip().startswith(b"%PDF"):
                    return response.content, "application/pdf"
                else:
                    return response.content, "text/html" # デフォルトはHTML扱い
        # except requests.exceptions.RequestException as e:
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"[JStageClient] ダウンロード中にエラーが発生しました: {e}")
            return None, None

    def search_articles(self, keyword: str, count: int = 1000, start: int = 1) -> tuple[list, int]:
        """
        J-STAGEの論文検索APIを叩き、論文メタデータのリストと総ヒット件数を返す。
        (雑誌名・発行年/日を含むように修正)
        """
        self._wait_for_interval()
        params = {"service": "3", "keyword": keyword, "count": count, "start": start}
        print(f"[JStageClient] APIで論文を検索中 (keyword): '{keyword}', (start): {start}, (count): {count}")

        try:
            # response = self.session.get(self.base_url, params=params, timeout=30)
            response = self.client.get(self.base_url, params=params)
            response.raise_for_status()
            # response.encoding = response.apparent_encoding
            root = ET.fromstring(response.text)

            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "prism": "http://prismstandard.org/namespaces/basic/2.0/",
                "opensearch": "http://a9.com/-/spec/opensearch/1.1/"
            }

            total_results_elem = root.find("opensearch:totalResults", ns)
            total_results = int(total_results_elem.text) if total_results_elem is not None else 0

            articles = []
            for entry in root.findall("atom:entry", ns):
                # 既存の抽出 (タイトル)
                title_elem_ja = entry.find(".//atom:article_title/atom:ja", ns)
                title_elem_en = entry.find(".//atom:article_title/atom:en", ns)
                title_elem_atom = entry.find("atom:title", ns) # フォールバック
                title = "N/A"
                # 日本語タイトルがあれば優先、なければ英語、それもなければatom:title
                if title_elem_ja is not None and title_elem_ja.text:
                    title = title_elem_ja.text.strip()
                elif title_elem_en is not None and title_elem_en.text:
                    title = title_elem_en.text.strip()
                elif title_elem_atom is not None and title_elem_atom.text:
                    title = title_elem_atom.text.strip()

                # 既存の抽出 (DOI)
                doi_elem = entry.find("prism:doi", ns)
                doi = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else None

                # 既存の抽出 (URL)
                link_url = None
                # PDFリンクを最優先
                pdf_link_elem = entry.find('atom:link[@type="application/pdf"]', ns)
                if pdf_link_elem is not None:
                    link_url = pdf_link_elem.get("href")

                # PDFがなければHTMLリンクを探し、PDF URLへの変換を試みる
                # if link_url is None:
                #     html_link_elem = entry.find('atom:link[@type="text/html"]', ns)
                #     if html_link_elem is not None:
                #         html_url = html_link_elem.get("href")
                #         # PDF URLへの変換ロジック (成功するとは限らない)
                #         if html_url and "/_article/" in html_url:
                #             # link_url = html_url.replace("/_article/", "/_pdf/").replace("-char/ja", "")
                #             link_url = html_url.replace("/_article/", "/_pdf/")
                #         else:
                #              link_url = html_url # 変換できなければHTML URLをそのまま使う
                if link_url is None:
                    html_link_elem = entry.find('atom:link[@type="text/html"]', ns)
                    if html_link_elem is not None:
                        link_url = html_link_elem.get("href")


                # 上記で見つからなければ、最初のatom:linkをフォールバックとして使う
                if link_url is None:
                    fallback_link_elem = entry.find("atom:link", ns)
                    if fallback_link_elem is not None:
                        link_url = fallback_link_elem.get("href")

                original_link_url = link_url
                
                # if link_url and "/_article/" in link_url:
                #     link_url = link_url.replace("/_article/", "/_pdf/")

                if link_url and "/_article/" in link_url:
                    # 新ロジック: /_article/ と、それに続く余計な文字列（例: /-char/ja/）を
                    # まとめて /_pdf/ に置換する
                    link_url = re.sub(r'/_article/.*', '/_pdf/', link_url)


                # 追加情報の抽出 (テストスクリプトの結果を反映)
                # 1. 雑誌名/会議録名 (日本語 -> 英語 -> prism:publicationName の順で探す)
                journal_name = "N/A"
                journal_ja_elem = entry.find(".//atom:material_title/atom:ja", ns)
                journal_en_elem = entry.find(".//atom:material_title/atom:en", ns)
                prism_pub_name_elem = entry.find("prism:publicationName", ns) # フォールバック用

                if journal_ja_elem is not None and journal_ja_elem.text:
                    journal_name = journal_ja_elem.text.strip()
                elif journal_en_elem is not None and journal_en_elem.text:
                    journal_name = journal_en_elem.text.strip()
                elif prism_pub_name_elem is not None and prism_pub_name_elem.text:
                     journal_name = prism_pub_name_elem.text.strip()

                # 2. 発行年/日 (prism:publicationDate -> atom:pubyear の順で探す)
                published_date = "N/A"
                pub_date_elem = entry.find("prism:publicationDate", ns) # YYYY-MM-DD形式
                pub_year_elem = entry.find("atom:pubyear", ns) # YYYY形式

                if pub_date_elem is not None and pub_date_elem.text: # 日付形式があれば優先
                    published_date = pub_date_elem.text.strip()
                elif pub_year_elem is not None and pub_year_elem.text: # 年だけでも取得
                    published_date = pub_year_elem.text.strip()


                # DOI と URL が取得できた場合のみリストに追加
                if doi and link_url:
                    articles.append(
                        {
                            "title": title,
                            "doi": doi,
                            "url": link_url,
                            "journal": journal_name,
                            "published_date": published_date,
                            "debug_original_url": original_link_url,
                        }
                    )

            # ログ表示
            if start == 1:
                 print(f"  -> 総ヒット件数: {total_results} 件。")
            print(f"  -> {len(articles)} 件の論文メタデータを取得しました。")
            return articles, total_results

        # エラーハンドリング
        # except requests.exceptions.RequestException as e:
        except httpx.RequestError as e:
            print(f"[JStageClient] 論文検索APIへのリクエスト中にエラーが発生しました（リトライ後）: {e}")
            return [], 0
        except ET.ParseError as e:
            print(f"[JStageClient] 論文検索APIの応答XMLの解析に失敗しました: {e}")
            print(f"  -> 受信したテキスト: {response.text[:500]}") # デバッグ用に受信内容の一部を表示
            return [], 0
        except Exception as e: # 予期せぬエラー
             print(f"[JStageClient] 予期せぬエラーが発生しました: {e}")
             return [], 0