import os
from google import genai
from google.genai import types  # Part.from_bytes を使用するために必須
from utils.jstage_client import JStageClient
from utils.text_extractor import extract_text_from_html

# 定数定義

# MARKDOWN_GENERATION_PROMPT = """
# あなたは、学術論文をRAGシステムで利用するのに最適な、構造化Markdownに変換するエキスパートです。
# 以下の【最優先ルール】と【出力の3大原則】、【具体的ルール】を絶対的な最優先事項として、提供された論文をMarkdown形式で出力してください。

# 【最優先ルール：捏造（ハルシネーション）の厳格な禁止】
# 1.  **テキストを創作しない:** 元の論文に含まれていない文章、数値、考察、セクション（「はじめに」「方法」など）を**絶対に創作しないでください**。
# 2.  **「〇〇」や「X人」のようなプレースホルダーの禁止:** AIが「〇〇」や「X人」のような意味のないプレースホルダーを**創作することは、最も重大なエラー**です。もしPDF/テキストの読み取りに失敗し、具体的な数値や内容が不明な場合は、**その部分を要約・創作しようとせず、読み取れたテキストをそのまま出力するか、そのセクションごとスキップしてください**。
# 3.  **忠実性:** 元の論文の文章をできる限りそのまま保持してください。特に数値、%（パーセンテージ）、統計結果などを省略したり、置き換えたりしないでください。

# ---
# 【出力の3大原則】 (最優先ルールに従うこと)
# 1.  **構造がすべてを決定する (Structure is King):** 機械が処理しやすいよう、一貫した構造を維持します。
# 2.  **特殊コンテンツには「名札」を付ける (Tag Your Special Content):** Mermaid、表、数式などは、それ自体が何であるかを示す見出しを付けます。
# 3.  **チャンクは自己完結させる (Chunks Must Be Self-Contained):** 各セクションは、それ一つで意味が通じるように記述します。（ただし、**元の論文の文章を無理に書き換えてはいけません**。「上記の理由により」といった記述は、文脈が失われてもそのまま出力してください。）

# ---
# 【具体的ルール】 (最優先ルールに従うこと)
# - **ルール1：見出しレベルの階層を絶対に崩さない**
#   - **(重要) 論文タイトルは出力しない:** 論文全体のタイトル（H1見出し）は、ファイルの先頭にあるYAMLフロントマターで管理するため、本文中には含めないでください。**元のテキストから読み取れた**「## 要旨」や「## はじめに」（または「【目的】」など）から始めてください。
#   - `##` (H2) は章や大きなセクション（例: `はじめに`, `TKA術後のリハビリテーションの概要`）に使用します。
#   - `###` (H3) は節や具体的な項目（例: `膝関節の可動域制限`, `股関節周囲筋の機能低下`）に使用します。
#   - `####` (H4) は図、表、Mermaid、数式などの特殊コンテンツの「名札」として**のみ**使用します。

# - **ルール2：特殊コンテンツは「専用の見出し」の下に配置する**
#   - **(重要) 図(Image):** PDF内の画像は直接Markdownに埋め込めません。代わりに、**元のテキストにキャプション（例: 「図1：〇〇」）や説明文が記述されている場合のみ**、`#### 図1：[図のキャプション]`という見出しの下に、**その説明文を忠実に転記**してください。`![...](...)`構文は絶対に使用しないでください。
#   - **表(Table):** **元のテキストに表のキャプションや説明、要約が記述されている場合のみ**、`#### 表1：比較データ` のような見出しを付け、そのテキストを転記してください。**AIが表を読み取ってMarkdownテーブルを創作したり、独自の要約を創作したりしないでください。**
#   - **フローチャート(Mermaid):** ルール2と同様に、テキストとして記述されている場合のみ転記してください。
#   - **数式:** 数式はインラインなら`$E=mc^2$`、ブロックなら`$$...$$`のようにLaTeX形式で記述してください。

# - **ルール3：本文の品質**
#   - 論文の要旨（Abstract, 要旨, 目的, 方法, 結果, まとめ等）は、**元のテキストに存在する見出し**（例: `## 要旨` や `## 目的`）の下に配置してください。
#   - 最後の参考文献リストは完全に削除してください。

