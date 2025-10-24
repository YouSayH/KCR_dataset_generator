import os
from google import genai
from google.genai import types  # Part.from_bytes を使用するために必須
from utils.jstage_client import JStageClient
from utils.text_extractor import extract_text_from_html

# 定数定義
MARKDOWN_GENERATION_PROMPT = """

あなたは、学術論文をRAGシステムで利用するのに最適な、構造化Markdownに変換するエキスパートです。
以下の【出力の3大原則】と【具体的ルール】を絶対的な最優先事項として、提供された論文をMarkdown形式で出力してください。

【出力の3大原則】
1.  **構造がすべてを決定する (Structure is King):** 機械が処理しやすいよう、一貫した構造を維持します。
2.  **特殊コンテンツには「名札」を付ける (Tag Your Special Content):** Mermaid、表、数式などは、それ自体が何であるかを示す見出しを付けます。
3.  **チャンクは自己完結させる (Chunks Must Be Self-Contained):** 各セクションは、それ一つで意味が通じるように記述します。

---
【具体的ルール】
- **ルール1：見出しレベルの階層を絶対に崩さない**
  - **(重要) 論文タイトルは出力しない:** 論文全体のタイトル（H1見出し）は、ファイルの先頭にあるYAMLフロントマターで管理するため、本文中には含めないでください。最初の見出しは `## 要旨` や `## はじめに` から始めてください。
  - `##` (H2) は章や大きなセクション（例: `はじめに`, `TKA術後のリハビリテーションの概要`）に使用します。
  - `###` (H3) は節や具体的な項目（例: `膝関節の可動域制限`, `股関節周囲筋の機能低下`）に使用します。
  - `####` (H4) は図、表、Mermaid、数式などの特殊コンテンツの「名札」として**のみ**使用します。

- **ルール2：特殊コンテンツは「専用の見出し」の下に配置する**
  - **(重要) 図(Image):** PDF内の画像は直接Markdownに埋め込めません。代わりに、`#### 図1：[図のキャプション]`という見出しの下に、**画像の内容を詳細に説明する文章**を記述してください。`![...](...)`という構文は**絶対に使用しないでください。**
  - **表(Table):** `#### 表1：比較データ` のような見出しを付け、その下にMarkdownテーブルを配置し、**続けて表の要約**も記述してください（例: `**要約:** この表は...`）。
  - **フローチャート(Mermaid):** `#### フローチャート：治療の流れ` のような見出しを付け、その下にMermaidコードブロックを配置し、**続けてフローチャートの解説**も記述してください（例: `**解説:** このフローチャートは...`）。
  - **数式:** 数式はインラインなら`$E=mc^2$`、ブロックなら`$$...$$`のようにLaTeX形式で記述してください。必要であれば `#### 数式1：〇〇の計算式` のような見出しを付け、解説を加えてください。

- **ルール3：本文の品質**
  - 各セクション（特に`###`以下）は、それだけで意味が通じるように記述してください。「上記の理由により」のような、前のセクションに依存する表現は避けてください。
  - 論文の要旨（Abstract, 要旨）は、`## 要旨`の見出しの下に配置してください。
  - 最後の参考文献リストは完全に削除してください。


---
【理想的な出力例 (Few-Shot Example)】

## 要旨
本研究では、変形性膝関節症（OA）患者に対する高強度運動療法と低強度運動療法の効果を比較検討した。結果として、高強度群において膝関節機能の有意な改善が認められた。

## 介入方法
対象者を2群に分け、以下の介入を行った。

### 高強度運動療法群
週3回、理学療法士の監督下で最大筋力の80%に相当する負荷でのレッグプレスを10回3セット実施した。

#### 表1：対象者の基本情報
| 項目 | 高強度群 | 低強度群 |
| :--- | :--- | :--- |
| 年齢(歳) | 71.5 ± 5.2 | 72.1 ± 4.8 |
| 性別(男/女) | 10/20 | 11/19 |

**要約:** この表は、研究に参加した高強度運動療法群と低強度運動療法群の被験者の基本的な属性（平均年齢と標準偏差、男女比）を示しています。両群間で年齢や性別構成に大きな差は見られません。

### 結果
介入後の膝関節機能の改善度を図1に示す。

#### 図1：介入前後の膝関節機能スコアの変化
この棒グラフは、介入前と介入後における高強度群と低強度群の膝関節機能スコア（JKOM）を示している。高強度群ではスコアが平均20点から45点へと大幅に改善しているが、低強度群では19点から22点への微増に留まっている。



---


以上のルールに従い、提供された論文を解析し、完璧な構造化Markdownを生成してください。
"""


MARKDOWN_GENERATION_PROMPT_FOR_TEXT = MARKDOWN_GENERATION_PROMPT + "\n【論文テキスト】\n{article_text}"


def process_pipeline_1(job_data: dict, gemini_api_key: str) -> dict:
    """
    パイプライン1のメイン処理。論文URLから構造化Markdownを生成する。
    (インラインデータ方式に修正)
    """
    client = genai.Client(api_key=gemini_api_key)

    url = job_data.get("url")
    if not url:
        raise ValueError("ジョブデータにURLが含まれていません。")

    jstage_client = JStageClient()
    content, content_type = jstage_client.download_article_content(url)
    if not content or not content_type:
        raise ConnectionError(f"URLからのコンテンツダウンロードに失敗しました: {url}")

    model_name = "gemini-2.5-flash-lite"

    if "pdf" in content_type:
        # PDF処理フロー (インラインデータ)
        print("  [Pipeline 1] PDFを検出。インラインデータとして送信します...")

        # ファイルのバイトデータとプロンプトをリストにまとめる
        contents = [types.Part.from_bytes(data=content, mime_type="application/pdf"), MARKDOWN_GENERATION_PROMPT]

        response = client.models.generate_content(model=model_name, contents=contents)
        markdown_body = response.text

    elif "html" in content_type:
        # HTML処理フロー
        print("  [Pipeline 1] HTMLを検出。テキストを抽出して送信します...")
        extracted_text = extract_text_from_html(content)
        if not extracted_text:
            raise ValueError("HTMLからのテキスト抽出に失敗しました。")
        print(f"  -> テキスト抽出完了 (約{len(extracted_text)}文字)")

        prompt = MARKDOWN_GENERATION_PROMPT_FOR_TEXT.format(article_text=extracted_text)
        response = client.models.generate_content(model=model_name, contents=prompt)
        markdown_body = response.text

    else:
        raise TypeError(f"サポートされていないコンテントタイプです: {content_type}")

    if not markdown_body:
        raise RuntimeError("Gemini APIから空の応答がありました。Markdownを生成できませんでした。")

    # YAML Frontmatterを作成
    metadata = job_data.get("metadata", {})
    frontmatter = f"""---
title: "{metadata.get("title", "N/A").replace('"', "'")}"
doi: "{metadata.get("doi", "N/A")}"
journal: "{metadata.get("journal", "N/A")}"
published_date: "{metadata.get("published_date", "N/A")}"
source_url: "{url}"
---
"""

    # 最終的なMarkdownコンテンツを結合
    final_markdown = f"{frontmatter}\n{markdown_body}"

    return {"content": final_markdown, "extension": ".md"}
