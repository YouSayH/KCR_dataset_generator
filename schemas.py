from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# Pydanticを使用して、AIに生成してほしいJSONの構造を定義します。
# Field(description=...) を使用して、各項目が何を意味するのかをAIに明確に伝えます。
class RehabPlanSchema(BaseModel):
    # 事実の要約
    # main_comorbidities_txt: str = Field(description="患者データから併存疾患・合併症を要約して記述")

    # 臨床推論に基づく生成
    main_risks_txt: str = Field(
        description="算定病名、併存疾患、ADL状況から考えられる安静度やリハビリテーション施行上のリスクを具体的に考察して簡潔に記述(50文字程度)"
    )
    main_contraindications_txt: str = Field(
        description="術式や疾患特有の禁忌や、リハビリを行う上での医学的な特記事項・注意点を考察して簡潔に記述(50文字程度)"
    )

    func_pain_txt: str = Field(
        description="患者データの'func_pain_chk'がTrueの場合、どの部位に、どのような動作で、どの程度の痛み(NRS等)が生じる可能性があるかを臨床的に推測して簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_rom_limitation_txt: str = Field(
        description="患者データの'func_rom_limitation_chk'がTrueの場合、その制限が具体的にどの日常生活動作(ADL)の妨げになっているかを考察して簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_muscle_weakness_txt: str = Field(
        description="患者データの'func_muscle_weakness_chk'がTrueの場合、その筋力低下が原因で困難となっている具体的な動作との関連性を考察して簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_swallowing_disorder_txt: str = Field(
        description="患者データの'func_swallowing_disorder_chk'がTrueの場合、栄養情報にある嚥下調整食コードなどを参考に、具体的な食事形態や注意点を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_behavioral_psychiatric_disorder_txt: str = Field(
        description="患者データの'func_behavioral_psychiatric_disorder_chk'がTrueの場合、リハビリ中の関わり方や環境設定での具体的な注意点を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )

    func_nutritional_disorder_txt: str = Field(
        description="患者データの'func_nutritional_disorder_chk'がTrueの場合、具体的な状態（例：低体重、特定の栄養素の欠乏）や食事摂取における課題を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_excretory_disorder_txt: str = Field(
        description="患者データの'func_excretory_disorder_chk'がTrueの場合、具体的な症状（例：尿失禁、便秘、カテーテル留置）を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_pressure_ulcer_txt: str = Field(
        description="患者データの'func_pressure_ulcer_chk'がTrueの場合、発生部位と重症度（DESIGN-Rなど）を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_contracture_deformity_txt: str = Field(
        description="患者データの'func_contracture_deformity_chk'がTrueの場合、具体的な部位とADLへの影響を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_motor_muscle_tone_abnormality_txt: str = Field(
        description="患者データの'func_motor_muscle_tone_abnormality_chk'がTrueの場合、具体的な状態（痙性、固縮、低緊張など）と部位を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_disorientation_txt: str = Field(
        description="患者データの'func_disorientation_chk'がTrueの場合、どの見当識（時間、場所、人物）に問題があるかを簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )
    func_memory_disorder_txt: str = Field(
        description="患者データの'func_memory_disorder_chk'がTrueの場合、具体的な症状（短期記憶の低下、エピソード記憶の欠落など）を簡潔に記述(20文字程度)。Falseまたはデータがない場合は必ず「特記なし」と記述してください。"
    )

    adl_equipment_and_assistance_details_txt: str = Field(
        description="FIM/BIの各項目点数から、ADL自立度向上のために適切と考えられる福祉用具の選定案や、具体的な介助方法を提案(200文字程度から400文字程度)"
    )

    goals_1_month_txt: str = Field(
        description="患者データ、特にADL状況や担当者所見から、1ヶ月で達成可能かつ具体的な短期目標（SMARTゴール）を設定(100文字から200文字程度)"
    )
    goals_at_discharge_txt: str = Field(
        description="患者の全体像を考慮し、退院時に達成を目指す現実的な長期目標を設定(100文字から150文字程度)"
    )

    policy_treatment_txt: str = Field(
        description="全ての情報を統合し、リハビリテーションの全体的な治療方針を専門的に記述(100文字から500文字程度)"
    )
    policy_content_txt: str = Field(
        description="治療方針に基づき、理学療法・作業療法・言語聴覚療法の具体的な訓練メニュー案を箇条書き形式で複数提案(100文字から250文字程度)。作業療法や理学療法など、職種が変わるときのみ改行してください。改行をしないでください。(100文字から250文字程度)"
    )

    # goal_p_household_role_txt: str = Field(
    #     description="患者の年齢、性別、ADL状況から、退院後に担う可能性のある現実的な家庭内役割の具体例を提案"
    # )
    # goal_p_hobby_txt: str = Field(description="患者のQOL向上に繋がりそうな趣味活動の具体例を提案")

    goal_a_action_plan_txt: str = Field(
        description="設定した活動目標（ADLなど）を達成するための具体的な対応方針、環境調整、指導内容を記述(100文字から500文字程度)"
    )
    goal_s_env_action_plan_txt: str = Field(
        description="退院後の生活を見据え、必要と考えられる住宅改修、社会資源の活用（介護保険サービス、障害福祉サービス等）に関する具体的な対応方針を記述(100文字から500文字程度)"
    )
    goal_p_action_plan_txt: str = Field(
        description="参加目標（復職、就学、家庭内役割など）を達成するための具体的な対応方針、関連機関との連携、家族への指導内容などを記述(100文字から300文字程度)"
    )
    goal_s_psychological_action_plan_txt: str = Field(
        description="心理面での目標（障害受容、精神的支援など）に対する具体的な関わり方、声かけ、家族への説明内容などを記述(100文字から200文字程度)"
    )
    goal_s_3rd_party_action_plan_txt: str = Field(
        description="主介護者や家族の負担軽減、環境の変化に対する具体的な支援策や社会資源の活用提案などを記述(100文字から200文字程度)"
    )


# --- グループ化された生成のためのスキーマ定義 ---
class RisksAndPrecautions(BaseModel):
    main_risks_txt: str = RehabPlanSchema.model_fields["main_risks_txt"]
    main_contraindications_txt: str = RehabPlanSchema.model_fields["main_contraindications_txt"]


class FunctionalLimitations(BaseModel):
    func_pain_txt: str = RehabPlanSchema.model_fields["func_pain_txt"]
    func_rom_limitation_txt: str = RehabPlanSchema.model_fields["func_rom_limitation_txt"]
    func_muscle_weakness_txt: str = RehabPlanSchema.model_fields["func_muscle_weakness_txt"]
    func_swallowing_disorder_txt: str = RehabPlanSchema.model_fields["func_swallowing_disorder_txt"]
    func_behavioral_psychiatric_disorder_txt: str = RehabPlanSchema.model_fields["func_behavioral_psychiatric_disorder_txt"]
    func_nutritional_disorder_txt: str = RehabPlanSchema.model_fields["func_nutritional_disorder_txt"]
    func_excretory_disorder_txt: str = RehabPlanSchema.model_fields["func_excretory_disorder_txt"]
    func_pressure_ulcer_txt: str = RehabPlanSchema.model_fields["func_pressure_ulcer_txt"]
    func_contracture_deformity_txt: str = RehabPlanSchema.model_fields["func_contracture_deformity_txt"]
    func_motor_muscle_tone_abnormality_txt: str = RehabPlanSchema.model_fields["func_motor_muscle_tone_abnormality_txt"]
    func_disorientation_txt: str = RehabPlanSchema.model_fields["func_disorientation_txt"]
    func_memory_disorder_txt: str = RehabPlanSchema.model_fields["func_memory_disorder_txt"]


class Goals(BaseModel):
    goals_1_month_txt: str = RehabPlanSchema.model_fields["goals_1_month_txt"]
    goals_at_discharge_txt: str = RehabPlanSchema.model_fields["goals_at_discharge_txt"]


class TreatmentPolicy(BaseModel):
    policy_treatment_txt: str = RehabPlanSchema.model_fields["policy_treatment_txt"]
    policy_content_txt: str = RehabPlanSchema.model_fields["policy_content_txt"]
    adl_equipment_and_assistance_details_txt: str = RehabPlanSchema.model_fields["adl_equipment_and_assistance_details_txt"]


class ActionPlans(BaseModel):
    goal_a_action_plan_txt: str = RehabPlanSchema.model_fields["goal_a_action_plan_txt"]
    goal_s_env_action_plan_txt: str = RehabPlanSchema.model_fields["goal_s_env_action_plan_txt"]
    goal_p_action_plan_txt: str = RehabPlanSchema.model_fields["goal_p_action_plan_txt"]
    goal_s_psychological_action_plan_txt: str = RehabPlanSchema.model_fields["goal_s_psychological_action_plan_txt"]
    goal_s_3rd_party_action_plan_txt: str = RehabPlanSchema.model_fields["goal_s_3rd_party_action_plan_txt"]


class CurrentAssessment(RisksAndPrecautions, FunctionalLimitations):
    """患者の現状評価（リスク、禁忌、機能障害）をまとめて生成するためのスキーマ"""

    pass


class ComprehensiveTreatmentPlan(TreatmentPolicy, ActionPlans):
    """目標達成のための包括的な治療計画（全体方針、ADL詳細、個別計画）をまとめて生成するためのスキーマ"""

    pass


# 生成をグループ単位で行うためのリスト
GENERATION_GROUPS = [
    CurrentAssessment,  # ステップ1: 現状評価（リスク、禁忌、機能障害）
    Goals,  # ステップ2: 目標設定
    ComprehensiveTreatmentPlan,  # ステップ3: 包括的な治療計画
]


class PatientMasterSchema(BaseModel):
    """カルテの自由記述テキストから抽出した患者マスタ情報。可能な限り全ての項目を埋めてください。不明な項目はnullにしてください。"""

    # --- Patientモデル由来の項目 ---
    name: Optional[str] = Field(None, description="患者氏名")
    age: Optional[int] = Field(None, description="患者の年齢")
    gender: Optional[str] = Field(None, description="患者の性別。'男'または'女'")

    # --- RehabilitationPlanモデル由来の項目 ---
    # 【1枚目】
    header_evaluation_date: Optional[date] = Field(None, description="評価日 (YYYY-MM-DD形式)")
    header_disease_name_txt: Optional[str] = Field(None, description="算定病名")
    header_treatment_details_txt: Optional[str] = Field(None, description="治療内容（手術名など）")
    header_onset_date: Optional[date] = Field(None, description="発症日または手術日 (YYYY-MM-DD形式)")
    header_rehab_start_date: Optional[date] = Field(None, description="リハビリテーション開始日 (YYYY-MM-DD形式)")
    header_therapy_pt_chk: Optional[bool] = Field(None, description="理学療法(PT)の実施有無")
    header_therapy_ot_chk: Optional[bool] = Field(None, description="作業療法(OT)の実施有無")
    header_therapy_st_chk: Optional[bool] = Field(None, description="言語聴覚療法(ST)の実施有無")
    main_comorbidities_txt: Optional[str] = Field(None, description="併存疾患・合併症")
    main_risks_txt: Optional[str] = Field(None, description="安静度やリハビリテーション施行上のリスク")
    main_contraindications_txt: Optional[str] = Field(None, description="禁忌や医学的な特記事項・注意点")
    func_consciousness_disorder_chk: Optional[bool] = Field(None, description="意識障害の有無")
    func_consciousness_disorder_jcs_gcs_txt: Optional[str] = Field(None, description="意識レベル (JCS, GCS)")
    func_respiratory_disorder_chk: Optional[bool] = Field(None, description="呼吸機能障害の有無")
    func_respiratory_o2_therapy_chk: Optional[bool] = Field(None, description="酸素療法の有無")
    func_respiratory_o2_therapy_l_min_txt: Optional[str] = Field(None, description="酸素流量 (L/min)")
    func_respiratory_tracheostomy_chk: Optional[bool] = Field(None, description="気管切開の有無")
    func_respiratory_ventilator_chk: Optional[bool] = Field(None, description="人工呼吸器使用の有無")
    func_circulatory_disorder_chk: Optional[bool] = Field(None, description="循環障害の有無")
    func_circulatory_ef_chk: Optional[bool] = Field(None, description="心駆出率(EF)測定の有無")
    func_circulatory_ef_val: Optional[int] = Field(None, description="心駆出率(EF)の値 (%)")
    func_circulatory_arrhythmia_chk: Optional[bool] = Field(None, description="不整脈の有無")
    func_circulatory_arrhythmia_status_slct: Optional[str] = Field(None, description="不整脈の状態 (例: 心房細動)")
    func_risk_factors_chk: Optional[bool] = Field(None, description="危険因子の有無")
    func_risk_hypertension_chk: Optional[bool] = Field(None, description="高血圧症の有無")
    func_risk_dyslipidemia_chk: Optional[bool] = Field(None, description="脂質異常症の有無")
    func_risk_diabetes_chk: Optional[bool] = Field(None, description="糖尿病の有無")
    func_risk_smoking_chk: Optional[bool] = Field(None, description="喫煙歴の有無")
    func_risk_obesity_chk: Optional[bool] = Field(None, description="肥満の有無")
    func_risk_hyperuricemia_chk: Optional[bool] = Field(None, description="高尿酸血症の有無")
    func_risk_ckd_chk: Optional[bool] = Field(None, description="慢性腎臓病(CKD)の有無")
    func_risk_family_history_chk: Optional[bool] = Field(None, description="家族歴の有無")
    func_risk_angina_chk: Optional[bool] = Field(None, description="狭心症の有無")
    func_risk_omi_chk: Optional[bool] = Field(None, description="陳旧性心筋梗塞(OMI)の有無")
    func_risk_other_chk: Optional[bool] = Field(None, description="その他の危険因子の有無")
    func_risk_other_txt: Optional[str] = Field(None, description="その他の危険因子の詳細")
    func_swallowing_disorder_chk: Optional[bool] = Field(None, description="摂食嚥下障害の有無")
    func_swallowing_disorder_txt: Optional[str] = Field(None, description="摂食嚥下障害の詳細")
    func_nutritional_disorder_chk: Optional[bool] = Field(None, description="栄養障害の有無")
    func_nutritional_disorder_txt: Optional[str] = Field(None, description="栄養障害の詳細")
    func_excretory_disorder_chk: Optional[bool] = Field(None, description="排泄機能障害の有無")
    func_excretory_disorder_txt: Optional[str] = Field(None, description="排泄機能障害の詳細")
    func_pressure_ulcer_chk: Optional[bool] = Field(None, description="褥瘡の有無")
    func_pressure_ulcer_txt: Optional[str] = Field(None, description="褥瘡の詳細 (部位、DESIGN-Rなど)")
    func_pain_chk: Optional[bool] = Field(None, description="疼痛の有無")
    func_pain_txt: Optional[str] = Field(None, description="疼痛の詳細 (部位、程度、NRSなど)")
    func_other_chk: Optional[bool] = Field(None, description="その他の心身機能障害の有無")
    func_other_txt: Optional[str] = Field(None, description="その他の心身機能障害の詳細")
    func_rom_limitation_chk: Optional[bool] = Field(None, description="関節可動域制限の有無")
    func_rom_limitation_txt: Optional[str] = Field(None, description="関節可動域制限の詳細")
    func_contracture_deformity_chk: Optional[bool] = Field(None, description="拘縮・変形の有無")
    func_contracture_deformity_txt: Optional[str] = Field(None, description="拘縮・変形の詳細")
    func_muscle_weakness_chk: Optional[bool] = Field(None, description="筋力低下の有無")
    func_muscle_weakness_txt: Optional[str] = Field(None, description="筋力低下の詳細 (MMTなど)")
    func_motor_dysfunction_chk: Optional[bool] = Field(None, description="運動機能障害の有無")
    func_motor_paralysis_chk: Optional[bool] = Field(None, description="麻痺の有無")
    func_motor_involuntary_movement_chk: Optional[bool] = Field(None, description="不随意運動の有無")
    func_motor_ataxia_chk: Optional[bool] = Field(None, description="運動失調の有無")
    func_motor_parkinsonism_chk: Optional[bool] = Field(None, description="パーキンソニズムの有無")
    func_motor_muscle_tone_abnormality_chk: Optional[bool] = Field(None, description="筋緊張異常の有無")
    func_motor_muscle_tone_abnormality_txt: Optional[str] = Field(None, description="筋緊張異常の詳細 (痙性, 固縮など)")
    func_sensory_dysfunction_chk: Optional[bool] = Field(None, description="感覚機能障害の有無")
    func_sensory_hearing_chk: Optional[bool] = Field(None, description="聴覚障害の有無")
    func_sensory_vision_chk: Optional[bool] = Field(None, description="視覚障害の有無")
    func_sensory_superficial_chk: Optional[bool] = Field(None, description="表在感覚障害の有無")
    func_sensory_deep_chk: Optional[bool] = Field(None, description="深部感覚障害の有無")
    func_speech_disorder_chk: Optional[bool] = Field(None, description="音声発話障害の有無")
    func_speech_articulation_chk: Optional[bool] = Field(None, description="構音障害の有無")
    func_speech_aphasia_chk: Optional[bool] = Field(None, description="失語症の有無")
    func_speech_stuttering_chk: Optional[bool] = Field(None, description="吃音の有無")
    func_speech_other_chk: Optional[bool] = Field(None, description="その他の音声発話障害の有無")
    func_speech_other_txt: Optional[str] = Field(None, description="その他の音声発話障害の詳細")
    func_higher_brain_dysfunction_chk: Optional[bool] = Field(None, description="高次脳機能障害の有無")
    func_higher_brain_memory_chk: Optional[bool] = Field(None, description="記憶障害(高次脳)の有無")
    func_higher_brain_attention_chk: Optional[bool] = Field(None, description="注意障害の有無")
    func_higher_brain_apraxia_chk: Optional[bool] = Field(None, description="失行の有無")
    func_higher_brain_agnosia_chk: Optional[bool] = Field(None, description="失認の有無")
    func_higher_brain_executive_chk: Optional[bool] = Field(None, description="遂行機能障害の有無")
    func_behavioral_psychiatric_disorder_chk: Optional[bool] = Field(None, description="精神行動障害の有無")
    func_behavioral_psychiatric_disorder_txt: Optional[str] = Field(None, description="精神行動障害の詳細")
    func_disorientation_chk: Optional[bool] = Field(None, description="見当識障害の有無")
    func_disorientation_txt: Optional[str] = Field(None, description="見当識障害の詳細")
    func_memory_disorder_chk: Optional[bool] = Field(None, description="記憶障害の有無")
    func_memory_disorder_txt: Optional[str] = Field(None, description="記憶障害の詳細")
    func_developmental_disorder_chk: Optional[bool] = Field(None, description="発達障害の有無")
    func_developmental_asd_chk: Optional[bool] = Field(None, description="自閉症スペクトラム症(ASD)の有無")
    func_developmental_ld_chk: Optional[bool] = Field(None, description="学習障害(LD)の有無")
    func_developmental_adhd_chk: Optional[bool] = Field(None, description="注意欠陥多動性障害(ADHD)の有無")
    func_basic_rolling_chk: Optional[bool] = Field(None, description="寝返り動作の評価有無")
    func_basic_rolling_independent_chk: Optional[bool] = Field(None, description="寝返り: 自立")
    func_basic_rolling_partial_assistance_chk: Optional[bool] = Field(None, description="寝返り: 一部介助")
    func_basic_rolling_assistance_chk: Optional[bool] = Field(None, description="寝返り: 全介助")
    func_basic_rolling_not_performed_chk: Optional[bool] = Field(None, description="寝返り: 行わない")
    func_basic_getting_up_chk: Optional[bool] = Field(None, description="起き上がり動作の評価有無")
    func_basic_getting_up_independent_chk: Optional[bool] = Field(None, description="起き上がり: 自立")
    func_basic_getting_up_partial_assistance_chk: Optional[bool] = Field(None, description="起き上がり: 一部介助")
    func_basic_getting_up_assistance_chk: Optional[bool] = Field(None, description="起き上がり: 全介助")
    func_basic_getting_up_not_performed_chk: Optional[bool] = Field(None, description="起き上がり: 行わない")
    func_basic_standing_up_chk: Optional[bool] = Field(None, description="立ち上がり動作の評価有無")
    func_basic_standing_up_independent_chk: Optional[bool] = Field(None, description="立ち上がり: 自立")
    func_basic_standing_up_partial_assistance_chk: Optional[bool] = Field(None, description="立ち上がり: 一部介助")
    func_basic_standing_up_assistance_chk: Optional[bool] = Field(None, description="立ち上がり: 全介助")
    func_basic_standing_up_not_performed_chk: Optional[bool] = Field(None, description="立ち上がり: 行わない")
    func_basic_sitting_balance_chk: Optional[bool] = Field(None, description="座位保持の評価有無")
    func_basic_sitting_balance_independent_chk: Optional[bool] = Field(None, description="座位保持: 自立")
    func_basic_sitting_balance_partial_assistance_chk: Optional[bool] = Field(None, description="座位保持: 一部介助")
    func_basic_sitting_balance_assistance_chk: Optional[bool] = Field(None, description="座位保持: 全介助")
    func_basic_sitting_balance_not_performed_chk: Optional[bool] = Field(None, description="座位保持: 行わない")
    func_basic_standing_balance_chk: Optional[bool] = Field(None, description="立位保持の評価有無")
    func_basic_standing_balance_independent_chk: Optional[bool] = Field(None, description="立位保持: 自立")
    func_basic_standing_balance_partial_assistance_chk: Optional[bool] = Field(None, description="立位保持: 一部介助")
    func_basic_standing_balance_assistance_chk: Optional[bool] = Field(None, description="立位保持: 全介助")
    func_basic_standing_balance_not_performed_chk: Optional[bool] = Field(None, description="立位保持: 行わない")
    func_basic_other_chk: Optional[bool] = Field(None, description="その他の基本動作の評価有無")
    func_basic_other_txt: Optional[str] = Field(None, description="その他の基本動作の詳細")
    adl_eating_fim_start_val: Optional[int] = Field(None, description="食事のFIM開始時値")
    adl_eating_fim_current_val: Optional[int] = Field(None, description="食事のFIM現在値")
    adl_eating_bi_start_val: Optional[int] = Field(None, description="食事のBI開始時値")
    adl_eating_bi_current_val: Optional[int] = Field(None, description="食事のBI現在値")
    adl_grooming_fim_start_val: Optional[int] = Field(None, description="整容のFIM開始時値")
    adl_grooming_fim_current_val: Optional[int] = Field(None, description="整容のFIM現在値")
    adl_grooming_bi_start_val: Optional[int] = Field(None, description="整容のBI開始時値")
    adl_grooming_bi_current_val: Optional[int] = Field(None, description="整容のBI現在値")
    adl_bathing_fim_start_val: Optional[int] = Field(None, description="入浴のFIM開始時値")
    adl_bathing_fim_current_val: Optional[int] = Field(None, description="入浴のFIM現在値")
    adl_bathing_bi_start_val: Optional[int] = Field(None, description="入浴のBI開始時値")
    adl_bathing_bi_current_val: Optional[int] = Field(None, description="入浴のBI現在値")
    adl_dressing_upper_fim_start_val: Optional[int] = Field(None, description="更衣(上半身)のFIM開始時値")
    adl_dressing_upper_fim_current_val: Optional[int] = Field(None, description="更衣(上半身)のFIM現在値")
    adl_dressing_lower_fim_start_val: Optional[int] = Field(None, description="更衣(下半身)のFIM開始時値")
    adl_dressing_lower_fim_current_val: Optional[int] = Field(None, description="更衣(下半身)のFIM現在値")
    adl_dressing_bi_start_val: Optional[int] = Field(None, description="更衣のBI開始時値")
    adl_dressing_bi_current_val: Optional[int] = Field(None, description="更衣のBI現在値")
    adl_toileting_fim_start_val: Optional[int] = Field(None, description="トイレ動作のFIM開始時値")
    adl_toileting_fim_current_val: Optional[int] = Field(None, description="トイレ動作のFIM現在値")
    adl_toileting_bi_start_val: Optional[int] = Field(None, description="トイレ動作のBI開始時値")
    adl_toileting_bi_current_val: Optional[int] = Field(None, description="トイレ動作のBI現在値")
    adl_bladder_management_fim_start_val: Optional[int] = Field(None, description="排尿管理のFIM開始時値")
    adl_bladder_management_fim_current_val: Optional[int] = Field(None, description="排尿管理のFIM現在値")
    adl_bladder_management_bi_start_val: Optional[int] = Field(None, description="排尿管理のBI開始時値")
    adl_bladder_management_bi_current_val: Optional[int] = Field(None, description="排尿管理のBI現在値")
    adl_bowel_management_fim_start_val: Optional[int] = Field(None, description="排便管理のFIM開始時値")
    adl_bowel_management_fim_current_val: Optional[int] = Field(None, description="排便管理のFIM現在値")
    adl_bowel_management_bi_start_val: Optional[int] = Field(None, description="排便管理のBI開始時値")
    adl_bowel_management_bi_current_val: Optional[int] = Field(None, description="排便管理のBI現在値")
    adl_transfer_bed_chair_wc_fim_start_val: Optional[int] = Field(None, description="移乗(ベッド・椅子・車椅子)のFIM開始時値")
    adl_transfer_bed_chair_wc_fim_current_val: Optional[int] = Field(None, description="移乗(ベッド・椅子・車椅子)のFIM現在値")
    adl_transfer_toilet_fim_start_val: Optional[int] = Field(None, description="移乗(トイレ)のFIM開始時値")
    adl_transfer_toilet_fim_current_val: Optional[int] = Field(None, description="移乗(トイレ)のFIM現在値")
    adl_transfer_tub_shower_fim_start_val: Optional[int] = Field(None, description="移乗(浴槽・シャワー)のFIM開始時値")
    adl_transfer_tub_shower_fim_current_val: Optional[int] = Field(None, description="移乗(浴槽・シャワー)のFIM現在値")
    adl_transfer_bi_start_val: Optional[int] = Field(None, description="移乗のBI開始時値")
    adl_transfer_bi_current_val: Optional[int] = Field(None, description="移乗のBI現在値")
    adl_locomotion_walk_walkingAids_wc_fim_start_val: Optional[int] = Field(None, description="移動(歩行/車椅子)のFIM開始時値")
    adl_locomotion_walk_walkingAids_wc_fim_current_val: Optional[int] = Field(None, description="移動(歩行/車椅子)のFIM現在値")
    adl_locomotion_walk_walkingAids_wc_bi_start_val: Optional[int] = Field(None, description="移動のBI開始時値")
    adl_locomotion_walk_walkingAids_wc_bi_current_val: Optional[int] = Field(None, description="移動のBI現在値")
    adl_locomotion_stairs_fim_start_val: Optional[int] = Field(None, description="階段のFIM開始時値")
    adl_locomotion_stairs_fim_current_val: Optional[int] = Field(None, description="階段のFIM現在値")
    adl_locomotion_stairs_bi_start_val: Optional[int] = Field(None, description="階段のBI開始時値")
    adl_locomotion_stairs_bi_current_val: Optional[int] = Field(None, description="階段のBI現在値")
    adl_comprehension_fim_start_val: Optional[int] = Field(None, description="理解のFIM開始時値")
    adl_comprehension_fim_current_val: Optional[int] = Field(None, description="理解のFIM現在値")
    adl_expression_fim_start_val: Optional[int] = Field(None, description="表出のFIM開始時値")
    adl_expression_fim_current_val: Optional[int] = Field(None, description="表出のFIM現在値")
    adl_social_interaction_fim_start_val: Optional[int] = Field(None, description="社会的交流のFIM開始時値")
    adl_social_interaction_fim_current_val: Optional[int] = Field(None, description="社会的交流のFIM現在値")
    adl_problem_solving_fim_start_val: Optional[int] = Field(None, description="問題解決のFIM開始時値")
    adl_problem_solving_fim_current_val: Optional[int] = Field(None, description="問題解決のFIM現在値")
    adl_memory_fim_start_val: Optional[int] = Field(None, description="記憶のFIM開始時値")
    adl_memory_fim_current_val: Optional[int] = Field(None, description="記憶のFIM現在値")
    adl_equipment_and_assistance_details_txt: Optional[str] = Field(None, description="ADLの補装具・介助方法の詳細")
    nutrition_height_chk: Optional[bool] = Field(None, description="身長測定の有無")
    nutrition_height_val: Optional[float] = Field(None, description="身長 (cm)")
    nutrition_weight_chk: Optional[bool] = Field(None, description="体重測定の有無")
    nutrition_weight_val: Optional[float] = Field(None, description="体重 (kg)")
    nutrition_bmi_chk: Optional[bool] = Field(None, description="BMI計算の有無")
    nutrition_bmi_val: Optional[float] = Field(None, description="BMI値")
    nutrition_method_oral_chk: Optional[bool] = Field(None, description="栄養補給(経口)の有無")
    nutrition_method_oral_meal_chk: Optional[bool] = Field(None, description="経口栄養(食事)の有無")
    nutrition_method_oral_supplement_chk: Optional[bool] = Field(None, description="経口栄養(補助食品)の有無")
    nutrition_method_tube_chk: Optional[bool] = Field(None, description="経管栄養の有無")
    nutrition_method_iv_chk: Optional[bool] = Field(None, description="静脈栄養の有無")
    nutrition_method_iv_peripheral_chk: Optional[bool] = Field(None, description="末梢静脈栄養の有無")
    nutrition_method_iv_central_chk: Optional[bool] = Field(None, description="中心静脈栄養の有無")
    nutrition_method_peg_chk: Optional[bool] = Field(None, description="胃ろうの有無")
    nutrition_swallowing_diet_slct: Optional[str] = Field(None, description="嚥下調整食の選択")
    nutrition_swallowing_diet_code_txt: Optional[str] = Field(None, description="嚥下調整食コード")
    nutrition_status_assessment_slct: Optional[str] = Field(None, description="栄養状態評価の選択")
    nutrition_status_assessment_other_txt: Optional[str] = Field(None, description="その他の栄養状態評価")
    nutrition_required_energy_val: Optional[int] = Field(None, description="必要エネルギー量 (kcal)")
    nutrition_required_protein_val: Optional[int] = Field(None, description="必要タンパク質量 (g)")
    nutrition_total_intake_energy_val: Optional[int] = Field(None, description="総摂取エネルギー量 (kcal)")
    nutrition_total_intake_protein_val: Optional[int] = Field(None, description="総摂取タンパク質量 (g)")
    social_care_level_status_chk: Optional[bool] = Field(None, description="介護保険状況の有無")
    social_care_level_applying_chk: Optional[bool] = Field(None, description="介護保険(申請中)の有無")
    social_care_level_support_chk: Optional[bool] = Field(None, description="要支援認定の有無")
    social_care_level_support_num1_slct: Optional[bool] = Field(None, description="要支援1")
    social_care_level_support_num2_slct: Optional[bool] = Field(None, description="要支援2")
    social_care_level_care_slct: Optional[bool] = Field(None, description="要介護認定の有無")
    social_care_level_care_num1_slct: Optional[bool] = Field(None, description="要介護1")
    social_care_level_care_num2_slct: Optional[bool] = Field(None, description="要介護2")
    social_care_level_care_num3_slct: Optional[bool] = Field(None, description="要介護3")
    social_care_level_care_num4_slct: Optional[bool] = Field(None, description="要介護4")
    social_care_level_care_num5_slct: Optional[bool] = Field(None, description="要介護5")
    social_disability_certificate_physical_chk: Optional[bool] = Field(None, description="身体障害者手帳の有無")
    social_disability_certificate_physical_txt: Optional[str] = Field(None, description="身体障害者手帳の詳細")
    social_disability_certificate_physical_type_txt: Optional[str] = Field(None, description="身体障害者手帳の種別")
    social_disability_certificate_physical_rank_val: Optional[int] = Field(None, description="身体障害者手帳の等級")
    social_disability_certificate_mental_chk: Optional[bool] = Field(None, description="精神障害者保健福祉手帳の有無")
    social_disability_certificate_mental_rank_val: Optional[int] = Field(None, description="精神障害者保健福祉手帳の等級")
    social_disability_certificate_intellectual_chk: Optional[bool] = Field(None, description="療育手帳の有無")
    social_disability_certificate_intellectual_txt: Optional[str] = Field(None, description="療育手帳の詳細")
    social_disability_certificate_intellectual_grade_txt: Optional[str] = Field(None, description="療育手帳の等級")
    social_disability_certificate_other_chk: Optional[bool] = Field(None, description="その他の手帳の有無")
    social_disability_certificate_other_txt: Optional[str] = Field(None, description="その他の手帳の詳細")
    goals_1_month_txt: Optional[str] = Field(None, description="1ヶ月の短期目標")
    goals_at_discharge_txt: Optional[str] = Field(None, description="退院時の長期目標")
    goals_planned_hospitalization_period_chk: Optional[bool] = Field(None, description="入院期間の予定有無")
    goals_planned_hospitalization_period_txt: Optional[str] = Field(None, description="入院期間の予定詳細")
    goals_discharge_destination_chk: Optional[bool] = Field(None, description="退院先の予定有無")
    goals_discharge_destination_txt: Optional[str] = Field(None, description="退院先の予定詳細")
    goals_long_term_care_needed_chk: Optional[bool] = Field(None, description="長期療養の必要性有無")
    policy_treatment_txt: Optional[str] = Field(None, description="リハビリテーションの全体的な治療方針")
    policy_content_txt: Optional[str] = Field(None, description="具体的な訓練メニュー案")
    signature_rehab_doctor_txt: Optional[str] = Field(None, description="リハビリテーション科医師の署名")
    signature_primary_doctor_txt: Optional[str] = Field(None, description="主治医の署名")
    signature_pt_txt: Optional[str] = Field(None, description="理学療法士の署名")
    signature_ot_txt: Optional[str] = Field(None, description="作業療法士の署名")
    signature_st_txt: Optional[str] = Field(None, description="言語聴覚士の署名")
    signature_nurse_txt: Optional[str] = Field(None, description="看護師の署名")
    signature_dietitian_txt: Optional[str] = Field(None, description="管理栄養士の署名")
    signature_social_worker_txt: Optional[str] = Field(None, description="ソーシャルワーカーの署名")
    signature_explained_to_txt: Optional[str] = Field(None, description="説明を受けた方の氏名")
    signature_explanation_date: Optional[date] = Field(None, description="説明日 (YYYY-MM-DD形式)")
    signature_explainer_txt: Optional[str] = Field(None, description="説明者の氏名")

    # 【2枚目】
    goal_p_residence_chk: Optional[bool] = Field(None, description="住居場所の目標有無")
    goal_p_residence_slct: Optional[str] = Field(None, description="住居場所の選択 (自宅など)")
    goal_p_residence_other_txt: Optional[str] = Field(None, description="その他の住居場所")
    goal_p_return_to_work_chk: Optional[bool] = Field(None, description="復職の目標有無")
    goal_p_return_to_work_status_slct: Optional[str] = Field(None, description="復職状況の選択")
    goal_p_return_to_work_status_other_txt: Optional[str] = Field(None, description="その他の復職状況")
    goal_p_return_to_work_commute_change_chk: Optional[bool] = Field(None, description="通勤方法の変更有無")
    goal_p_schooling_chk: Optional[bool] = Field(None, description="就学の目標有無")
    goal_p_schooling_status_possible_chk: Optional[bool] = Field(None, description="就学: 可能")
    goal_p_schooling_status_needs_consideration_chk: Optional[bool] = Field(None, description="就学: 要検討")
    goal_p_schooling_status_change_course_chk: Optional[bool] = Field(None, description="就学: 転科・転校")
    goal_p_schooling_status_not_possible_chk: Optional[bool] = Field(None, description="就学: 不可能")
    goal_p_schooling_status_other_chk: Optional[bool] = Field(None, description="就学: その他")
    goal_p_schooling_status_other_txt: Optional[str] = Field(None, description="その他の就学状況")
    goal_p_schooling_destination_chk: Optional[bool] = Field(None, description="就学先の有無")
    goal_p_schooling_destination_txt: Optional[str] = Field(None, description="就学先の詳細")
    goal_p_schooling_commute_change_chk: Optional[bool] = Field(None, description="通学方法の変更有無")
    goal_p_schooling_commute_change_txt: Optional[str] = Field(None, description="通学方法の変更詳細")
    goal_p_household_role_chk: Optional[bool] = Field(None, description="家庭内役割の目標有無")
    goal_p_household_role_txt: Optional[str] = Field(None, description="家庭内役割の詳細")
    goal_p_social_activity_chk: Optional[bool] = Field(None, description="社会活動の目標有無")
    goal_p_social_activity_txt: Optional[str] = Field(None, description="社会活動の詳細")
    goal_p_hobby_chk: Optional[bool] = Field(None, description="趣味の目標有無")
    goal_p_hobby_txt: Optional[str] = Field(None, description="趣味の詳細")
    goal_a_action_plan_txt: Optional[str] = Field(None, description="活動目標の達成に向けた具体的対応方針")
    goal_s_env_action_plan_txt: Optional[str] = Field(None, description="環境因子への具体的対応方針")
    goal_p_action_plan_txt: Optional[str] = Field(None, description="参加目標の達成に向けた具体的対応方針")
    goal_s_psychological_action_plan_txt: Optional[str] = Field(None, description="心理面への具体的対応方針")
    goal_s_3rd_party_action_plan_txt: Optional[str] = Field(None, description="人的因子への具体的対応方針")

    # --- 2枚目 goal_a_* (活動目標) ---
    goal_a_bed_mobility_chk: Optional[bool] = Field(None, description="活動目標(床上移動)の有無")
    goal_a_bed_mobility_independent_chk: Optional[bool] = Field(None, description="活動目標(床上移動): 自立")
    goal_a_bed_mobility_assistance_chk: Optional[bool] = Field(None, description="活動目標(床上移動): 介助")
    goal_a_bed_mobility_not_performed_chk: Optional[bool] = Field(None, description="活動目標(床上移動): 行わない")
    goal_a_bed_mobility_equipment_chk: Optional[bool] = Field(None, description="活動目標(床上移動): 補装具")
    goal_a_bed_mobility_environment_setup_chk: Optional[bool] = Field(None, description="活動目標(床上移動): 環境設定")
    goal_a_indoor_mobility_chk: Optional[bool] = Field(None, description="活動目標(屋内移動)の有無")
    goal_a_indoor_mobility_independent_chk: Optional[bool] = Field(None, description="活動目標(屋内移動): 自立")
    goal_a_indoor_mobility_assistance_chk: Optional[bool] = Field(None, description="活動目標(屋内移動): 介助")
    goal_a_indoor_mobility_not_performed_chk: Optional[bool] = Field(None, description="活動目標(屋内移動): 行わない")
    goal_a_indoor_mobility_equipment_chk: Optional[bool] = Field(None, description="活動目標(屋内移動): 補装具")
    goal_a_indoor_mobility_equipment_txt: Optional[str] = Field(None, description="活動目標(屋内移動): 補装具詳細")
    goal_a_outdoor_mobility_chk: Optional[bool] = Field(None, description="活動目標(屋外移動)の有無")
    goal_a_outdoor_mobility_independent_chk: Optional[bool] = Field(None, description="活動目標(屋外移動): 自立")
    goal_a_outdoor_mobility_assistance_chk: Optional[bool] = Field(None, description="活動目標(屋外移動): 介助")
    goal_a_outdoor_mobility_not_performed_chk: Optional[bool] = Field(None, description="活動目標(屋外移動): 行わない")
    goal_a_outdoor_mobility_equipment_chk: Optional[bool] = Field(None, description="活動目標(屋外移動): 補装具")
    goal_a_outdoor_mobility_equipment_txt: Optional[str] = Field(None, description="活動目標(屋外移動): 補装具詳細")
    goal_a_driving_chk: Optional[bool] = Field(None, description="活動目標(自動車運転)の有無")
    goal_a_driving_independent_chk: Optional[bool] = Field(None, description="活動目標(自動車運転): 自立")
    goal_a_driving_assistance_chk: Optional[bool] = Field(None, description="活動目標(自動車運転): 介助")
    goal_a_driving_not_performed_chk: Optional[bool] = Field(None, description="活動目標(自動車運転): 行わない")
    goal_a_driving_modification_chk: Optional[bool] = Field(None, description="活動目標(自動車運転): 改造")
    goal_a_driving_modification_txt: Optional[str] = Field(None, description="活動目標(自動車運転): 改造詳細")
    goal_a_public_transport_chk: Optional[bool] = Field(None, description="活動目標(公共交通機関)の有無")
    goal_a_public_transport_independent_chk: Optional[bool] = Field(None, description="活動目標(公共交通機関): 自立")
    goal_a_public_transport_assistance_chk: Optional[bool] = Field(None, description="活動目標(公共交通機関): 介助")
    goal_a_public_transport_not_performed_chk: Optional[bool] = Field(None, description="活動目標(公共交通機関): 行わない")
    goal_a_public_transport_type_chk: Optional[bool] = Field(None, description="活動目標(公共交通機関): 種類")
    goal_a_public_transport_type_txt: Optional[str] = Field(None, description="活動目標(公共交通機関): 種類詳細")
    goal_a_toileting_chk: Optional[bool] = Field(None, description="活動目標(排泄)の有無")
    goal_a_toileting_independent_chk: Optional[bool] = Field(None, description="活動目標(排泄): 自立")
    goal_a_toileting_assistance_chk: Optional[bool] = Field(None, description="活動目標(排泄): 介助")
    goal_a_toileting_assistance_clothing_chk: Optional[bool] = Field(None, description="活動目標(排泄): 衣服の着脱")
    goal_a_toileting_assistance_wiping_chk: Optional[bool] = Field(None, description="活動目標(排泄): 清拭")
    goal_a_toileting_assistance_catheter_chk: Optional[bool] = Field(None, description="活動目標(排泄): カテーテル")
    goal_a_toileting_type_chk: Optional[bool] = Field(None, description="活動目標(排泄): 種類")
    goal_a_toileting_type_western_chk: Optional[bool] = Field(None, description="活動目標(排泄): 洋式")
    goal_a_toileting_type_japanese_chk: Optional[bool] = Field(None, description="活動目標(排泄): 和式")
    goal_a_toileting_type_other_chk: Optional[bool] = Field(None, description="活動目標(排泄): その他")
    goal_a_toileting_type_other_txt: Optional[str] = Field(None, description="活動目標(排泄): その他詳細")
    goal_a_eating_chk: Optional[bool] = Field(None, description="活動目標(食事)の有無")
    goal_a_eating_independent_chk: Optional[bool] = Field(None, description="活動目標(食事): 自立")
    goal_a_eating_assistance_chk: Optional[bool] = Field(None, description="活動目標(食事): 介助")
    goal_a_eating_not_performed_chk: Optional[bool] = Field(None, description="活動目標(食事): 行わない")
    goal_a_eating_method_chopsticks_chk: Optional[bool] = Field(None, description="活動目標(食事): 箸")
    goal_a_eating_method_fork_etc_chk: Optional[bool] = Field(None, description="活動目標(食事): フォーク等")
    goal_a_eating_method_tube_feeding_chk: Optional[bool] = Field(None, description="活動目標(食事): 経管栄養")
    goal_a_eating_diet_form_txt: Optional[str] = Field(None, description="活動目標(食事): 食事形態")
    goal_a_grooming_chk: Optional[bool] = Field(None, description="活動目標(整容)の有無")
    goal_a_grooming_independent_chk: Optional[bool] = Field(None, description="活動目標(整容): 自立")
    goal_a_grooming_assistance_chk: Optional[bool] = Field(None, description="活動目標(整容): 介助")
    goal_a_dressing_chk: Optional[bool] = Field(None, description="活動目標(更衣)の有無")
    goal_a_dressing_independent_chk: Optional[bool] = Field(None, description="活動目標(更衣): 自立")
    goal_a_dressing_assistance_chk: Optional[bool] = Field(None, description="活動目標(更衣): 介助")
    goal_a_bathing_chk: Optional[bool] = Field(None, description="活動目標(入浴)の有無")
    goal_a_bathing_independent_chk: Optional[bool] = Field(None, description="活動目標(入浴): 自立")
    goal_a_bathing_assistance_chk: Optional[bool] = Field(None, description="活動目標(入浴): 介助")
    goal_a_bathing_type_tub_chk: Optional[bool] = Field(None, description="活動目標(入浴): 浴槽")
    goal_a_bathing_type_shower_chk: Optional[bool] = Field(None, description="活動目標(入浴): シャワー")
    goal_a_bathing_assistance_body_washing_chk: Optional[bool] = Field(None, description="活動目標(入浴): 洗身")
    goal_a_bathing_assistance_transfer_chk: Optional[bool] = Field(None, description="活動目標(入浴): 移乗")
    goal_a_housework_meal_chk: Optional[bool] = Field(None, description="活動目標(家事)の有無")
    goal_a_housework_meal_all_chk: Optional[bool] = Field(None, description="活動目標(家事): 全般")
    goal_a_housework_meal_not_performed_chk: Optional[bool] = Field(None, description="活動目標(家事): 行わない")
    goal_a_housework_meal_partial_chk: Optional[bool] = Field(None, description="活動目標(家事): 一部")
    goal_a_housework_meal_partial_txt: Optional[str] = Field(None, description="活動目標(家事): 一部詳細")
    goal_a_writing_chk: Optional[bool] = Field(None, description="活動目標(書字)の有無")
    goal_a_writing_independent_chk: Optional[bool] = Field(None, description="活動目標(書字): 自立")
    goal_a_writing_independent_after_hand_change_chk: Optional[bool] = Field(
        None, description="活動目標(書字): 利き手交換後自立"
    )
    goal_a_writing_other_chk: Optional[bool] = Field(None, description="活動目標(書字): その他")
    goal_a_writing_other_txt: Optional[str] = Field(None, description="活動目標(書字): その他詳細")
    goal_a_ict_chk: Optional[bool] = Field(None, description="活動目標(ICT機器)の有無")
    goal_a_ict_independent_chk: Optional[bool] = Field(None, description="活動目標(ICT機器): 自立")
    goal_a_ict_assistance_chk: Optional[bool] = Field(None, description="活動目標(ICT機器): 介助")
    goal_a_communication_chk: Optional[bool] = Field(None, description="活動目標(コミュニケーション)の有無")
    goal_a_communication_independent_chk: Optional[bool] = Field(None, description="活動目標(コミュニケーション): 自立")
    goal_a_communication_assistance_chk: Optional[bool] = Field(None, description="活動目標(コミュニケーション): 介助")
    goal_a_communication_device_chk: Optional[bool] = Field(None, description="活動目標(コミュニケーション): 機器使用")
    goal_a_communication_letter_board_chk: Optional[bool] = Field(None, description="活動目標(コミュニケーション): 文字盤使用")
    goal_a_communication_cooperation_chk: Optional[bool] = Field(None, description="活動目標(コミュニケーション): 協力")

    # --- 2枚目 goal_s_* (対応を要する項目) ---
    goal_s_psychological_support_chk: Optional[bool] = Field(None, description="対応項目(心理的支援)の有無")
    goal_s_psychological_support_txt: Optional[str] = Field(None, description="対応項目(心理的支援): 詳細")
    goal_s_disability_acceptance_chk: Optional[bool] = Field(None, description="対応項目(障害受容)の有無")
    goal_s_disability_acceptance_txt: Optional[str] = Field(None, description="対応項目(障害受容): 詳細")
    goal_s_psychological_other_chk: Optional[bool] = Field(None, description="対応項目(心理面その他)の有無")
    goal_s_psychological_other_txt: Optional[str] = Field(None, description="対応項目(心理面その他): 詳細")
    goal_s_env_home_modification_chk: Optional[bool] = Field(None, description="対応項目(住宅改修)の有無")
    goal_s_env_home_modification_txt: Optional[str] = Field(None, description="対応項目(住宅改修): 詳細")
    goal_s_env_assistive_device_chk: Optional[bool] = Field(None, description="対応項目(補装具)の有無")
    goal_s_env_assistive_device_txt: Optional[str] = Field(None, description="対応項目(補装具): 詳細")
    goal_s_env_social_security_chk: Optional[bool] = Field(None, description="対応項目(社会保障)の有無")
    goal_s_env_social_security_physical_disability_cert_chk: Optional[bool] = Field(
        None, description="対応項目(社会保障): 身体障害者手帳"
    )
    goal_s_env_social_security_disability_pension_chk: Optional[bool] = Field(None, description="対応項目(社会保障): 障害年金")
    goal_s_env_social_security_intractable_disease_cert_chk: Optional[bool] = Field(
        None, description="対応項目(社会保障): 難病医療費助成"
    )
    goal_s_env_social_security_other_chk: Optional[bool] = Field(None, description="対応項目(社会保障): その他")
    goal_s_env_social_security_other_txt: Optional[str] = Field(None, description="対応項目(社会保障): その他詳細")
    goal_s_env_care_insurance_chk: Optional[bool] = Field(None, description="対応項目(介護保険)の有無")
    goal_s_env_care_insurance_details_txt: Optional[str] = Field(None, description="対応項目(介護保険): 詳細")
    goal_s_env_care_insurance_outpatient_rehab_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 通所リハ")
    goal_s_env_care_insurance_home_rehab_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 訪問リハ")
    goal_s_env_care_insurance_day_care_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 通所介護")
    goal_s_env_care_insurance_home_nursing_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 訪問看護")
    goal_s_env_care_insurance_home_care_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 訪問介護")
    goal_s_env_care_insurance_health_facility_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 老健")
    goal_s_env_care_insurance_nursing_home_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 特養")
    goal_s_env_care_insurance_care_hospital_chk: Optional[bool] = Field(None, description="対応項目(介護保険): 介護医療院")
    goal_s_env_care_insurance_other_chk: Optional[bool] = Field(None, description="対応項目(介護保険): その他")
    goal_s_env_care_insurance_other_txt: Optional[str] = Field(None, description="対応項目(介護保険): その他詳細")
    goal_s_env_disability_welfare_chk: Optional[bool] = Field(None, description="対応項目(障害福祉)の有無")
    goal_s_env_disability_welfare_after_school_day_service_chk: Optional[bool] = Field(
        None, description="対応項目(障害福祉): 放課後等デイ"
    )
    goal_s_env_disability_welfare_child_development_support_chk: Optional[bool] = Field(
        None, description="対応項目(障害福祉): 児童発達支援"
    )
    goal_s_env_disability_welfare_life_care_chk: Optional[bool] = Field(None, description="対応項目(障害福祉): 生活介護")
    goal_s_env_disability_welfare_other_chk: Optional[bool] = Field(None, description="対応項目(障害福祉): その他")
    goal_s_env_other_chk: Optional[bool] = Field(None, description="対応項目(環境因子その他)の有無")
    goal_s_env_other_txt: Optional[str] = Field(None, description="対応項目(環境因子その他): 詳細")
    goal_s_3rd_party_main_caregiver_chk: Optional[bool] = Field(None, description="対応項目(主介護者)の有無")
    goal_s_3rd_party_main_caregiver_txt: Optional[str] = Field(None, description="対応項目(主介護者): 詳細")
    goal_s_3rd_party_family_structure_change_chk: Optional[bool] = Field(None, description="対応項目(家族構成変化)の有無")
    goal_s_3rd_party_family_structure_change_txt: Optional[str] = Field(None, description="対応項目(家族構成変化): 詳細")
    goal_s_3rd_party_household_role_change_chk: Optional[bool] = Field(None, description="対応項目(家庭内役割変化)の有無")
    goal_s_3rd_party_household_role_change_txt: Optional[str] = Field(None, description="対応項目(家庭内役割変化): 詳細")
    goal_s_3rd_party_family_activity_change_chk: Optional[bool] = Field(None, description="対応項目(家族活動変化)の有無")
    goal_s_3rd_party_family_activity_change_txt: Optional[str] = Field(None, description="対応項目(家族活動変化): 詳細")


# --- PatientMasterSchemaの分割定義 ---
# 巨大なスキーマをAPIが処理可能な小さなグループに分割します。


class PatientInfo_Basic(BaseModel):
    """患者の基本情報とリハビリテーションの概要"""

    name: Optional[str] = PatientMasterSchema.model_fields["name"]
    age: Optional[int] = PatientMasterSchema.model_fields["age"]
    gender: Optional[str] = Field(None, description="患者の性別。'男性'なら'男'、'女性'なら'女'と出力してください。")
    header_evaluation_date: Optional[date] = PatientMasterSchema.model_fields["header_evaluation_date"]
    header_disease_name_txt: Optional[str] = PatientMasterSchema.model_fields["header_disease_name_txt"]
    header_treatment_details_txt: Optional[str] = PatientMasterSchema.model_fields["header_treatment_details_txt"]
    header_onset_date: Optional[date] = PatientMasterSchema.model_fields["header_onset_date"]
    header_rehab_start_date: Optional[date] = PatientMasterSchema.model_fields["header_rehab_start_date"]
    header_therapy_pt_chk: Optional[bool] = PatientMasterSchema.model_fields["header_therapy_pt_chk"]
    header_therapy_ot_chk: Optional[bool] = PatientMasterSchema.model_fields["header_therapy_ot_chk"]
    header_therapy_st_chk: Optional[bool] = PatientMasterSchema.model_fields["header_therapy_st_chk"]
    main_comorbidities_txt: Optional[str] = PatientMasterSchema.model_fields["main_comorbidities_txt"]
    main_risks_txt: Optional[str] = PatientMasterSchema.model_fields["main_risks_txt"]
    main_contraindications_txt: Optional[str] = PatientMasterSchema.model_fields["main_contraindications_txt"]


class PatientInfo_Function_General(BaseModel):
    """患者の心身機能・構造に関する評価（全般）"""

    func_consciousness_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_consciousness_disorder_chk"]
    func_consciousness_disorder_jcs_gcs_txt: Optional[str] = PatientMasterSchema.model_fields[
        "func_consciousness_disorder_jcs_gcs_txt"
    ]
    func_respiratory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_respiratory_disorder_chk"]
    func_respiratory_o2_therapy_chk: Optional[bool] = PatientMasterSchema.model_fields["func_respiratory_o2_therapy_chk"]
    func_respiratory_o2_therapy_l_min_txt: Optional[str] = PatientMasterSchema.model_fields[
        "func_respiratory_o2_therapy_l_min_txt"
    ]
    func_respiratory_tracheostomy_chk: Optional[bool] = PatientMasterSchema.model_fields["func_respiratory_tracheostomy_chk"]
    func_respiratory_ventilator_chk: Optional[bool] = PatientMasterSchema.model_fields["func_respiratory_ventilator_chk"]
    func_circulatory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_circulatory_disorder_chk"]
    func_circulatory_ef_chk: Optional[bool] = PatientMasterSchema.model_fields["func_circulatory_ef_chk"]
    func_circulatory_ef_val: Optional[int] = PatientMasterSchema.model_fields["func_circulatory_ef_val"]
    func_circulatory_arrhythmia_chk: Optional[bool] = PatientMasterSchema.model_fields["func_circulatory_arrhythmia_chk"]
    func_circulatory_arrhythmia_status_slct: Optional[str] = PatientMasterSchema.model_fields[
        "func_circulatory_arrhythmia_status_slct"
    ]
    func_risk_factors_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_factors_chk"]
    func_risk_hypertension_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_hypertension_chk"]
    func_risk_dyslipidemia_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_dyslipidemia_chk"]
    func_risk_diabetes_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_diabetes_chk"]
    func_risk_smoking_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_smoking_chk"]
    func_risk_obesity_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_obesity_chk"]
    func_risk_hyperuricemia_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_hyperuricemia_chk"]
    func_risk_ckd_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_ckd_chk"]
    func_risk_family_history_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_family_history_chk"]
    func_risk_angina_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_angina_chk"]
    func_risk_omi_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_omi_chk"]
    func_risk_other_chk: Optional[bool] = PatientMasterSchema.model_fields["func_risk_other_chk"]
    func_risk_other_txt: Optional[str] = PatientMasterSchema.model_fields["func_risk_other_txt"]
    func_swallowing_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_swallowing_disorder_chk"]
    func_swallowing_disorder_txt: Optional[str] = PatientMasterSchema.model_fields["func_swallowing_disorder_txt"]
    func_nutritional_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_nutritional_disorder_chk"]
    func_nutritional_disorder_txt: Optional[str] = PatientMasterSchema.model_fields["func_nutritional_disorder_txt"]
    func_excretory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_excretory_disorder_chk"]
    func_excretory_disorder_txt: Optional[str] = PatientMasterSchema.model_fields["func_excretory_disorder_txt"]
    func_pressure_ulcer_chk: Optional[bool] = PatientMasterSchema.model_fields["func_pressure_ulcer_chk"]
    func_pressure_ulcer_txt: Optional[str] = PatientMasterSchema.model_fields["func_pressure_ulcer_txt"]
    func_pain_chk: Optional[bool] = PatientMasterSchema.model_fields["func_pain_chk"]
    func_pain_txt: Optional[str] = PatientMasterSchema.model_fields["func_pain_txt"]
    func_other_chk: Optional[bool] = PatientMasterSchema.model_fields["func_other_chk"]
    func_other_txt: Optional[str] = PatientMasterSchema.model_fields["func_other_txt"]


class PatientInfo_Function_Motor(BaseModel):
    """患者の心身機能・構造に関する評価（運動機能）"""

    func_rom_limitation_chk: Optional[bool] = PatientMasterSchema.model_fields["func_rom_limitation_chk"]
    func_rom_limitation_txt: Optional[str] = PatientMasterSchema.model_fields["func_rom_limitation_txt"]
    func_contracture_deformity_chk: Optional[bool] = PatientMasterSchema.model_fields["func_contracture_deformity_chk"]
    func_contracture_deformity_txt: Optional[str] = PatientMasterSchema.model_fields["func_contracture_deformity_txt"]
    func_muscle_weakness_chk: Optional[bool] = PatientMasterSchema.model_fields["func_muscle_weakness_chk"]
    func_muscle_weakness_txt: Optional[str] = PatientMasterSchema.model_fields["func_muscle_weakness_txt"]
    func_motor_dysfunction_chk: Optional[bool] = PatientMasterSchema.model_fields["func_motor_dysfunction_chk"]
    func_motor_paralysis_chk: Optional[bool] = PatientMasterSchema.model_fields["func_motor_paralysis_chk"]
    func_motor_involuntary_movement_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_motor_involuntary_movement_chk"
    ]
    func_motor_ataxia_chk: Optional[bool] = PatientMasterSchema.model_fields["func_motor_ataxia_chk"]
    func_motor_parkinsonism_chk: Optional[bool] = PatientMasterSchema.model_fields["func_motor_parkinsonism_chk"]
    func_motor_muscle_tone_abnormality_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_motor_muscle_tone_abnormality_chk"
    ]
    func_motor_muscle_tone_abnormality_txt: Optional[str] = PatientMasterSchema.model_fields[
        "func_motor_muscle_tone_abnormality_txt"
    ]


