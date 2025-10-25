import os
import json
from google import genai

# from pydantic import create_model # 動的スキーマは不要
from schemas import RehabPlanSchema  # 計画書全体のスキーマをインポート
# from schemas import SEQUENTIAL_GENERATION_ORDER # 逐次生成は不要

# プロンプトテンプレート
LORA_GENERATION_PROMPT_TEMPLATE = """
あなたは、LoRAファインチューニング用の高品質な教師データを作成する専門家です。
以下の【入力データ】（患者ペルソナと関連論文）を基に、**リハビリテーション実施計画書の全項目**を生成してください。
出力は、指定されたJSONスキーマに厳密に従ってください。

【入力データ】
{input_json}

【指示】
上記の入力データを基に、臨床的に妥当で、一貫性のあるリハビリテーション実施計画書（`RehabPlanSchema`）を完成させよ。
ペルソナの背景や希望、論文の知見を最大限に反映すること。
"""


def process_full_plan_generation(job_data: dict, gemini_api_key: str) -> dict:
    """
    【新版】リハビリ計画書（全項目）を一括生成する関数
    """
    print(f"  [Pipeline 2] LoRAデータ生成ジョブ(一括)を開始: {job_data.get('job_id')}")
    client = genai.Client(api_key=gemini_api_key)

    # 1. 必要なファイルを読み込む
    source_markdown_path = os.path.join("output", "pipeline_1_rag_source", job_data["source_markdown"])
    persona_path = os.path.join("output", "pipeline_2_lora_finetune", "personas", job_data["source_persona"])

    try:
        with open(source_markdown_path, "r", encoding="utf-8") as f:
            article_text = f.read()
        with open(persona_path, "r", encoding="utf-8") as f:
            persona_data = json.load(f)
    except FileNotFoundError as e:
        print(f"    -> エラー: 必要なファイルが見つかりません。 {e}")
        raise
    except Exception as e:
        print(f"    -> エラー: ファイル読み込み中にエラー。 {e}")
        raise

    # 2. 安全な入力JSONの構築
    # P2 (LoRA) の入力は「ペルソナ」と「論文」
    input_data = {
        "patient_persona": persona_data,
        "relevant_article_text": article_text[:10000],  # RAGコンテキストとして論文を渡す（トークン数考慮）
    }
    input_json_string = json.dumps(input_data, ensure_ascii=False, indent=2)

    prompt = LORA_GENERATION_PROMPT_TEMPLATE.format(
        input_json=input_json_string,
    )

    print("    -> スキーマ 'RehabPlanSchema' に基づき全項目を一括生成します。")

    parsed_response = None  # パース結果を格納する変数を初期化

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",  # 全項目生成は高機能モデル推奨
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": RehabPlanSchema,  # ★計画書全体のスキーマを指定
            },
        )

        # 応答のパース処理（手動クリーンアップ試行を含む）
        if hasattr(response, "parsed") and response.parsed:
            parsed_response = response.parsed

        elif hasattr(response, "text") and response.text:
            print("    -> API応答の自動パースに失敗。手動でのJSONクリーンアップを試みます...")
            try:
                clean_text = response.text.strip().lstrip("```json").rstrip("```").strip()
                json_data = json.loads(clean_text)
                parsed_response = RehabPlanSchema(**json_data)  # Pydanticモデルに流し込む
                print("    -> 手動クリーンアップ成功。")

            except Exception as parse_e:
                print(f"    -> 手動クリーンアップ失敗: {parse_e}")
                debug_info = {
                    "message": "APIからのパース可能な応答がありませんでした (手動パースも失敗)。",
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "N/A",
                    "response_text": response.text,
                    "manual_parse_error": str(parse_e),
                }
                raise ValueError(json.dumps(debug_info, ensure_ascii=False))

        if parsed_response is None:
            debug_info = {
                "message": "APIからパース可能な応答がありませんでした (応答テキストも空またはパース不能)。",
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "N/A",
                "prompt_feedback": str(response.prompt_feedback),
                "response_text": response.text if hasattr(response, "text") else "N/A",
            }
            raise ValueError(json.dumps(debug_info, ensure_ascii=False))

    except Exception as e:
        print(f"    -> Gemini API呼び出し中にエラーが発生しました。詳細: {e}")
        raise e

    # 3. Alpaca形式のJSONLを作成
    # P2の instruction は「計画書を作れ」
    alpaca_record = {
        "instruction": "患者ペルソナと関連論文に基づき、包括的なリハビリテーション実施計画書を生成せよ。",
        "input": input_data,  # 入力は「ペルソナ」と「論文」
        "output": parsed_response.model_dump(),  # 出力は「計画書（全項目）」
    }

    # 4. ハブ（run_dataset_generation）に結果を返す
    return {
        "content": json.dumps(alpaca_record, ensure_ascii=False),
        "extension": ".jsonl",
        # "next_step_data" は不要になった
    }
