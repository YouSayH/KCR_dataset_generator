import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date  # date型を扱うためにインポート
from google import genai
import json  # エラー表示用にインポート


# --- 1. Pydanticによるペルソナのスキーマ定義 ---
# ご提示いただいたJSON構造に基づき、Pydanticモデルを定義します。


class FimScores(BaseModel):
    """ADL評価 FIMの各項目（文字列で点数を格納）"""

    Eating: Optional[str] = Field(None, description="食事 (FIM点数 例: 7点)")
    Grooming: Optional[str] = Field(None, description="整容 (FIM点数 例: 7点)")
    Bathing: Optional[str] = Field(None, description="入浴 (FIM点数 例: 5点)")
    Dressing_Upper: Optional[str] = Field(None, description="更衣(上半身) (FIM点数 例: 7点)", alias="Dressing Upper")
    Dressing_Lower: Optional[str] = Field(None, description="更衣(下半身) (FIM点数 例: 5点)", alias="Dressing Lower")
    Toileting: Optional[str] = Field(None, description="トイレ動作 (FIM点数 例: 6点)")
    Bladder_Management: Optional[str] = Field(None, description="排尿管理 (FIM点数 例: 7点)", alias="Bladder Management")
    Bowel_Management: Optional[str] = Field(None, description="排便管理 (FIM点数 例: 7点)", alias="Bowel Management")
    Transfer_Bed_Chair_Wc: Optional[str] = Field(
        None, description="移乗(ベッド・椅子・車椅子) (FIM点数 例: 6点)", alias="Transfer Bed Chair Wc"
    )
    Transfer_Toilet: Optional[str] = Field(None, description="移乗(トイレ) (FIM点数 例: 6点)", alias="Transfer Toilet")
    Transfer_Tub_Shower: Optional[str] = Field(
        None, description="移乗(浴槽・シャワー) (FIM点数 例: 4点)", alias="Transfer Tub Shower"
    )
    Locomotion_Walk_Walkingaids_Wc: Optional[str] = Field(
        None, description="移動(歩行/車椅子) (FIM点数 例: 3点)", alias="Locomotion Walk Walkingaids Wc"
    )
    Locomotion_Stairs: Optional[str] = Field(None, description="階段 (FIM点数 例: 1点)", alias="Locomotion Stairs")
    Comprehension: Optional[str] = Field(None, description="理解 (FIM点数 例: 7点)")
    Expression: Optional[str] = Field(None, description="表出 (FIM点数 例: 7点)")
    Social_Interaction: Optional[str] = Field(None, description="社会的交流 (FIM点数 例: 7点)", alias="Social Interaction")
    Problem_Solving: Optional[str] = Field(None, description="問題解決 (FIM点数 例: 7点)", alias="Problem Solving")
    Memory: Optional[str] = Field(None, description="記憶 (FIM点数 例: 7点)")


class BasicInfo(BaseModel):
    """患者の基本情報"""

    年齢: Optional[str] = Field(None, description="年代 (例: 10代後半, 70代)")
    性別: Optional[str] = Field(None, description="性別 (男または女)")
    算定病名: Optional[str] = Field(None, description="中心となる疾患名や術式 (例: 右膝前十字靭帯(ACL)損傷術後)")
    発症日_手術日: Optional[date] = Field(None, description="発症日または手術日 (YYYY-MM-DD)", alias="発症日・手術日")
    リハ開始日: Optional[date] = Field(None, description="リハビリテーション開始日 (YYYY-MM-DD)")


class FunctionStructure(BaseModel):
    """心身機能・構造に関する特記事項"""

    疼痛: Optional[str] = Field(None, description="疼痛の状態 (例: 右膝の術後痛、NRS4。)")
    関節可動域制限: Optional[str] = Field(None, description="関節可動域制限の状態 (例: 右膝の曲げ伸ばしが制限。)")
    筋力低下: Optional[str] = Field(None, description="筋力低下の状態 (例: 右大腿四頭筋の筋力低下。)")
    栄養障害: Optional[str] = Field(None, description="栄養に関する特記事項 (例: 鉄欠乏性貧血の既往。)")


class AdlEvaluation(BaseModel):
    """ADL評価 (FIM)"""

    FIM現在値: FimScores = Field(
        ..., description="FIMの現在値（FIMはFunctional Independence Measureの略）", alias="FIM(現在値)"
    )


class NutritionStatus(BaseModel):
    """栄養状態の客観的データ"""

    身長cm: Optional[float] = Field(None, description="身長(cm)", alias="身長(cm)")
    体重kg: Optional[float] = Field(None, description="体重(kg)", alias="体重(kg)")
    BMI: Optional[float] = Field(None, description="BMI値")


class SocialService(BaseModel):
    """社会保障サービスの利用状況"""

    要介護: Optional[str] = Field("なし", description="介護保険の状況 (例: なし, 要支援2, 要介護3)")


class LifeGoal(BaseModel):
    """患者の生活状況や目標"""

    趣味: Optional[str] = Field(
        None, description="患者の背景となる趣味や、本人の主な希望・目標 (例: 大学のサッカー部活動への完全復帰。)"
    )


