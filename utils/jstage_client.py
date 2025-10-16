# import os
# import time
# import requests
# import xml.etree.ElementTree as ET
# from dotenv import load_dotenv

# load_dotenv()


# class JStageClient:
#     """
#     J-STAGEからの論文ダウンロードを管理するクライアント。
#     """

#     def __init__(self):
#         self.request_interval = float(os.getenv("JSTAGE_REQUEST_INTERVAL", 2.0))
#         self.headers = {
#             'User-Agent': 'DatasetGenerator/1.0 (https://github.com/YouSayH/kcr_Rehab-Plan-Generator; mailto:your-email@example.com)'
#         }
#         self.search_api_url = "https://api.jstage.jst.go.jp/searchapi/do"
#         self.last_request_time = 0

#     def _wait_for_interval(self):
#         """
#         前回のアクセスから指定した間隔が経過するまで待機する。
#         """
#         elapsed_time = time.time() - self.last_request_time
#         wait_time = self.request_interval - elapsed_time
#         if wait_time > 0:
#             # print(f"[JStageClient] サーバー負荷軽減のため {wait_time:.2f} 秒待機します...")
#             time.sleep(wait_time)
#         self.last_request_time = time.time()

#     def download_article_content(self, url: str) -> tuple[bytes | None, str | None]:
#         """
#         指定されたURLから論文のコンテンツをダウンロードする。

#         Args:
#             url (str): 論文ページのURL。

#         Returns:
#             タプル: (ダウンロードしたコンテンツ(bytes), コンテンツタイプ(str))。
#             失敗した場合は (None, None) を返す。
#         """
#         self._wait_for_interval()
#         try:
#             print(f"[JStageClient] URLからコンテンツをダウンロード中: {url}")
#             response = requests.get(url, headers=self.headers, timeout=30, allow_redirects=True)
#             response.raise_for_status()  # 200番台以外のステータスコードで例外を発生させる

#             content_type = response.headers.get("Content-Type", "").lower()

#             # PDFがContent-Dispositionヘッダで示唆される場合もある
#             if "application/pdf" in content_type or response.headers.get("Content-Disposition", "").endswith(".pdf"):
#                 return response.content, "application/pdf"
#             elif "text/html" in content_type:
#                 return response.content, "text/html"
#             else:
#                 # 不明なタイプの場合、中身を少し見て判断する（簡易版）
#                 if response.content.strip().startswith(b"%PDF"):
#                     return response.content, "application/pdf"
#                 else:
#                     # デフォルトはHTMLとして扱う
#                     return response.content, "text/html"

#         except requests.exceptions.RequestException as e:
#             print(f"[JStageClient] ダウンロード中にエラーが発生しました: {e}")
#             return None, None

#     def search_articles(self, keyword: str, count: int = 10) -> list:
#         """
#         J-STAGEの論文検索APIを叩き、論文メタデータのリストを返す。
#         """
#         self._wait_for_interval()
#         params = {
#             'text': keyword,
#             'count': count,
#             'service': 3 # 論文のみを対象
#         }
        
#         print(f"[JStageClient] APIで論文を検索中: '{keyword}'")
#         try:
#             response = requests.get(self.search_api_url, params=params, headers=self.headers, timeout=30)
#             response.raise_for_status()
#             response.encoding = response.apparent_encoding # 文字化け対策

#             # --- XML解析部分を全面的に修正 ---
#             root = ET.fromstring(response.content)
            
#             # J-STAGE APIが返すXMLの名前空間を定義
#             ns = {
#                 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
#                 'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
#                 'dc': 'http://purl.org/dc/elements/1.1/',
#                 'rss': 'http://purl.org/rss/1.0/',
#             }

#             articles = []
#             # 'item' タグを名前空間付きで検索
#             for item in root.findall('.//rss:item', ns):
#                 title = item.find('dc:title', ns).text if item.find('dc:title', ns) is not None else "N/A"
#                 doi = item.find('prism:doi', ns).text if item.find('prism:doi', ns) is not None else None
#                 # URLは 'link' タグから取得するのが正しい
#                 link_url = item.find('rss:link', ns).text if item.find('rss:link', ns) is not None else None

#                 if doi and link_url:
#                     # PDFへの直接リンクを試みる
#                     pdf_url = link_url.replace('/_article/', '/_pdf/').replace('-char/ja', '')
#                     articles.append({
#                         'title': title,
#                         'doi': doi,
#                         'url': pdf_url, # PDFのURLを優先的に使用
#                     })
            
#             print(f"  -> {len(articles)} 件の論文メタデータを取得しました。")
#             return articles

#         except requests.exceptions.RequestException as e:
#             print(f"[JStageClient] 論文検索APIへのリクエスト中にエラーが発生しました: {e}")
#             return []
#         except ET.ParseError as e:
#             print(f"[JStageClient] 論文検索APIの応答XMLの解析に失敗しました: {e}")
#             print(f"  -> 受信したテキスト: {response.text[:500]}") # デバッグ用に受信内容を表示
#             return []


import os
import time
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()


class JStageClient:
    """
    J-STAGEからの論文ダウンロードを管理するクライアント。
    """

    def __init__(self):
        self.request_interval = float(os.getenv("JSTAGE_REQUEST_INTERVAL", 2.0))
        self.headers = {
            'User-Agent': 'DatasetGenerator/1.0 (https://github.com/YouSayH/kcr_Rehab-Plan-Generator; mailto:your-email@example.com)'
        }
        # エンドポイントはHTTPのままが確実です
        self.search_api_url = "http://api.jstage.jst.go.jp/searchapi/do"
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
        J-STAGEの論文検索APIを叩き、論文メタデータのリストを返す。
        """
        self._wait_for_interval()
        # パラメータは 'text' のままで問題ありません
        params = {
            'text': keyword,
            'count': count,
            'service': 3
        }
        
        print(f"[JStageClient] APIで論文を検索中: '{keyword}'")
        try:
            response = requests.get(self.search_api_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            response.encoding = response.apparent_encoding # 文字化け対策

            # --- XML解析部分を全面的に修正 ---
            root = ET.fromstring(response.content)
            
            # J-STAGE APIが返すXMLの名前空間を定義
            ns = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'rss': 'http://purl.org/rss/1.0/',
            }

            articles = []
            # 'item' タグを名前空間付きで検索
            for item in root.findall('.//rss:item', ns):
                title = item.find('dc:title', ns).text if item.find('dc:title', ns) is not None else "N/A"
                doi = item.find('prism:doi', ns).text if item.find('prism:doi', ns) is not None else None
                # URLは 'link' タグから取得するのが正しい
                link_url = item.find('rss:link', ns).text if item.find('rss:link', ns) is not None else None

                if doi and link_url:
                    # PDFへの直接リンクを試みる
                    pdf_url = link_url.replace('/_article/', '/_pdf/').replace('-char/ja', '')
                    articles.append({
                        'title': title,
                        'doi': doi,
                        'url': pdf_url, # PDFのURLを優先的に使用
                    })
            
            print(f"  -> {len(articles)} 件の論文メタデータを取得しました。")
            return articles

        except requests.exceptions.RequestException as e:
            print(f"[JStageClient] 論文検索APIへのリクエスト中にエラーが発生しました: {e}")
            return []
        except ET.ParseError as e:
            print(f"[JStageClient] 論文検索APIの応答XMLの解析に失敗しました: {e}")
            print(f"  -> 受信したテキスト: {response.text[:500]}") # デバッグ用に受信内容を表示
            return []