class PatientInfo_Function_Cognitive(BaseModel):
    """患者の心身機能・構造に関する評価（感覚・認知・言語）"""

    func_sensory_dysfunction_chk: Optional[bool] = PatientMasterSchema.model_fields["func_sensory_dysfunction_chk"]
    func_sensory_hearing_chk: Optional[bool] = PatientMasterSchema.model_fields["func_sensory_hearing_chk"]
    func_sensory_vision_chk: Optional[bool] = PatientMasterSchema.model_fields["func_sensory_vision_chk"]
    func_sensory_superficial_chk: Optional[bool] = PatientMasterSchema.model_fields["func_sensory_superficial_chk"]
    func_sensory_deep_chk: Optional[bool] = PatientMasterSchema.model_fields["func_sensory_deep_chk"]
    func_speech_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_speech_disorder_chk"]
    func_speech_articulation_chk: Optional[bool] = PatientMasterSchema.model_fields["func_speech_articulation_chk"]
    func_speech_aphasia_chk: Optional[bool] = PatientMasterSchema.model_fields["func_speech_aphasia_chk"]
    func_speech_stuttering_chk: Optional[bool] = PatientMasterSchema.model_fields["func_speech_stuttering_chk"]
    func_speech_other_chk: Optional[bool] = PatientMasterSchema.model_fields["func_speech_other_chk"]
    func_speech_other_txt: Optional[str] = PatientMasterSchema.model_fields["func_speech_other_txt"]
    func_higher_brain_dysfunction_chk: Optional[bool] = PatientMasterSchema.model_fields["func_higher_brain_dysfunction_chk"]
    func_higher_brain_memory_chk: Optional[bool] = PatientMasterSchema.model_fields["func_higher_brain_memory_chk"]
    func_higher_brain_attention_chk: Optional[bool] = PatientMasterSchema.model_fields["func_higher_brain_attention_chk"]
    func_higher_brain_apraxia_chk: Optional[bool] = PatientMasterSchema.model_fields["func_higher_brain_apraxia_chk"]
    func_higher_brain_agnosia_chk: Optional[bool] = PatientMasterSchema.model_fields["func_higher_brain_agnosia_chk"]
    func_higher_brain_executive_chk: Optional[bool] = PatientMasterSchema.model_fields["func_higher_brain_executive_chk"]
    func_behavioral_psychiatric_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_behavioral_psychiatric_disorder_chk"
    ]
    func_behavioral_psychiatric_disorder_txt: Optional[str] = PatientMasterSchema.model_fields[
        "func_behavioral_psychiatric_disorder_txt"
    ]
    func_disorientation_chk: Optional[bool] = PatientMasterSchema.model_fields["func_disorientation_chk"]
    func_disorientation_txt: Optional[str] = PatientMasterSchema.model_fields["func_disorientation_txt"]
    func_memory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_memory_disorder_chk"]
    func_memory_disorder_txt: Optional[str] = PatientMasterSchema.model_fields["func_memory_disorder_txt"]
    func_developmental_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields["func_developmental_disorder_chk"]
    func_developmental_asd_chk: Optional[bool] = PatientMasterSchema.model_fields["func_developmental_asd_chk"]
    func_developmental_ld_chk: Optional[bool] = PatientMasterSchema.model_fields["func_developmental_ld_chk"]
    func_developmental_adhd_chk: Optional[bool] = PatientMasterSchema.model_fields["func_developmental_adhd_chk"]


