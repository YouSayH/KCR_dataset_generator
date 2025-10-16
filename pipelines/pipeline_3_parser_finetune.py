import os
import json
from google import genai
from schemas import PATIENT_INFO_EXTRACTION_GROUPS

# --- プロンプトテンプレート ---

# ステージ1: 架空の臨床サマリーを生成するためのプロンプト
SUMMARY_CREATION_PROMPT_TEMPLATE = """
あなたは、経験豊富な指導医です。
以下の【患者ペルソナ】と【関連論文の抜粋】の情報を統合し、この患者の架空の「カルテサマリー」を、臨床現場で使われる自然な文体で作成してください。
このサマリーは、情報抽出モデルの学習データとして使用されるため、ペルソナに含まれる多様な情報（年齢、性別、疾患名、ADL状況、社会的背景など）を文章の中に自然に盛り込むことが重要です。

【患者ペルソナ】
{persona_json}

【関連論文の抜粋】
{article_text}
"""

# ステージ2: サマリーから構造化データを抽出するためのプロンプト
JSON_EXTRACTION_PROMPT_TEMPLATE = """
あなたは、医療テキストから情報を正確に抽出する専門家です。
以下の【臨床サマリー】から、指定されたJSONスキーマに合致する情報をすべて抽出してください。
テキスト中に存在しない情報は `null` としてください。

【臨床サマリー】
{summary_text}
"""


def process_parser_finetune_data_generation(job_data: dict, gemini_api_key: str) -> dict:
    """
    パイプライン3の本体。架空の臨床サマリーと対応する構造化JSONのペアを生成する。
    """
    print(f"  [Pipeline 3] 情報抽出データ生成ジョブを開始: {job_data.get('job_id')}")
    client = genai.Client(api_key=gemini_api_key)

    # --- 1. 必要なファイルを読み込む ---
    source_markdown_path = os.path.join("output", "pipeline_1_rag_source", job_data["source_markdown"])
    persona_path = os.path.join("output", "pipeline_2_lora_finetune", "personas", job_data["source_persona"])

    with open(source_markdown_path, "r", encoding="utf-8") as f:
        article_text = f.read()

    with open(persona_path, "r", encoding="utf-8") as f:
        persona_data = json.load(f)

    # --- 2.【ステージ1】架空の臨床サマリーを生成 ---
    print("    -> ステージ1: 臨床サマリーを生成中...")
    summary_prompt = SUMMARY_CREATION_PROMPT_TEMPLATE.format(
        persona_json=json.dumps(persona_data, ensure_ascii=False, indent=2),
        article_text=article_text[:4000],  # 論文の一部をコンテキストとして使用
    )
    response_summary = client.models.generate_content(model="gemini-2.5-flash", contents=summary_prompt)
    clinical_summary_text = response_summary.text
    print("    -> ステージ1: 完了")

    # --- 3.【ステージ2】構造化JSONを抽出（スキーマグループごとに逐次処理） ---
    print("    -> ステージ2: 構造化JSONを抽出中...")
    full_extracted_data = {}

    for sub_schema in PATIENT_INFO_EXTRACTION_GROUPS:
        print(f"      - スキーマ '{sub_schema.__name__}' の情報を抽出...")
        extraction_prompt = JSON_EXTRACTION_PROMPT_TEMPLATE.format(summary_text=clinical_summary_text)

        try:
            response_extraction = client.models.generate_content(
                model="gemini-2.5-flash",  # 抽出は高精度なモデルを推奨
                contents=extraction_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": sub_schema,
                },
            )
            if hasattr(response_extraction, "parsed") and response_extraction.parsed:
                # `exclude_none=True` で `null` の値を除外してマージ
                full_extracted_data.update(response_extraction.parsed.model_dump(exclude_none=True))
        except Exception as e:
            print(f"      - スキーマ '{sub_schema.__name__}' の抽出中にエラー: {e}")
            continue  # エラーが起きても次のスキーマに進む
    print("    -> ステージ2: 完了")

    if not full_extracted_data:
        raise ValueError("どのスキーマからも情報を抽出できませんでした。")

    # --- 4. 最終的な学習データ形式に整形 ---
    # ここではOpenAIの fine-tuningでよく使われる `messages` 形式を採用
    final_record = {
        "messages": [
            {"role": "user", "content": clinical_summary_text},
            {"role": "assistant", "content": json.dumps(full_extracted_data, ensure_ascii=False)},
        ]
    }

    return {"content": json.dumps(final_record, ensure_ascii=False), "extension": ".jsonl"}
