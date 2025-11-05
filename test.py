# test_pdf_read.py
import os
import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types

def run_test():
    """
    pipeline_1_rag_source.py と同じ方法でPDFをAPIに渡し、
    正しくOCR（文字認識）できるかを確認するテスト
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("エラー: .env ファイルに GEMINI_API_KEY が設定されていません。")
        return

    client = genai.Client(api_key=api_key)

    # 問題のPDF (2001.28.2_281_1.pdf) のJ-STAGE上のPDF直リンク
    # jstage_client.py のロジック (/_article/ -> /_pdf/) を適用したURL
    # pdf_url = "https://www.jstage.jst.go.jp/article/cjpt/2001.28.2/0/2001.28.2_281_1/_pdf/"
    pdf_url = "https://www.jstage.jst.go.jp/article/jsmekanto/2017.23/0/2017.23_1917/_pdf/-char/ja"


    print(f"テスト対象PDFをダウンロード中:\n{pdf_url}\n")
    
    try:
        # jstage_client.py と同様にPDFのバイトデータを取得
        pdf_data = httpx.get(pdf_url, follow_redirects=True, timeout=30).content
    except Exception as e:
        print(f"PDFのダウンロードに失敗しました: {e}")
        return

    # ★最重要：創造性を排除した「文字起こし」を指示するプロンプト
    prompt = """

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

    print("Gemini API (gemini-2.5-flash-lite) にPDFを送信し、文字起こしを依頼します...")
    print("--------------------------------------------------")

    try:
        # pipeline_1_rag_source.py と全く同じ方法でAPIを呼び出し
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", # pipeline_1 と同じモデル
            contents=[
                types.Part.from_bytes(
                    data=pdf_data,
                    mime_type='application/pdf',
                ),
                prompt
            ],
            config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=24576)),
        )
        
        print("【Gemini APIからの応答（文字起こし結果）】:")
        print(response.text)
        print("--------------------------------------------------")

        # --- 検証 ---
        expected_text = "【目的】人工膝関節置換術"
        if expected_text in response.text:
            print("\n【検証結果】: 成功 ✅")
            print("APIはPDFのOCRと2段組の解析に成功しました。")
        else:
            print("\n【検証結果】: 失敗 ❌")
            print(f"APIは「{expected_text}」というテキストを読み取れませんでした。")
            print("これが、AIが本文を捏造（ハルシネーション）する根本原因である可能性が極めて高いです。")

    except Exception as e:
        print(f"\nAPI呼び出し中にエラーが発生しました: {e}")

if __name__ == "__main__":
    run_test()