class PatientInfo_ADL(BaseModel):
    """患者のADL評価 (FIM, BI)"""

    # ADL関連の項目を抽出
    adl_eating_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_eating_fim_start_val"]
    adl_eating_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_eating_fim_current_val"]
    adl_eating_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_eating_bi_start_val"]
    adl_eating_bi_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_eating_bi_current_val"]
    adl_grooming_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_grooming_fim_start_val"]
    adl_grooming_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_grooming_fim_current_val"]
    adl_grooming_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_grooming_bi_start_val"]
    adl_grooming_bi_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_grooming_bi_current_val"]
    adl_bathing_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_bathing_fim_start_val"]
    adl_bathing_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_bathing_fim_current_val"]
    adl_bathing_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_bathing_bi_start_val"]
    adl_bathing_bi_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_bathing_bi_current_val"]
    adl_dressing_upper_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_dressing_upper_fim_start_val"]
    adl_dressing_upper_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_dressing_upper_fim_current_val"]
    adl_dressing_lower_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_dressing_lower_fim_start_val"]
    adl_dressing_lower_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_dressing_lower_fim_current_val"]
    adl_dressing_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_dressing_bi_start_val"]
    adl_dressing_bi_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_dressing_bi_current_val"]
    adl_toileting_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_toileting_fim_start_val"]
    adl_toileting_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_toileting_fim_current_val"]
    adl_toileting_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_toileting_bi_start_val"]
    adl_toileting_bi_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_toileting_bi_current_val"]
    adl_bladder_management_fim_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_bladder_management_fim_start_val"
    ]
    adl_bladder_management_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_bladder_management_fim_current_val"
    ]
    adl_bladder_management_bi_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_bladder_management_bi_start_val"
    ]
    adl_bladder_management_bi_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_bladder_management_bi_current_val"
    ]
    adl_bowel_management_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_bowel_management_fim_start_val"]
    adl_bowel_management_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_bowel_management_fim_current_val"
    ]
    adl_bowel_management_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_bowel_management_bi_start_val"]
    adl_bowel_management_bi_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_bowel_management_bi_current_val"
    ]
    adl_transfer_bed_chair_wc_fim_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_transfer_bed_chair_wc_fim_start_val"
    ]
    adl_transfer_bed_chair_wc_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_transfer_bed_chair_wc_fim_current_val"
    ]
    adl_transfer_toilet_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_transfer_toilet_fim_start_val"]
    adl_transfer_toilet_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_transfer_toilet_fim_current_val"
    ]
    adl_transfer_tub_shower_fim_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_transfer_tub_shower_fim_start_val"
    ]
    adl_transfer_tub_shower_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_transfer_tub_shower_fim_current_val"
    ]
    adl_transfer_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_transfer_bi_start_val"]
    adl_transfer_bi_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_transfer_bi_current_val"]
    adl_locomotion_walk_walkingAids_wc_fim_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_locomotion_walk_walkingAids_wc_fim_start_val"
    ]
    adl_locomotion_walk_walkingAids_wc_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_locomotion_walk_walkingAids_wc_fim_current_val"
    ]
    adl_locomotion_walk_walkingAids_wc_bi_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_locomotion_walk_walkingAids_wc_bi_start_val"
    ]
    adl_locomotion_walk_walkingAids_wc_bi_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_locomotion_walk_walkingAids_wc_bi_current_val"
    ]
    adl_locomotion_stairs_fim_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_locomotion_stairs_fim_start_val"
    ]
    adl_locomotion_stairs_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_locomotion_stairs_fim_current_val"
    ]
    adl_locomotion_stairs_bi_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_locomotion_stairs_bi_start_val"]
    adl_locomotion_stairs_bi_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_locomotion_stairs_bi_current_val"
    ]
    adl_comprehension_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_comprehension_fim_start_val"]
    adl_comprehension_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_comprehension_fim_current_val"]
    adl_expression_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_expression_fim_start_val"]
    adl_expression_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_expression_fim_current_val"]
    adl_social_interaction_fim_start_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_social_interaction_fim_start_val"
    ]
    adl_social_interaction_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_social_interaction_fim_current_val"
    ]
    adl_problem_solving_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_problem_solving_fim_start_val"]
    adl_problem_solving_fim_current_val: Optional[int] = PatientMasterSchema.model_fields[
        "adl_problem_solving_fim_current_val"
    ]
    adl_memory_fim_start_val: Optional[int] = PatientMasterSchema.model_fields["adl_memory_fim_start_val"]
    adl_memory_fim_current_val: Optional[int] = PatientMasterSchema.model_fields["adl_memory_fim_current_val"]