# ---
# 【理想的な出力例 (Few-Shot Example)】
# （元のプロンプトの例は、AIが「創作」すべきだと誤解する可能性があるため、より「忠実な抽出」の例を示します）

# ## 目的
# 人工膝関節置換術(以下TKA) 術後に、手術側膝周辺の熱感は非常に多く観察される臨床症状である。これは、感染、生体の異物反応、手術侵襲による炎症症状や循環障害などが考えられるものの、運動によってさらに増強することも考えられる。しかし、これまでに運動と熱感の関係について詳細に研究した報告は認めない。そこで、今回、TKA患者の熱感が、運動によって増強するかどうかを確認するための予備的実験を行った。

# ## 方法
# 68歳女性、左TKA術後(術後27日) 1例において検討を行った。CRP値は正常範囲。運動は、持続的他動運動(CPM:範囲0~120度,速度120度/分,実施時間1時間)とした。皮膚温測定には、サーモトレーサー (NEC三栄製 TH5100)を用いた。なお、環境温度の影響を避けるため、エアコンを備えた部屋を利用し、温度設定を25℃とした。測定手順は、10分以上の安静臥位を取った後、手術側及び非手術側下肢外側面の皮膚温を測定した。そして、CPM終了直後、及び終了10分後に同様の測定を行った。得られた画像データーから露出した下肢の輪郭に沿って領域設定し、温度ヒストグラムを作成した。

# #### 図：手術側下肢の温度ヒストグラム
# （注：元のPDF にはキャプションが「手術側下肢の温度ヒストグラム」としか書かれていないため、AIはそれ以上説明を創作しないこと）

# ## 結果
# 手術側において、CPM施行前の膝周辺部皮膚温は非手術側に比し高値を示した(最高温度:手術側38.9℃/非手術側37.5℃)。CPM終了時において手術側皮膚温の上昇を認めた(最高温度38.9℃→39.7℃)。CPM終了10分後では終了直後よりも手術側皮膚温の下降が見られたが、CPM施行前よりは高かった(最高温度39.7℃ 39.4℃)。非手術側下肢は、CPM施行前,終了直後,終了10分後の各時点において最高皮膚温及び平均皮膚温に著明な変化は認めなかった。

# ## まとめ
# このことは、感染、生体の異物反応、炎症反応、循環障害などに加え、運動そのものも熱感の上昇に関与する可能性が示唆された。そのため、感染などの鑑別も含め、患部の直視下および用手接触での観察のもと、適切に理学療法を実施する必要があるといえよう。

# ---
# 【不適切な出力例（捏造の例）】
# ## 結果
# ### 熱感の発生頻度
# CPM施行後の熱感は、〇〇%の患者に認められた。
# #### 表1：術式と熱感の有無
# | 術式 | 熱感あり | 熱感なし |
# | :--- | :--- | :--- |
# | 全置換術 | X人 | Y人 |
# **要約:** この表は...
# （↑ これらは元の論文 に存在しない情報をAIが創作したため、**重大なエラー**です。）
# ---

# 以上のルールに従い、提供された論文を解析し、**捏造せず、忠実にかつ構造化された**Markdownを生成してください。
# """



