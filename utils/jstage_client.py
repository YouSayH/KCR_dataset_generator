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
        self.search_api_url = "https://api.jstage.jst.go.jp/search/article/"
        self.last_request_time = 0

    def _wait_for_interval(self):
        """
        前回のアクセスから指定した間隔が経過するまで待機する。
        """
        elapsed_time = time.time() - self.last_request_time
        wait_time = self.request_interval - elapsed_time
        if wait_time > 0:
            # print(f"[JStageClient] サーバー負荷軽減のため {wait_time:.2f} 秒待機します...")
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def download_article_content(self, url: str) -> tuple[bytes | None, str | None]:
        """
        指定されたURLから論文のコンテンツをダウンロードする。

        Args:
            url (str): 論文ページのURL。

        Returns:
            タプル: (ダウンロードしたコンテンツ(bytes), コンテンツタイプ(str))。
            失敗した場合は (None, None) を返す。
        """
        self._wait_for_interval()
        try:
            print(f"[JStageClient] URLからコンテンツをダウンロード中: {url}")
            response = requests.get(url, headers=self.headers, timeout=30, allow_redirects=True)
            response.raise_for_status()  # 200番台以外のステータスコードで例外を発生させる

            content_type = response.headers.get("Content-Type", "").lower()

            # PDFがContent-Dispositionヘッダで示唆される場合もある
            if "application/pdf" in content_type or response.headers.get("Content-Disposition", "").endswith(".pdf"):
                return response.content, "application/pdf"
            elif "text/html" in content_type:
                return response.content, "text/html"
            else:
                # 不明なタイプの場合、中身を少し見て判断する（簡易版）
                if response.content.strip().startswith(b"%PDF"):
                    return response.content, "application/pdf"
                else:
                    # デフォルトはHTMLとして扱う
                    return response.content, "text/html"

        except requests.exceptions.RequestException as e:
            print(f"[JStageClient] ダウンロード中にエラーが発生しました: {e}")
            return None, None

    def search_articles(self, keyword: str, count: int = 10) -> list:
        """
        J-STAGEの論文検索APIを叩き、論文メタデータのリストを返す。
        """
        self._wait_for_interval()
        params = {
            'searchword': keyword,
            'count': count,
            'service': 3 # 論文のみを対象
        }
        
        print(f"[JStageClient] APIで論文を検索中: '{keyword}'")
        try:
            response = requests.get(self.search_api_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()

            # XMLを解析
            root = ET.fromstring(response.content)
            articles = []
            
            # 名前空間を定義（J-STAGE APIの仕様）
            ns = {
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'prism': 'http://prismstandard.org/namespaces/basic/2.0/',
                'dc': 'http://purl.org/dc/elements/1.1/'
            }
            
            for item in root.findall('.//rdf:Description', ns):
                title = item.find('dc:title', ns).text if item.find('dc:title', ns) is not None else "N/A"
                doi = item.find('prism:doi', ns).text if item.find('prism:doi', ns) is not None else None
                html_url = item.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
                
                # J-STAGEの慣例に従い、HTML URLからPDF URLを推測する
                pdf_url = html_url.replace('/_article/', '/_pdf/').replace('-char/ja', '') if html_url else None
                
                process_url = pdf_url if pdf_url else html_url

                if doi and process_url:
                    articles.append({
                        'title': title, 'doi': doi, 'url': process_url,
                    })
            
            print(f"  -> {len(articles)} 件の論文メタデータを取得しました。")
            return articles

        except requests.exceptions.RequestException as e:
            print(f"[JStageClient] 論文検索APIへのリクエスト中にエラーが発生しました: {e}")
            return []
        except ET.ParseError as e:
            print(f"[JStageClient] 論文検索APIの応答XMLの解析に失敗しました: {e}")
            return []