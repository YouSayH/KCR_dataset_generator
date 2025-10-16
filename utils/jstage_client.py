import os
import time
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import urllib.parse

load_dotenv()


class JStageClient:
    """
    J-STAGEからの論文ダウンロードを管理するクライアント。
    """

    def __init__(self):
        self.request_interval = float(os.getenv("JSTAGE_REQUEST_INTERVAL", 1.5))
        self.headers = {
            'User-Agent': 'DatasetGenerator/1.0 (https://github.com/YouSayH/kcr_Rehab-Plan-Generator; mailto:your-email@example.com)'
        }
        self.base_url = "https://api.jstage.jst.go.jp/searchapi/do"
        self.last_request_time = 0

    def _wait_for_interval(self):
        """
        前回のアクセスから指定した間隔が経過するまで待機する。
        """
        elapsed_time = time.time() - self.last_request_time
        wait_time = self.request_interval - elapsed_time
        if wait_time > 0:
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def download_article_content(self, url: str) -> tuple[bytes | None, str | None]:
        """
        指定されたURLから論文のコンテンツをダウンロードする。
        """
        self._wait_for_interval()
        try:
            print(f"[JStageClient] URLからコンテンツをダウンロード中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30, allow_redirects=True)
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
        J-STAGEの論文検索APIを叩き、論文メタデータのリストを返す。（最終修正版）
        """
        self._wait_for_interval()
        
        # ★★★ 修正点: URLを手動で構築 ★★★
        # 共有いただいた記事の通り、'text'パラメータを使い、キーワードをURLエンコードして結合します。
        encoded_keyword = urllib.parse.quote(f'"{keyword}"')
        request_url = f"{self.base_url}?service=3&text={encoded_keyword}&count={count}"
        
        print(f"[JStageClient] APIで論文を検索中: '{keyword}'")
        try:
            # params引数を使わず、構築したURLを直接渡します
            response = requests.get(request_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            root = ET.fromstring(response.content)
            
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'prism': 'http://prismstandard.org/namespaces/basic/2.0/'
            }

            articles = []
            for entry in root.findall('atom:entry', ns):
                title_elem = entry.find('atom:title', ns)
                title = title_elem.text if title_elem is not None else "N/A"
                
                doi_elem = entry.find('prism:doi', ns)
                doi = doi_elem.text if doi_elem is not None else None
                
                # 'text/html'タイプのリンクを取得
                link_elem = entry.find('atom:link[@type="text/html"]', ns)
                if link_elem is None:
                    # 見つからない場合はタイプ指定なしで探す
                    link_elem = entry.find('atom:link', ns)
                
                link_url = link_elem.get('href') if link_elem is not None else None

                if doi and link_url:
                    pdf_url = link_url.replace('/_article/', '/_pdf/').replace('-char/ja', '')
                    articles.append({
                        'title': title,
                        'doi': doi,
                        'url': pdf_url,
                    })
            
            print(f"  -> {len(articles)} 件の論文メタデータを取得しました。")
            return articles

        except requests.exceptions.RequestException as e:
            print(f"[JStageClient] 論文検索APIへのリクエスト中にエラーが発生しました: {e}")
            return []
        except ET.ParseError as e:
            print(f"[JStageClient] 論文検索APIの応答XMLの解析に失敗しました: {e}")
            print(f"  -> 受信したテキスト: {response.text[:500]}")
            return []