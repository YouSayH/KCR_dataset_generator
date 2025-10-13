from bs4 import BeautifulSoup


def extract_text_from_html(content: bytes) -> str:
    """
    HTMLコンテンツからテキストを抽出する。

    Args:
        content (bytes): ダウンロードしたHTMLファイルの中身。

    Returns:
        抽出されたプレーンテキスト。
    """
    try:
        soup = BeautifulSoup(content, "html.parser")

        # スクリプト、スタイルシート、ヘッダー、フッターなどの不要な要素を削除
        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.decompose()

        body = soup.find("body")
        if body:
            # strip=Trueで前後の余分な空白を削除し、separatorで改行を適切に挿入
            return body.get_text(separator="\n", strip=True)
        return ""
    except Exception as e:
        print(f"[TextExtractor] HTMLの解析中にエラーが発生しました: {e}")
        return ""