class PatientPersona(BaseModel):
    """
    【新定義】リハビリテーション計画のシミュレーションに使用する、詳細な架空の患者ペルソナ。
    このデータは、P2(LoRA)では入力として、P3(Parser)では出力として使用される。
    """

    基本情報: BasicInfo
    心身機能_構造: FunctionStructure = Field(..., alias="心身機能・構造")
    ADL評価: AdlEvaluation
    栄養状態: NutritionStatus
    社会保障サービス: SocialService
    生活状況_目標_本人_家族: LifeGoal = Field(..., alias="生活状況・目標(本人・家族)")
    担当者からの所見: Optional[str] = Field("特になし")


# 2. Geminiに投げるためのメタプロンプト
PERSONA_GENERATION_PROMPT_TEMPLATE = """
あなたは経験豊富な臨床家であり、脚本家でもあります。
以下の【関連論文の内容】を読み、その内容に**最もふさわしい、臨床的にあり得るリアルな架空の患者プロフィール**を**1人分**創作してください。

このプロフィールは、リハビリテーション実施計画書（P2 LoRA）の**入力(Input)**データ、およびカルテ抽出（P3 Parser）の**出力(Output)**データとして使用されます。
そのため、必ず指定されたJSONスキーマに厳密に従い、**全ての項目を埋めてください**。

【関連論文のテーマ】
{paper_theme}

【関連論文の内容】
{paper_content}

【生成するプロファイルの要件】
- **臨床的整合性**: 論文のテーマ（疾患、術式、患者集団）と完全に一致する「算定病名」「年齢」「性別」を設定してください。
- **客観的データの創作**: 論文の内容とペルソナの背景に基づき、臨床的に妥当な「発症日・手術日」「リハ開始日」「FIM点数」「身長」「体重」などの客観的データを**創作**してください。
- **背景の具体化**: 「生活状況・目標(本人・家族)」の「趣味」欄には、その人らしさが伝わる背景（職業、家族構成、趣味）と、本人の具体的な希望・目標を**文章で**記述してください。
- **一貫性**: 「心身機能・構造」の記述（疼痛、ROM制限、筋力低下など）は、「ADL評価」のFIM点数と論理的に一貫している必要があります。（例：筋力低下やROM制限があれば、移乗や歩行の点数は低くなるはずです）

- **考慮すべき詳細**: ペルソナを作成する際は、以下のような詳細情報も念頭に置いてください（ただし、これらすべてを出力スキーマに含める必要はありません）：
  - **具体的な機能障害**: 麻痺の有無、感覚障害、高次脳機能障害（注意障害など）
  - **ADLの詳細**: 各動作の開始時と現在のスコア、使用している福祉用具
  - **社会資源**: 申請中の介護保険区分、利用中のサービス
  - **生活環境**: 自宅の改修状況、同居家族の介護力

出力は、指定されたJSONスキーマ（`PatientPersona`）に厳密に従ってください。
"""


def generate_persona(paper_theme: str, paper_content: str, gemini_api_key: str) -> PatientPersona:
    """
    論文テーマと内容から、Geminiを使って【詳細な】患者ペルソナを1つ生成する。
    """

    client = genai.Client(api_key=gemini_api_key)

    prompt = PERSONA_GENERATION_PROMPT_TEMPLATE.format(
        paper_theme=paper_theme,
        paper_content=paper_content,  # 論文内容を渡す
    )

    print("\n～～～ ペルソナ生成リクエスト（詳細版） ～～～")
    print(f"テーマ: {paper_theme}")
    print(f"関連論文(冒頭):\n{paper_content[:300]}...")
    print("～～～～～～～～～～～～～～～～～～")

    response = client.models.generate_content(
        model="gemini-2.5-flash",  # このタスクは複雑なため、Proモデルを強く推奨
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": PatientPersona,  # ★新しい詳細スキーマを指定
            "temperature": 1.0,  # 創造性と安定性のバランス
        },
    )

    if not hasattr(response, "parsed") or not response.parsed:
        # パース失敗時のデバッグ情報
        debug_info = {
            "message": "APIからパース可能な応答がありませんでした。",
            "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "N/A",
            "prompt_feedback": str(response.prompt_feedback),
            "response_text": response.text if hasattr(response, "text") else "N/A",
        }
        raise ValueError(f"ペルソナ生成に失敗しました: {json.dumps(debug_info, ensure_ascii=False)}")

    return response.parsed


# 3. このファイル単体で動作確認するためのテストコード
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 `GEMINI_API_KEY` が設定されていません。")

    # テスト用のダミー論文内容
    dummy_paper_content_1 = """
    若年アスリートの前十字靭帯（ACL）損傷は、スポーツ活動への復帰を目的としたリハビリテーションが不可欠である。
    多くの場合、自家腱（膝蓋腱または半腱様筋腱）を用いた再建術が行われる。
    術後のリハビリテーションは、可動域の回復、大腿四頭筋の筋力強化、および固有受容感覚の再教育が中心となる。
    スポーツ特有の動作（カッティング、ジャンプ）の訓練は、術後6ヶ月以降に段階的に導入される。
    心理的因子（再受傷への恐怖）が復帰の妨げとなることも報告されている。
    """

    try:
        # テストケース1
        print("【テストケース1】")
        persona_1 = generate_persona(
            paper_theme="前十字靭帯(ACL)損傷 術後", paper_content=dummy_paper_content_1, gemini_api_key=api_key
        )
        print("\n～～～ 生成されたペルソナ（詳細版） ～～～")
        # by_alias=True で Pydantic の alias を JSON キーとして使用
        print(persona_1.model_dump_json(indent=2, ensure_ascii=False, by_alias=True))

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
