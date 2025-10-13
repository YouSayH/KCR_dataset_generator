import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


class JStageClient:
    """
    J-STAGEからの論文ダウンロードを管理するクライアント。
    """

    def __init__(self):
        self.request_interval = float(os.getenv("JSTAGE_REQUEST_INTERVAL", 1.5))
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
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

    # J-STAGE APIを使った論文検索機能（ハブPC側で将来的に使用）
    def search_articles(self, keyword: str, count: int = 10) -> list:
        # TODO: 仕様書に基づき、J-STAGEの論文検索APIを叩く処理を実装
        print(f"[JStageClient] '{keyword}' で論文を検索する機能は未実装です。")
        return []
