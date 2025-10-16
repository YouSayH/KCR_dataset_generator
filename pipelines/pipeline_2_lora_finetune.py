import os
import json
from google import genai
from pydantic import create_model # Pydanticモデルを動的に作成するためにインポート
from schemas import SEQUENTIAL_GENERATION_ORDER # 新しい設計図をインポート

# プロンプトテンプレート
LORA_GENERATION_PROMPT_TEMPLATE = """
あなたは、LoRAファインチューニング用の高品質な教師データを作成する専門家です。
以下の【入力データ】を基に、【指示】に従って【出力データ】を生成してください。
出力は、指定されたJSONスキーマに厳密に従ってください。

【入力データ】
{input_json}

【指示】
上記の入力データを基に、リハビリテーション実施計画書の「{target_field_name}」の項目のみを生成せよ。
これまでの項目（previously_generated_items）との論理的な一貫性を保ち、臨床的に妥当な内容を記述すること。
"""

def process_lora_data_generation(job_data: dict, gemini_api_key: str) -> dict:
    """
    【新版】単一項目特化型 LoRAデータペア生成関数
    """
    print(f"  [Pipeline 2] LoRAデータ生成ジョブ(単一項目)を開始: {job_data.get('job_id')}")
    client = genai.Client(api_key=gemini_api_key)

    # 1. ジョブデータと設計図から、今回のタスクを特定
    target_step = job_data.get('target_step', 0)
    
    # 設計図から、今回生成するフィールド名と、その定義が含まれるクラスを取得
    target_field_name, source_schema_class = SEQUENTIAL_GENERATION_ORDER[target_step]
    
    print(f"    -> ステップ {target_step}: '{target_field_name}' を生成します。")

    # 2. 動的にPydanticスキーマを作成
    # source_schema_classから、対象フィールドの定義(説明文など)を取得
    field_definition = source_schema_class.model_fields[target_field_name]
    
    # 対象のフィールド名と型定義だけを持つ、新しいPydanticモデルをその場で作成
    # これがGeminiに渡す response_schema となる
    DynamicSchema = create_model(
        f'DynamicSchema_{target_field_name}',
        **{target_field_name: (field_definition.annotation, field_definition)}
    )

    # 3. 必要なファイルを読み込む
    source_markdown_path = os.path.join("output", "pipeline_1_rag_source", job_data['source_markdown'])
    persona_path = os.path.join("output", "pipeline_2_lora_finetune", "personas", job_data['source_persona'])
    
    with open(source_markdown_path, 'r', encoding='utf-8') as f:
        article_text = f.read()
    with open(persona_path, 'r', encoding='utf-8') as f:
        persona_data = json.load(f)

    # 4. 安全な入力JSONの構築
    input_data = {
        "patient_persona": persona_data,
        "relevant_article_text": article_text[:6000],
        "previously_generated_items": job_data.get('previous_results', {})
    }
    input_json_string = json.dumps(input_data, ensure_ascii=False, indent=2)

    prompt = LORA_GENERATION_PROMPT_TEMPLATE.format(
        input_json=input_json_string,
        target_field_name=target_field_name,
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={"response_mime_type": "application/json", "response_schema": DynamicSchema}
        )

        # 正常な応答でも、パースに失敗するケースを詳細に調査する
        if not hasattr(response, 'parsed') or not response.parsed:
            # パース失敗の真の原因を特定するためのデバッグ情報を構築
            debug_info = {
                "message": f"APIから '{target_field_name}' のパース可能な応答がありませんでした。",
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "N/A",
                "prompt_feedback": str(response.prompt_feedback),
                "response_text": response.text if hasattr(response, 'text') else "N/A"
            }
            # エラー情報全体を文字列として例外を発生させる
            raise ValueError(json.dumps(debug_info, ensure_ascii=False))

    except Exception as e:
        # Gemini APIからの直接のエラーも、詳細情報と共に再raiseする
        print(f"    -> Gemini API呼び出し中にエラーが発生しました。詳細: {e}")
        raise e
    
    # 6. Alpaca形式のJSONLを作成
    alpaca_record = {
        "instruction": f"リハビリテーション実施計画書の「{target_field_name}」の項目を、先行する項目を踏まえて生成せよ。",
        "input": input_data,
        "output": response.parsed.model_dump() # model_dump()は {"field_name": "generated_text"} を返す
    }

    # 7. ハブに次のステップの情報を返す
    return {
        "content": json.dumps(alpaca_record, ensure_ascii=False),
        "extension": ".jsonl",
        "next_step_data": {
            "generated_items": response.parsed.model_dump(),
            "next_step": target_step + 1
        }
    }