class PatientInfo_BasicMovements(BaseModel):
    """患者の基本動作に関する評価"""

    func_basic_rolling_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_rolling_chk"]
    func_basic_rolling_level: Optional[str] = Field(
        None, description="寝返りのレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。"
    )
    func_basic_rolling_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_rolling_independent_chk"]
    func_basic_rolling_partial_assistance_chk: Optional[bool] = Field(
        None, description="寝返り: 一部介助。'一部介助'や'軽介助'という記述があればtrueにしてください。"
    )
    func_basic_rolling_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_rolling_assistance_chk"]
    func_basic_rolling_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_rolling_not_performed_chk"
    ]
    func_basic_getting_up_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_getting_up_chk"]
    func_basic_getting_up_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_getting_up_independent_chk"
    ]
    func_basic_getting_up_partial_assistance_chk: Optional[bool] = Field(
        None, description="起き上がり: 一部介助。'一部介助'や'軽介助'という記述があればtrueにしてください。"
    )
    func_basic_getting_up_level: Optional[str] = Field(
        None, description="起き上がりのレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。"
    )
    func_basic_getting_up_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_getting_up_assistance_chk"
    ]
    func_basic_getting_up_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_getting_up_not_performed_chk"
    ]
    func_basic_standing_up_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_standing_up_chk"]
    func_basic_standing_up_level: Optional[str] = Field(
        None, description="立ち上がりのレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。"
    )
    func_basic_standing_up_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_standing_up_independent_chk"
    ]
    func_basic_standing_up_partial_assistance_chk: Optional[bool] = Field(
        None, description="立ち上がり: 一部介助。'一部介助'や'軽介助'という記述があればtrueにしてください。"
    )
    func_basic_standing_up_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_standing_up_assistance_chk"
    ]
    func_basic_standing_up_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_standing_up_not_performed_chk"
    ]
    func_basic_sitting_balance_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_sitting_balance_chk"]
    func_basic_sitting_balance_level: Optional[str] = Field(
        None, description="座位保持のレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。"
    )
    func_basic_sitting_balance_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_sitting_balance_independent_chk"
    ]
    func_basic_sitting_balance_partial_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_sitting_balance_partial_assistance_chk"
    ]
    func_basic_sitting_balance_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_sitting_balance_assistance_chk"
    ]
    func_basic_sitting_balance_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_sitting_balance_not_performed_chk"
    ]
    func_basic_standing_balance_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_standing_balance_chk"]
    func_basic_standing_balance_level: Optional[str] = Field(
        None, description="立位保持のレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。"
    )
    func_basic_standing_balance_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_standing_balance_independent_chk"
    ]
    func_basic_standing_balance_partial_assistance_chk: Optional[bool] = Field(
        None, description="立位保持: 一部介助。'一部介助'や'軽介助'という記述があればtrueにしてください。"
    )
    func_basic_standing_balance_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_standing_balance_assistance_chk"
    ]
    func_basic_standing_balance_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "func_basic_standing_balance_not_performed_chk"
    ]
    func_basic_other_chk: Optional[bool] = PatientMasterSchema.model_fields["func_basic_other_chk"]
    func_basic_other_txt: Optional[str] = PatientMasterSchema.model_fields["func_basic_other_txt"]


