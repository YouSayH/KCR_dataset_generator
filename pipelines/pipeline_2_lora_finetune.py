import os
import json
from google import genai
from schemas import RehabPlanSchema, GENERATION_GROUPS  # 既存のschemas.pyを活用

# プロンプトテンプレート
LORA_GENERATION_PROMPT_TEMPLATE = """
あなたは、LoRAファインチューニング用の高品質な教師データを作成する専門家です。
以下の【入力データ】を基に、【指示】に従って【出力データ】を生成してください。
出力は、指定されたJSONスキーマに厳密に従ってください。

【入力データ】
{input_json}

【指示】
上記の入力データを基に、リハビリテーション実施計画書の一部である「{target_schema_name}」に関する項目を生成せよ。
臨床的に妥当で、一貫性のある内容を記述すること。
"""


def process_lora_data_generation(job_data: dict, gemini_api_key: str) -> dict:
    """
    パイプライン2の本体。論文とペルソナからLoRA用データペアを生成する。
    """
    print(f"  [Pipeline 2] LoRAデータ生成ジョブを開始: {job_data.get('job_id')}")

    # 1. 必要なファイルを読み込む
    source_markdown_path = os.path.join("output", "pipeline_1_rag_source", job_data["source_markdown"])
    persona_path = os.path.join("output", "pipeline_2_lora_finetune", "personas", job_data["source_persona"])

    with open(source_markdown_path, "r", encoding="utf-8") as f:
        article_text = f.read()  # TODO: 本来はRAGで関連箇所を抽出するが、まずは全文を使う

    with open(persona_path, "r", encoding="utf-8") as f:
        persona_data = json.load(f)

    target_step = job_data.get("target_step", 0)
    target_schema = GENERATION_GROUPS[target_step]
    target_schema_name = target_schema.__name__
    previous_items = job_data.get("previous_results", {})

    # 文字列フォーマットではなく、Pythonの辞書として入力データを構築
    input_data = {
        "patient_persona": persona_data,
        "relevant_article_text": article_text[:6000],  # コンテキスト長を少し増やす
        "previously_generated_items": previous_items,
    }
    # 辞書をJSON文字列に変換
    input_json_string = json.dumps(input_data, ensure_ascii=False, indent=2)

    prompt = LORA_GENERATION_PROMPT_TEMPLATE.format(
        input_json=input_json_string,
        target_schema_name=target_schema_name,
    )

    # 3. Gemini API呼び出し (構造化出力)
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # 高度な推論が要求されるため、Proモデルを推奨
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": target_schema,
        },
    )

    if not hasattr(response, "parsed") or not response.parsed:
        raise ValueError("APIからパース可能な応答がありませんでした。")

    # 4. Alpaca形式のJSONLを作成
    # `instruction`と`input`はプロンプトから再構成、`output`はAPIの生成結果
    alpaca_record = {
        "instruction": f"リハビリテーション実施計画書の一部である「{target_schema_name}」に関する項目を生成せよ。",
        "input": input_data,
        "output": response.parsed.model_dump(),
    }

    return {
        "content": json.dumps(alpaca_record, ensure_ascii=False),
        "extension": ".jsonl",
        # 次のステップのために、生成結果と次のステップ番号を返す
        "next_step_data": {"generated_items": response.parsed.model_dump(), "next_step": target_step + 1},
    }
