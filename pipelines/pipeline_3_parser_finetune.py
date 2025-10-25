import os
import json
from datetime import date
from google import genai

# from schemas import PATIENT_INFO_EXTRACTION_GROUPS # 古いP3スキーマ
from utils.persona_generator import PatientPersona  # P3の「出力」としてペルソナのスキーマをインポート


def json_serial(obj):
    """JSON a-serializable objects handler."""
    if isinstance(obj, date):
        return obj.isoformat()  # dateオブジェクトを "YYYY-MM-DD" 形式の文字列に変換
    raise TypeError("Type %s not serializable" % type(obj))


# --- プロンプトテンプレート ---

# ステージ1: 「架空のリハビリ資料（カルテメモなど）」を生成するためのプロンプト
REHAB_MATERIALS_CREATION_PROMPT_TEMPLATE = """
あなたは、経験豊富な指導医（バイザー）です。
以下の【患者ペルソナ】の情報を基に、この患者を担当する**複数のセラピスト（例：PT、OT、ST）**が書いたであろう**「架空のリハビリテーション関連資料（日々のリハビリメモ、カルテ、経過記録など）」**を創作してください。

この資料は、**「非構造化テキストから構造化された患者ペルソナを抽出するAI」**を学習させるための入力データとなります。
そのため、以下の【要件】を**必ず**満たしてください。

【患者ペルソナ】
{persona_json}

【関連論文のコンテキスト】
（参考情報として、このペルソナの元となった論文の抜粋を添付します）
{article_text}

【要件】
1.  **多様な文体**: セラピストによって書き方が違う状況を再現してください（例：箇条書き中心、単語の殴り書き、"である調"の詳細な記述、"ですます調"のポエム、SOAP形式など）。
2.  **情報の分散**: ペルソナの全情報を1箇所にまとめず、意図的に文章全体に分散させてください（例：年齢はAさんのメモに、家族構成はBさんのメモに書かれている）。
3.  **ノイズの含有**: リハビリの直接の経過（例：「本日T-caneにて50m歩行。vitals安定」）など、ペルソナ情報とは**直接関係のない**情報も自然に含めてください。
4.  **リアリティ**: 専門用語（例：MMT, ROM, ADL）を適切に使用し、臨床現場のリアリティを追求してください。
5.  **情報の網羅性**: ペルソナに含まれる重要な情報（年齢、性別、疾患名、合併症、背景、希望、心理因子など）が、資料全体を読めば**必ず**推測できるようにしてください。
"""


def process_parser_finetune_data_generation(job_data: dict, gemini_api_key: str) -> dict:
    """
    パイプライン3の本体。
    【新版】「架空のリハビリ資料（入力）」と「ペルソナJSON（出力）」のペアを生成する。
    """
    print(f"  [Pipeline 3] 情報抽出データ生成ジョブ（資料→ペルソナ）を開始: {job_data.get('job_id')}")
    client = genai.Client(api_key=gemini_api_key)

    # --- 1. 必要なファイルを読み込む ---
    source_markdown_path = os.path.join("output", "pipeline_1_rag_source", job_data["source_markdown"])
    persona_path = os.path.join("output", "pipeline_2_lora_finetune", "personas", job_data["source_persona"])

    try:
        with open(source_markdown_path, "r", encoding="utf-8") as f:
            article_text = f.read()
        with open(persona_path, "r", encoding="utf-8") as f:
            persona_data = json.load(f)  # P3では、このペルソナが「正解データ」になる
    except FileNotFoundError as e:
        print(f"    -> エラー: 必要なファイルが見つかりません。 {e}")
        raise
    except Exception as e:
        print(f"    -> エラー: ファイル読み込み中にエラー。 {e}")
        raise

    # --- 2.【ステージ1】架空のリハビリ資料（非構造化テキスト）を生成 ---
    print("    -> ステージ1: 架空のリハビリ資料（カルテメモ等）を生成中...")
    summary_prompt = REHAB_MATERIALS_CREATION_PROMPT_TEMPLATE.format(
        persona_json=json.dumps(persona_data, ensure_ascii=False, indent=2),
        article_text=article_text[:4000],  # 論文の一部をコンテキストとして使用
    )

    # この生成タスクは創造性が高いため、Proモデルと高めのtemperatureを推奨
    response_summary = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=summary_prompt, config={"temperature": 0.8}
    )

    fictitious_rehab_materials_text = response_summary.text
    print("    -> ステージ1: 完了")

    # --- 3.【ステージ2】は不要（JSON抽出は行わない） ---

    # --- 4. 最終的な学習データ形式に整形 (QAを反転) ---
    # P3の instruction は「資料からペルソナを抽出せよ」
    # （※ファインチューニング時にこの形式が使われることを想定）
    final_record = {
        "messages": [
            {
                "role": "system",
                "content": f"あなたは、非構造化テキスト（カルテやリハビリメモ）から患者のペルソナ情報を抽出し、指定されたJSONスキーマ（{PatientPersona.__name__}）で出力するエキスパートです。",
            },
            {
                "role": "user",
                "content": fictitious_rehab_materials_text,  # 入力 = 架空の資料
            },
            {
                "role": "assistant",
                "content": json.dumps(persona_data, ensure_ascii=False, default=json_serial),  # 出力 = ペルソナJSON
            },
        ]
    }

    return {"content": json.dumps(final_record, ensure_ascii=False, default=json_serial), "extension": ".jsonl"}