# 要約をいれることでOCRがうまくいっていないので、一旦要約中止
MARKDOWN_GENERATION_PROMPT = """

あなたは、学術論文をRAGシステムで利用するのに最適な、構造化Markdownに変換するエキスパートです。
以下の【出力の3大原則】と【具体的ルール】を絶対的な最優先事項として、提供された論文をMarkdown形式で出力してください。

【ルール：捏造（ハルシネーション）の厳格な禁止】
1.  **テキストを創作しない:** 元の論文に含まれていない文章、数値、考察、セクション（例：「要旨」や「まとめ」など）を**絶対に創作しないでください**。
2.  **忠実性:** 元の論文の文章をできる限りそのまま保持してください。AIによる要約や言い換えは行わず、読み取れたテキストをそのまま転記してください。
3.  **構造の厳守:** 元の論文の見出し構造（例: 「1. 緒言」「2. 方法」）を、Markdownの見出し（`## 緒言`, `## 方法`）として忠実に再現してください。

【出力の3大原則】
1.  **構造がすべてを決定する (Structure is King):** 機械が処理しやすいよう、一貫した構造を維持します。
2.  **特殊コンテンツには「名札」を付ける (Tag Your Special Content):** Mermaid、表、数式などは、それ自体が何であるかを示す見出しを付けます。
3.  **チャンクは自己完結させる (Chunks Must Be Self-Contained):** 各セクションは、それ一つで意味が通じるように記述します。

---
【具体的ルール】
- **ルール1：見出しレベルの階層を絶対に崩さない**
  - **(重要) 論文タイトルは出力しない:** 論文全体のタイトル（H1見出し）は、ファイルの先頭にあるYAMLフロントマターで管理するため、本文中には含めないでください。最初の見出しは `## 要旨` や `## はじめに` から始めてください。
  - **(重要) 最初の見出し:** 元の論文から読み取れた**最初のセクション見出し**（例: `## 緒言`, `## はじめに`, `## 目的`）から出力を開始してください。
  - `##` (H2) は章や大きなセクション（例: `はじめに`, `TKA術後のリハビリテーションの概要`）に使用します。
  - `###` (H3) は節や具体的な項目（例: `膝関節の可動域制限`, `股関節周囲筋の機能低下`）に使用します。
  - `####` (H4) は図、表、Mermaid、数式などの特殊コンテンツの「名札」として**のみ**使用します。

- **ルール2：特殊コンテンツは「専用の見出し」の下に配置する**
  - **(重要) 図(Image):** PDF内の画像は直接Markdownに埋め込めません。代わりに、`#### 図1：[図のキャプション]`という見出しの下に、**画像の内容を詳細に説明する文章**を記述してください。`![...](...)`という構文は**絶対に使用しないでください。**
  - **図(Image)の補足:** 論文上で図の説明がある場合、論文の説明を入れる。画像自体の内容を詳細に説明する文章も追加してください。
  - **表(Table):** `#### 表1：比較データ` のような見出しを付け、その下にMarkdownテーブルを配置し、**続けて表の要約**も記述してください（例: `**要約:** この表は...`）。
  - **フローチャート(Mermaid):** `#### フローチャート：治療の流れ` のような見出しを付け、その下にMermaidコードブロックを配置し、**続けてフローチャートの解説**も記述してください（例: `**解説:** このフローチャートは...`）。
  - **数式:** 数式はインラインなら`$E=mc^2$`、ブロックなら`$$...$$`のようにLaTeX形式で記述してください。必要であれば `#### 数式1：〇〇の計算式` のような見出しを付け、解説を加えてください。

- **ルール3：本文の品質**
  - 段落の整形: PDFの2段組レイアウトや行末で自動的に挿入された、**段落途中の不自然な改行**は**絶対に**そのまま出力せず、必ず適切に連結し、自然な文章の段落として整形してください。（例：「...医師の技量を必\n要とし...」は「...医師の技量を必要とし...」とします）。
  - ただし、**意図的な段落の区切り**（元のテキストでの空行など）は、Markdownの段落（空行を挟む）として正しく維持してください。
  - 各セクション（特に`###`以下）は、それだけで意味が通じるように記述してください。「上記の理由により」のような、前のセクションに依存する表現は避けてください。
  - 論文の要旨（Abstract, 要旨）は、`## 要旨`の見出しの下に配置してください。
  - 最後の参考文献リストは完全に削除してください。


---
【理想的な出力例 (Few-Shot Example)】(セクション名の要旨や介入方などは論文のセクションに置き換えてください。)

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
    jstage_client = JStageClient()

    # url = job_data.get("url")
    pdf_url_to_try = job_data.get("url")
    # if not url:
    if not pdf_url_to_try:
        raise ValueError("ジョブデータにURLが含まれていません。")
    
    metadata = job_data.get("metadata", {})
    html_url_fallback = metadata.get("debug_original_url")

    # content, content_type = jstage_client.download_article_content(url)
    content, content_type = jstage_client.download_article_content(pdf_url_to_try)

    # --- DEBUGGING START ---
    # ユーザーのデバッグリクエストに対応
    content_length_for_debug = len(content) if content else 0
    print(f"    [DEBUG] ダウンロード試行。タイプ: {content_type}, サイズ: {content_length_for_debug} bytes")

    is_pdf_success = content and content_type and "pdf" in content_type

    if not is_pdf_success:
        print(f"    [DEBUG] 1回目のPDFダウンロード失敗（またはPDFでない）。HTML URLにフォールバックします。")
        print(f"    [DEBUG]   -> フォールバックURL: {html_url_fallback}")
        
        if not html_url_fallback or html_url_fallback == pdf_url_to_try:
            # フォールバック先がない、または同じURL（=元からPDFリンクだった）場合
            raise ConnectionError(f"PDFダウンロードに失敗。フォールバック先のHTML URLもありません。URL: {pdf_url_to_try}")

        # HTML URLで再試行
        content, content_type = jstage_client.download_article_content(html_url_fallback)
        content_length_for_debug = len(content) if content else 0
        print(f"    [DEBUG] ダウンロード試行 (2回目: HTML URL)。タイプ: {content_type}, サイズ: {content_length_for_debug} bytes")

        if not content or not content_type or "html" not in content_type:
            # 2回目も失敗
            raise ConnectionError(f"PDFとHTMLの両方のダウンロードに失敗しました。PDF: {pdf_url_to_try}, HTML: {html_url_fallback}")

        # ★重要★ HTMLフォールバックが成功した場合、source_urlもHTMLのものに差し替える
        job_data["url"] = html_url_fallback


    # if "pdf" in (content_type or ""):
    #     print(f"    [DEBUG] -> PDFとして処理します。")
    # elif "html" in (content_type or ""):
    #     print(f"    [DEBUG] -> HTMLとして処理します。")
    # else:
    #     print(f"    [DEBUG] -> 不明なコンテントタイプ、またはダウンロード失敗。")
    # --- DEBUGGING END ---

    # if not content or not content_type:
    #     raise ConnectionError(f"URLからのコンテンツダウンロードに失敗しました: {url}")

    # model_name = "gemini-2.5-flash-lite"
    model_name = "gemini-2.5-flash"


    if "pdf" in content_type:
        # PDF処理フロー (インラインデータ)
        print("  [Pipeline 1] PDFを検出。インラインデータとして送信します...")

        # ファイルのバイトデータとプロンプトをリストにまとめる
        contents = [types.Part.from_bytes(data=content, mime_type="application/pdf"), MARKDOWN_GENERATION_PROMPT]

        response = client.models.generate_content(model=model_name, contents=contents,config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=24576)),)
        markdown_body = response.text

    elif "html" in content_type:
        # HTML処理フロー
        print("  [Pipeline 1] HTMLを検出。テキストを抽出して送信します...")
        extracted_text = extract_text_from_html(content)
        if not extracted_text:
            raise ValueError("HTMLからのテキスト抽出に失敗しました。")
        print(f"  -> テキスト抽出完了 (約{len(extracted_text)}文字)")

        prompt = MARKDOWN_GENERATION_PROMPT_FOR_TEXT.format(article_text=extracted_text)
        response = client.models.generate_content(model=model_name, contents=prompt,config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=24576)),)
        markdown_body = response.text

    else:
        raise TypeError(f"サポートされていないコンテントタイプです: {content_type} (URL: {job_data.get('url')})")

    if not markdown_body:
        raise RuntimeError("Gemini APIから空の応答がありました。Markdownを生成できませんでした。")

    # YAML Frontmatterを作成
    metadata = job_data.get("metadata", {})
    # html_url_fallback = metadata.get("debug_original_url")
    
    frontmatter = f"""---
title: "{metadata.get("title", "N/A").replace('"', "'")}"
doi: "{metadata.get("doi", "N/A")}"
journal: "{metadata.get("journal", "N/A")}"
published_date: "{metadata.get("published_date", "N/A")}"
source_url: "{job_data.get('url')}"
---
"""

    # 最終的なMarkdownコンテンツを結合
    final_markdown = f"{frontmatter}\n{markdown_body}"

    return {"content": final_markdown, "extension": ".md"}