class PatientInfo_Goals(BaseModel):
    """患者の目標設定に関する情報"""

    # 1枚目
    goals_1_month_txt: Optional[str] = PatientMasterSchema.model_fields["goals_1_month_txt"]
    goals_at_discharge_txt: Optional[str] = PatientMasterSchema.model_fields["goals_at_discharge_txt"]
    goals_planned_hospitalization_period_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goals_planned_hospitalization_period_chk"
    ]
    goals_planned_hospitalization_period_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goals_planned_hospitalization_period_txt"
    ]
    goals_discharge_destination_chk: Optional[bool] = PatientMasterSchema.model_fields["goals_discharge_destination_chk"]
    goals_discharge_destination_txt: Optional[str] = PatientMasterSchema.model_fields["goals_discharge_destination_txt"]
    goals_long_term_care_needed_chk: Optional[bool] = PatientMasterSchema.model_fields["goals_long_term_care_needed_chk"]
    # 2枚目：参加
    goal_p_residence_slct: Optional[str] = Field(
        None, description="住居場所の選択肢。'home_detached', 'home_apartment', 'facility', 'other' のいずれか。"
    )
    goal_p_residence_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_residence_chk"]
    goal_p_residence_slct: Optional[str] = PatientMasterSchema.model_fields["goal_p_residence_slct"]
    goal_p_residence_other_txt: Optional[str] = PatientMasterSchema.model_fields["goal_p_residence_other_txt"]
    goal_p_return_to_work_status_slct: Optional[str] = Field(
        None, description="復職状況の選択肢。'current_job', 'reassignment', 'new_job', 'not_possible', 'other' のいずれか。"
    )
    goal_p_return_to_work_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_return_to_work_chk"]
    goal_p_return_to_work_status_slct: Optional[str] = PatientMasterSchema.model_fields["goal_p_return_to_work_status_slct"]
    goal_p_return_to_work_status_other_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_p_return_to_work_status_other_txt"
    ]
    goal_p_return_to_work_commute_change_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_p_return_to_work_commute_change_chk"
    ]
    goal_p_schooling_status_slct: Optional[str] = Field(
        None,
        description="就学状況の選択肢。'possible', 'needs_consideration', 'change_course', 'not_possible', 'other' のいずれか。",
    )
    goal_p_schooling_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_schooling_chk"]
    goal_p_schooling_status_possible_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_p_schooling_status_possible_chk"
    ]
    goal_p_schooling_status_needs_consideration_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_p_schooling_status_needs_consideration_chk"
    ]
    goal_p_schooling_status_change_course_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_p_schooling_status_change_course_chk"
    ]
    goal_p_schooling_status_not_possible_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_p_schooling_status_not_possible_chk"
    ]
    goal_p_schooling_status_other_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_schooling_status_other_chk"]
    goal_p_schooling_status_other_txt: Optional[str] = PatientMasterSchema.model_fields["goal_p_schooling_status_other_txt"]
    goal_p_schooling_destination_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_schooling_destination_chk"]
    goal_p_schooling_destination_txt: Optional[str] = PatientMasterSchema.model_fields["goal_p_schooling_destination_txt"]
    goal_p_schooling_commute_change_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_p_schooling_commute_change_chk"
    ]
    goal_p_schooling_commute_change_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_p_schooling_commute_change_txt"
    ]
    goal_p_household_role_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_household_role_chk"]
    goal_p_household_role_txt: Optional[str] = PatientMasterSchema.model_fields["goal_p_household_role_txt"]
    goal_p_social_activity_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_social_activity_chk"]
    goal_p_social_activity_txt: Optional[str] = PatientMasterSchema.model_fields["goal_p_social_activity_txt"]
    goal_p_hobby_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_p_hobby_chk"]
    goal_p_hobby_txt: Optional[str] = PatientMasterSchema.model_fields["goal_p_hobby_txt"]


