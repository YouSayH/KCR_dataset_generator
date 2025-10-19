import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from google import genai


# 1. Pydanticによるペルソナのスキーマ定義
class PatientPersona(BaseModel):
    """リハビリテーション計画のシミュレーションに使用する架空の患者ペルソナ"""

    age_group: str = Field(description="年代（例：70代）")
    gender: str = Field(description="性別（男性または女性）")
    primary_disease: str = Field(description="中心となる疾患名や状態（例：変形性膝関節症, 大腿骨頸部骨折術後）")
    comorbidities: List[str] = Field(description="合併症のリスト（例：['高血圧', '2型糖尿病']）")
    background_history: str = Field(description="職業、家族構成、住環境、趣味、受傷・発症経緯などの背景や生活史。")
    subjective_complaints: str = Field(description="患者本人や家族の主な訴え、希望、目標。")
    psychosocial_factors: str = Field(
        description="リハビリテーションの進行に影響を与えうる心理的・社会的因子（例：転倒への恐怖心が強い, 家族の協力が得られにくい, 独居で不安がある）。"
    )


# 2. Geminiに投げるためのメタプロンプト
PERSONA_GENERATION_PROMPT_TEMPLATE = """
あなたは経験豊富な臨床家であり、脚本家でもあります。
以下の【条件】に合致する、臨床的にあり得るリアルな架空の患者プロフィールを創作してください。
あなたの創作するプロフィールは、新人セラピストが高品質なリハビリテーション実施計画書を作成するための教材として使用されます。
そのため、単なる事実の羅列ではなく、背景や感情が垣間見えるような、人間味のある記述を心がけてください。

【条件】
- **基本属性**: {age_group}, {gender}
- **主要疾患**: {paper_theme}

【関連論文の内容】
{paper_content}

【生成するプロファイルの要件】
- **多様性のため、臨床的にあり得る合併症を1つか2つ程度あってもいい。合併症がなくてもいい。必須ではありません。**
- **毎回異なる職業、家族構成、趣味を持つように心がけてください。**そのうえで、具体的な生活史や、その人らしさが伝わる背景（仕事、趣味など）を記述すること。
- **心理社会的因子も、不安、意欲、家族関係、社会的孤立など、様々な側面から記述してください。**
- 患者が抱える具体的な悩みや、リハビリテーションを通じて達成したい希望を明確に記述すること。
- 治療の妨げ、または促進になりうる心理・社会的因子を必ず1つ以上含めること。

出力は、指定されたJSONスキーマに厳密に従ってください。
"""

def generate_persona(paper_theme: str, age_group: str, gender: str, paper_content: str, gemini_api_key: str) -> PatientPersona:
    """
    論文テーマと基本属性から、Geminiを使って患者ペルソナを生成する。
    """
    # 正しい作法でのクライアント初期化
    client = genai.Client(api_key=gemini_api_key)

    prompt = PERSONA_GENERATION_PROMPT_TEMPLATE.format(
            paper_theme=paper_theme,
            age_group=age_group,
            gender=gender,
            paper_content=paper_content # 論文内容を渡す
        )

    print("\n～～～ ペルソナ生成リクエスト ～～～")
    print(f"テーマ: {paper_theme}, 属性: {age_group} {gender}")
    print(f"関連論文(冒頭):\n{paper_content[:200]}...") # ログにも一部表示
    print("～～～～～～～～～～～～～～～～～～")

    # 正しい作法でのAPIコール
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": PatientPersona,
            "temperature":1.5
        },
    )

    # `response.parsed` にパース済みのPydanticオブジェクトが入る
    if not hasattr(response, "parsed") or not response.parsed:
        raise ValueError("APIからパース可能な応答がありませんでした。")

    return response.parsed


# 3. このファイル単体で動作確認するためのテストコード
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("`config.ini`ファイルに環境変数 `GEMINI_API_KEY` が設定されていません。")

    try:
        # テストケース1
        print("【テストケース1】")
        persona_1 = generate_persona(
            paper_theme="大腿骨頸部骨折 術後", age_group="10代前半", gender="女性", gemini_api_key=api_key
        )
        print("\n～～～ 生成されたペルソナ ～～～")
        print(persona_1.model_dump_json(indent=2, ensure_ascii=False))

        # テストケース2
        print("\n\n【テストケース2】")
        persona_2 = generate_persona(paper_theme="脳卒中片麻痺", age_group="60代", gender="男性", gemini_api_key=api_key)
        print("\n～～～ 生成されたペルソナ ～～～")
        print(persona_2.model_dump_json(indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