class PatientInfo_Social(BaseModel):
    """患者の社会保障サービスに関する情報"""

    social_care_level_status_chk: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_status_chk"]
    social_care_level_applying_chk: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_applying_chk"]
    social_care_level_support_chk: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_support_chk"]
    social_care_level_support_num1_slct: Optional[bool] = PatientMasterSchema.model_fields[
        "social_care_level_support_num1_slct"
    ]
    social_care_level_support_num2_slct: Optional[bool] = PatientMasterSchema.model_fields[
        "social_care_level_support_num2_slct"
    ]
    social_care_level_care_slct: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_care_slct"]
    social_care_level_care_num1_slct: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_care_num1_slct"]
    social_care_level_care_num2_slct: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_care_num2_slct"]
    social_care_level_care_num3_slct: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_care_num3_slct"]
    social_care_level_care_num4_slct: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_care_num4_slct"]
    social_care_level_care_num5_slct: Optional[bool] = PatientMasterSchema.model_fields["social_care_level_care_num5_slct"]
    social_disability_certificate_physical_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "social_disability_certificate_physical_chk"
    ]
    social_disability_certificate_physical_txt: Optional[str] = PatientMasterSchema.model_fields[
        "social_disability_certificate_physical_txt"
    ]
    social_disability_certificate_physical_type_txt: Optional[str] = PatientMasterSchema.model_fields[
        "social_disability_certificate_physical_type_txt"
    ]
    social_disability_certificate_physical_rank_val: Optional[int] = PatientMasterSchema.model_fields[
        "social_disability_certificate_physical_rank_val"
    ]
    social_disability_certificate_mental_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "social_disability_certificate_mental_chk"
    ]
    social_disability_certificate_mental_rank_val: Optional[int] = PatientMasterSchema.model_fields[
        "social_disability_certificate_mental_rank_val"
    ]
    social_disability_certificate_intellectual_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "social_disability_certificate_intellectual_chk"
    ]
    social_disability_certificate_intellectual_txt: Optional[str] = PatientMasterSchema.model_fields[
        "social_disability_certificate_intellectual_txt"
    ]
    social_disability_certificate_intellectual_grade_txt: Optional[str] = PatientMasterSchema.model_fields[
        "social_disability_certificate_intellectual_grade_txt"
    ]
    social_disability_certificate_other_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "social_disability_certificate_other_chk"
    ]
    social_disability_certificate_other_txt: Optional[str] = PatientMasterSchema.model_fields[
        "social_disability_certificate_other_txt"
    ]


class PatientInfo_Nutrition(BaseModel):
    """患者の栄養状態に関する情報"""

    nutrition_height_chk: Optional[bool] = PatientMasterSchema.model_fields["nutrition_height_chk"]
    nutrition_height_val: Optional[float] = PatientMasterSchema.model_fields["nutrition_height_val"]
    nutrition_weight_chk: Optional[bool] = PatientMasterSchema.model_fields["nutrition_weight_chk"]
    nutrition_weight_val: Optional[float] = PatientMasterSchema.model_fields["nutrition_weight_val"]
    nutrition_bmi_chk: Optional[bool] = PatientMasterSchema.model_fields["nutrition_bmi_chk"]
    nutrition_bmi_val: Optional[float] = PatientMasterSchema.model_fields["nutrition_bmi_val"]
    nutrition_method_oral_chk: Optional[bool] = PatientMasterSchema.model_fields["nutrition_method_oral_chk"]
    nutrition_method_tube_chk: Optional[bool] = PatientMasterSchema.model_fields["nutrition_method_tube_chk"]
    nutrition_method_iv_chk: Optional[bool] = PatientMasterSchema.model_fields["nutrition_method_iv_chk"]
    nutrition_method_peg_chk: Optional[bool] = PatientMasterSchema.model_fields["nutrition_method_peg_chk"]
    nutrition_swallowing_diet_slct: Optional[str] = PatientMasterSchema.model_fields["nutrition_swallowing_diet_slct"]
    nutrition_swallowing_diet_code_txt: Optional[str] = PatientMasterSchema.model_fields["nutrition_swallowing_diet_code_txt"]
    nutrition_status_assessment_slct: Optional[str] = PatientMasterSchema.model_fields["nutrition_status_assessment_slct"]
    nutrition_required_energy_val: Optional[int] = PatientMasterSchema.model_fields["nutrition_required_energy_val"]
    nutrition_required_protein_val: Optional[int] = PatientMasterSchema.model_fields["nutrition_required_protein_val"]
    nutrition_total_intake_energy_val: Optional[int] = PatientMasterSchema.model_fields["nutrition_total_intake_energy_val"]
    nutrition_total_intake_protein_val: Optional[int] = PatientMasterSchema.model_fields["nutrition_total_intake_protein_val"]


class PatientInfo_Goal_Activity(BaseModel):
    """患者の活動目標に関する情報"""

    goal_a_bed_mobility_level: Optional[str] = Field(
        None, description="床上移動のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。"
    )
    goal_a_bed_mobility_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_bed_mobility_chk"]
    goal_a_bed_mobility_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_bed_mobility_independent_chk"
    ]
    goal_a_bed_mobility_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_bed_mobility_assistance_chk"]
    goal_a_bed_mobility_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_bed_mobility_not_performed_chk"
    ]
    goal_a_indoor_mobility_level: Optional[str] = Field(
        None, description="屋内移動のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。"
    )
    goal_a_indoor_mobility_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_indoor_mobility_chk"]
    goal_a_indoor_mobility_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_indoor_mobility_independent_chk"
    ]
    goal_a_indoor_mobility_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_indoor_mobility_assistance_chk"
    ]
    goal_a_indoor_mobility_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_indoor_mobility_not_performed_chk"
    ]
    goal_a_outdoor_mobility_level: Optional[str] = Field(
        None, description="屋外移動のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。"
    )
    goal_a_outdoor_mobility_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_outdoor_mobility_chk"]
    goal_a_outdoor_mobility_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_outdoor_mobility_independent_chk"
    ]
    goal_a_outdoor_mobility_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_outdoor_mobility_assistance_chk"
    ]
    goal_a_outdoor_mobility_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_outdoor_mobility_not_performed_chk"
    ]
    goal_a_driving_level: Optional[str] = Field(
        None, description="自動車運転のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。"
    )
    goal_a_driving_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_driving_chk"]
    goal_a_driving_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_driving_independent_chk"]
    goal_a_driving_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_driving_assistance_chk"]
    goal_a_driving_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_driving_not_performed_chk"]
    goal_a_transport_level: Optional[str] = Field(
        None, description="公共交通機関利用のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。"
    )
    goal_a_public_transport_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_public_transport_chk"]
    goal_a_public_transport_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_public_transport_independent_chk"
    ]
    goal_a_public_transport_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_public_transport_assistance_chk"
    ]
    goal_a_public_transport_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_public_transport_not_performed_chk"
    ]
    goal_a_toileting_level: Optional[str] = Field(
        None, description="排泄(移乗以外)のレベルを 'independent', 'assist' のいずれかで記述。"
    )
    goal_a_toileting_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_toileting_chk"]
    goal_a_toileting_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_toileting_independent_chk"]
    goal_a_toileting_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_toileting_assistance_chk"]
    goal_a_eating_level: Optional[str] = Field(
        None, description="食事のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。"
    )
    goal_a_eating_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_eating_chk"]
    goal_a_eating_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_eating_independent_chk"]
    goal_a_eating_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_eating_assistance_chk"]
    goal_a_eating_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_eating_not_performed_chk"]
    goal_a_grooming_level: Optional[str] = Field(None, description="整容のレベルを 'independent', 'assist' のいずれかで記述。")
    goal_a_grooming_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_grooming_chk"]
    goal_a_grooming_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_grooming_independent_chk"]
    goal_a_grooming_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_grooming_assistance_chk"]
    goal_a_dressing_level: Optional[str] = Field(None, description="更衣のレベルを 'independent', 'assist' のいずれかで記述。")
    goal_a_dressing_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_dressing_chk"]
    goal_a_dressing_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_dressing_independent_chk"]
    goal_a_dressing_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_dressing_assistance_chk"]
    goal_a_bathing_level: Optional[str] = Field(None, description="入浴のレベルを 'independent', 'assist' のいずれかで記述。")
    goal_a_bathing_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_bathing_chk"]
    goal_a_bathing_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_bathing_independent_chk"]
    goal_a_bathing_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_bathing_assistance_chk"]
    goal_a_housework_level: Optional[str] = Field(
        None, description="家事のレベルを 'all', 'partial', 'not_performed' のいずれかで記述。"
    )
    goal_a_housework_meal_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_housework_meal_chk"]
    goal_a_housework_meal_all_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_housework_meal_all_chk"]
    goal_a_housework_meal_not_performed_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_housework_meal_not_performed_chk"
    ]
    goal_a_housework_meal_partial_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_housework_meal_partial_chk"]
    goal_a_housework_meal_partial_txt: Optional[str] = PatientMasterSchema.model_fields["goal_a_housework_meal_partial_txt"]
    goal_a_writing_level: Optional[str] = Field(
        None, description="書字のレベルを 'independent', 'independent_after_hand_change', 'other' のいずれかで記述。"
    )
    goal_a_writing_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_writing_chk"]
    goal_a_writing_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_writing_independent_chk"]
    goal_a_writing_independent_after_hand_change_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_writing_independent_after_hand_change_chk"
    ]
    goal_a_writing_other_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_writing_other_chk"]
    goal_a_writing_other_txt: Optional[str] = PatientMasterSchema.model_fields["goal_a_writing_other_txt"]
    goal_a_ict_level: Optional[str] = Field(
        None, description="ICT機器利用のレベルを 'independent', 'assist' のいずれかで記述。"
    )
    goal_a_ict_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_ict_chk"]
    goal_a_ict_independent_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_ict_independent_chk"]
    goal_a_ict_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_ict_assistance_chk"]
    goal_a_communication_level: Optional[str] = Field(
        None, description="コミュニケーションのレベルを 'independent', 'assist' のいずれかで記述。"
    )
    goal_a_communication_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_a_communication_chk"]
    goal_a_communication_independent_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_communication_independent_chk"
    ]
    goal_a_communication_assistance_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_a_communication_assistance_chk"
    ]


class PatientInfo_Goal_Psychological(BaseModel):
    """患者の心理面に関する目標"""

    goal_s_psychological_support_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_psychological_support_chk"]
    goal_s_psychological_support_txt: Optional[str] = PatientMasterSchema.model_fields["goal_s_psychological_support_txt"]
    goal_s_disability_acceptance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_disability_acceptance_chk"]
    goal_s_disability_acceptance_txt: Optional[str] = PatientMasterSchema.model_fields["goal_s_disability_acceptance_txt"]
    goal_s_psychological_other_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_psychological_other_chk"]
    goal_s_psychological_other_txt: Optional[str] = PatientMasterSchema.model_fields["goal_s_psychological_other_txt"]


class PatientInfo_Goal_Environment(BaseModel):
    """患者の環境因子に関する目標"""

    goal_s_env_home_modification_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_env_home_modification_chk"]
    goal_s_env_home_modification_txt: Optional[str] = PatientMasterSchema.model_fields["goal_s_env_home_modification_txt"]
    goal_s_env_assistive_device_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_env_assistive_device_chk"]
    goal_s_env_assistive_device_txt: Optional[str] = PatientMasterSchema.model_fields["goal_s_env_assistive_device_txt"]
    goal_s_env_social_security_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_env_social_security_chk"]
    goal_s_env_social_security_physical_disability_cert_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_env_social_security_physical_disability_cert_chk"
    ]
    goal_s_env_social_security_disability_pension_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_env_social_security_disability_pension_chk"
    ]
    goal_s_env_social_security_intractable_disease_cert_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_env_social_security_intractable_disease_cert_chk"
    ]
    goal_s_env_social_security_other_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_env_social_security_other_chk"
    ]
    goal_s_env_social_security_other_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_s_env_social_security_other_txt"
    ]
    goal_s_env_care_insurance_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_env_care_insurance_chk"]
    goal_s_env_care_insurance_details_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_s_env_care_insurance_details_txt"
    ]
    goal_s_env_disability_welfare_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_env_disability_welfare_chk"]
    goal_s_env_disability_welfare_other_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_env_disability_welfare_other_chk"
    ]
    goal_s_env_other_chk: Optional[bool] = PatientMasterSchema.model_fields["goal_s_env_other_chk"]
    goal_s_env_other_txt: Optional[str] = PatientMasterSchema.model_fields["goal_s_env_other_txt"]


class PatientInfo_Goal_HumanFactors(BaseModel):
    """患者の人的因子（第三者の不利）に関する目標"""

    goal_s_3rd_party_main_caregiver_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_main_caregiver_chk"
    ]
    goal_s_3rd_party_main_caregiver_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_main_caregiver_txt"
    ]
    goal_s_3rd_party_family_structure_change_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_family_structure_change_chk"
    ]
    goal_s_3rd_party_family_structure_change_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_family_structure_change_txt"
    ]
    goal_s_3rd_party_household_role_change_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_household_role_change_chk"
    ]
    goal_s_3rd_party_household_role_change_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_household_role_change_txt"
    ]
    goal_s_3rd_party_family_activity_change_chk: Optional[bool] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_family_activity_change_chk"
    ]
    goal_s_3rd_party_family_activity_change_txt: Optional[str] = PatientMasterSchema.model_fields[
        "goal_s_3rd_party_family_activity_change_txt"
    ]


# 抽出処理を行うスキーマのリスト
PATIENT_INFO_EXTRACTION_GROUPS = [
    PatientInfo_Basic,
    PatientInfo_Function_General,
    PatientInfo_Function_Motor,
    PatientInfo_Function_Cognitive,
    PatientInfo_BasicMovements,
    PatientInfo_ADL,
    PatientInfo_Social,
    PatientInfo_Nutrition,
    PatientInfo_Goals,
    PatientInfo_Goal_Activity,
    PatientInfo_Goal_Psychological,
    PatientInfo_Goal_Environment,
    PatientInfo_Goal_HumanFactors,
    # 今後の拡張のために他のグループもここに追加可能
]


# SLMに項目ごとの逐次生成のための順序リスト
# 各要素は (フィールド名, それが含まれるPydanticクラス) のタプル
# このリストの順序が、AIが計画書を思考する順序を決定する
SEQUENTIAL_GENERATION_ORDER = [
    # ステップ1: 現状評価
    ('main_risks_txt', RisksAndPrecautions),
    ('main_contraindications_txt', RisksAndPrecautions),
    ('func_pain_txt', FunctionalLimitations),
    ('func_rom_limitation_txt', FunctionalLimitations),
    ('func_muscle_weakness_txt', FunctionalLimitations),
    ('func_swallowing_disorder_txt', FunctionalLimitations),
    ('func_behavioral_psychiatric_disorder_txt', FunctionalLimitations),
    ('func_nutritional_disorder_txt', FunctionalLimitations),
    ('func_excretory_disorder_txt', FunctionalLimitations),
    ('func_pressure_ulcer_txt', FunctionalLimitations),
    ('func_contracture_deformity_txt', FunctionalLimitations),
    ('func_motor_muscle_tone_abnormality_txt', FunctionalLimitations),
    ('func_disorientation_txt', FunctionalLimitations),
    ('func_memory_disorder_txt', FunctionalLimitations),
    
    # ステップ2: 目標設定
    ('goals_1_month_txt', Goals),
    ('goals_at_discharge_txt', Goals),
    
    # ステップ3: 包括的治療計画
    ('policy_treatment_txt', TreatmentPolicy),
    ('policy_content_txt', TreatmentPolicy),
    ('adl_equipment_and_assistance_details_txt', TreatmentPolicy),
    ('goal_a_action_plan_txt', ActionPlans),
    ('goal_s_env_action_plan_txt', ActionPlans),
    ('goal_p_action_plan_txt', ActionPlans),
    ('goal_s_psychological_action_plan_txt', ActionPlans),
    ('goal_s_3rd_party_action_plan_txt', ActionPlans),
]

# class PersonaStage1_BasicAndGeneralFunction(
#     PatientInfo_Basic,
#     PatientInfo_Function_General,
#     PatientInfo_Social,
#     PatientInfo_Nutrition
# ):
#     """ペルソナ生成ステージ1: 基本情報、全般的機能、社会情報、栄養"""
#     pass

# class PersonaStage2_DetailedFunction(
#     PatientInfo_Function_Motor,
#     PatientInfo_Function_Cognitive,
#     PatientInfo_BasicMovements
# ):
#     """ペルソナ生成ステージ2: 詳細な運動・認知機能、基本動作"""
#     pass

# class PersonaStage3_ADL(PatientInfo_ADL):
#     """ペルソナ生成ステージ3: ADL評価"""
#     pass

# class PersonaStage4_GoalsAndContext(
#     PatientInfo_Goals,
#     PatientInfo_Goal_Activity,
#     PatientInfo_Goal_Psychological,
#     PatientInfo_Goal_Environment,
#     PatientInfo_Goal_HumanFactors
# ):
#     """ペルソナ生成ステージ4: 目標設定と関連因子"""
#     pass

# # 新しい段階的生成のためのスキーマリスト
# PERSONA_GENERATION_STAGES = [
#     PersonaStage1_BasicAndGeneralFunction,
#     PersonaStage2_DetailedFunction,
#     PersonaStage3_ADL,
#     PersonaStage4_GoalsAndContext,
# ]
# schemas.py の末尾に追加
class PersonaStage_BasicAndSocial(PatientInfo_Basic, PatientInfo_Social): pass
class PersonaStage_GeneralFuncAndNutrition(PatientInfo_Function_General, PatientInfo_Nutrition): pass
class PersonaStage_MotorAndBasicMove(PatientInfo_Function_Motor, PatientInfo_BasicMovements): pass
class PersonaStage_Cognitive(PatientInfo_Function_Cognitive): pass # 単体
class PersonaStage_ADL(PatientInfo_ADL): pass # 単体
# --- PersonaStage_GoalsAndContext を分割 ---
class PersonaStage_Goals(PatientInfo_Goals): pass # 目標設定のみ
class PersonaStage_Goal_Activity(PatientInfo_Goal_Activity): pass # 活動目標のみ
class PersonaStage_Goal_ContextFactors(PatientInfo_Goal_Psychological, PatientInfo_Goal_Environment, PatientInfo_Goal_HumanFactors): pass # 残りの関連因子

# 新しい8段階のリスト
PERSONA_GENERATION_STAGES_8 = [
    PersonaStage_BasicAndSocial,
    PersonaStage_GeneralFuncAndNutrition,
    PersonaStage_MotorAndBasicMove,
    PersonaStage_Cognitive,
    PersonaStage_ADL,
    PersonaStage_Goals,              # 分割1
    PersonaStage_Goal_Activity,      # 分割2
    PersonaStage_Goal_ContextFactors, # 分割3
]