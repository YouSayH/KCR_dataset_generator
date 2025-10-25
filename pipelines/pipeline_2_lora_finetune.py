import os
import json
from google import genai
from datetime import date
from schemas import RehabPlanSchema # P2の「出力」スキーマ (英語キー)
# utils/persona_generator.py から PatientPersona (入力の型ヒント用) をインポート
from utils.persona_generator import PatientPersona 

# --- 日本語キー変換ロジック (gemini_client.py から移植・適合) ---

# DBカラム名と日本語名のマッピング
CELL_NAME_MAPPING = {
    "name": "氏名",
    "age": "年齢",
    "gender": "性別",
    "header_evaluation_date": "評価日",
    "header_disease_name_txt": "算定病名",
    "header_treatment_details_txt": "治療内容",
    "header_onset_date": "発症日・手術日",
    "header_rehab_start_date": "リハ開始日",
    "main_comorbidities_txt": "併存疾患・合併症",
    "header_therapy_pt_chk": "理学療法",
    "header_therapy_ot_chk": "作業療法",
    "header_therapy_st_chk": "言語聴覚療法",
    "func_consciousness_disorder_chk": "意識障害", "func_consciousness_disorder_jcs_gcs_txt": "意識障害(JCS/GCS)",
    "func_respiratory_disorder_chk": "呼吸機能障害", "func_respiratory_o2_therapy_chk": "酸素療法", "func_respiratory_o2_therapy_l_min_txt": "酸素流量(L/min)", "func_respiratory_tracheostomy_chk": "気管切開", "func_respiratory_ventilator_chk": "人工呼吸器",
    "func_circulatory_disorder_chk": "循環障害", "func_circulatory_ef_chk": "心駆出率(EF)測定", "func_circulatory_ef_val": "心駆出率(EF)の値(%)", "func_circulatory_arrhythmia_chk": "不整脈", "func_circulatory_arrhythmia_status_slct": "不整脈の状態",
    "func_risk_factors_chk": "危険因子", "func_risk_hypertension_chk": "高血圧症", "func_risk_dyslipidemia_chk": "脂質異常症", "func_risk_diabetes_chk": "糖尿病", "func_risk_smoking_chk": "喫煙", "func_risk_obesity_chk": "肥満", "func_risk_hyperuricemia_chk": "高尿酸血症", "func_risk_ckd_chk": "慢性腎臓病(CKD)", "func_risk_family_history_chk": "家族歴", "func_risk_angina_chk": "狭心症", "func_risk_omi_chk": "陳旧性心筋梗塞(OMI)", "func_risk_other_chk": "その他の危険因子", "func_risk_other_txt": "その他の危険因子の詳細",
    "func_swallowing_disorder_chk": "摂食嚥下障害", "func_swallowing_disorder_txt": "摂食嚥下障害の詳細",
    "func_nutritional_disorder_chk": "栄養障害", "func_nutritional_disorder_txt": "栄養障害の詳細",
    "func_excretory_disorder_chk": "排泄機能障害", "func_excretory_disorder_txt": "排泄機能障害の詳細",
    "func_pressure_ulcer_chk": "褥瘡", "func_pressure_ulcer_txt": "褥瘡の詳細",
    "func_pain_chk": "疼痛", "func_pain_txt": "疼痛の詳細",
    "func_other_chk": "その他の心身機能障害", "func_other_txt": "その他の心身機能障害の詳細",
    "func_rom_limitation_chk": "関節可動域制限", "func_rom_limitation_txt": "関節可動域制限の詳細",
    "func_contracture_deformity_chk": "拘縮・変形", "func_contracture_deformity_txt": "拘縮・変形の詳細",
    "func_muscle_weakness_chk": "筋力低下", "func_muscle_weakness_txt": "筋力低下の詳細",
    "func_motor_dysfunction_chk": "運動機能障害", "func_motor_paralysis_chk": "麻痺", "func_motor_involuntary_movement_chk": "不随意運動", "func_motor_ataxia_chk": "運動失調", "func_motor_parkinsonism_chk": "パーキンソニズム",
    "func_motor_muscle_tone_abnormality_chk": "筋緊張異常", "func_motor_muscle_tone_abnormality_txt": "筋緊張異常の詳細",
    "func_sensory_dysfunction_chk": "感覚機能障害", "func_sensory_hearing_chk": "聴覚障害", "func_sensory_vision_chk": "視覚障害", "func_sensory_superficial_chk": "表在感覚障害", "func_sensory_deep_chk": "深部感覚障害",
    "func_speech_disorder_chk": "音声発話障害", "func_speech_articulation_chk": "構音障害", "func_speech_aphasia_chk": "失語症", "func_speech_stuttering_chk": "吃音", "func_speech_other_chk": "その他の音声発話障害", "func_speech_other_txt": "その他の音声発話障害の詳細",
    "func_higher_brain_dysfunction_chk": "高次脳機能障害", "func_higher_brain_memory_chk": "記憶障害(高次脳)", "func_higher_brain_attention_chk": "注意障害", "func_higher_brain_apraxia_chk": "失行", "func_higher_brain_agnosia_chk": "失認", "func_higher_brain_executive_chk": "遂行機能障害",
    "func_behavioral_psychiatric_disorder_chk": "精神行動障害", "func_behavioral_psychiatric_disorder_txt": "精神行動障害の詳細",
    "func_disorientation_chk": "見当識障害", "func_disorientation_txt": "見当識障害の詳細",
    "func_memory_disorder_chk": "記憶障害", "func_memory_disorder_txt": "記憶障害の詳細",
    "func_developmental_disorder_chk": "発達障害", "func_developmental_asd_chk": "自閉症スペクトラム症(ASD)", "func_developmental_ld_chk": "学習障害(LD)", "func_developmental_adhd_chk": "注意欠陥多動性障害(ADHD)",
    "func_basic_rolling_chk": "寝返り動作の評価有無", "func_basic_rolling_level": "寝返りレベル",
    "func_basic_getting_up_chk": "起き上がり動作の評価有無", "func_basic_getting_up_level": "起き上がりレベル",
    "func_basic_standing_up_chk": "立ち上がり動作の評価有無", "func_basic_standing_up_level": "立ち上がりレベル",
    "func_basic_sitting_balance_chk": "座位保持の評価有無", "func_basic_sitting_balance_level": "座位保持レベル",
    "func_basic_standing_balance_chk": "立位保持の評価有無", "func_basic_standing_balance_level": "立位保持レベル",
    "func_basic_other_chk": "その他の基本動作の評価有無", "func_basic_other_txt": "その他の基本動作の詳細",
    "adl_eating_fim_start_val": "食事FIM(開始時)", "adl_eating_fim_current_val": "食事FIM(現在値)", "adl_eating_bi_start_val": "食事BI(開始時)", "adl_eating_bi_current_val": "食事BI(現在値)",
    "adl_grooming_fim_start_val": "整容FIM(開始時)", "adl_grooming_fim_current_val": "整容FIM(現在値)", "adl_grooming_bi_start_val": "整容BI(開始時)", "adl_grooming_bi_current_val": "整容BI(現在値)",
    "adl_bathing_fim_start_val": "入浴FIM(開始時)", "adl_bathing_fim_current_val": "入浴FIM(現在値)", "adl_bathing_bi_start_val": "入浴BI(開始時)", "adl_bathing_bi_current_val": "入浴BI(現在値)",
    "adl_dressing_upper_fim_start_val": "更衣(上半身)FIM(開始時)", "adl_dressing_upper_fim_current_val": "更衣(上半身)FIM(現在値)",
    "adl_dressing_lower_fim_start_val": "更衣(下半身)FIM(開始時)", "adl_dressing_lower_fim_current_val": "更衣(下半身)FIM(現在値)",
    "adl_dressing_bi_start_val": "更衣BI(開始時)", "adl_dressing_bi_current_val": "更衣BI(現在値)",
    "adl_toileting_fim_start_val": "トイレ動作FIM(開始時)", "adl_toileting_fim_current_val": "トイレ動作FIM(現在値)", "adl_toileting_bi_start_val": "トイレ動作BI(開始時)", "adl_toileting_bi_current_val": "トイレ動作BI(現在値)",
    "adl_bladder_management_fim_start_val": "排尿管理FIM(開始時)", "adl_bladder_management_fim_current_val": "排尿管理FIM(現在値)", "adl_bladder_management_bi_start_val": "排尿管理BI(開始時)", "adl_bladder_management_bi_current_val": "排尿管理BI(現在値)",
    "adl_bowel_management_fim_start_val": "排便管理FIM(開始時)", "adl_bowel_management_fim_current_val": "排便管理FIM(現在値)", "adl_bowel_management_bi_start_val": "排便管理BI(開始時)", "adl_bowel_management_bi_current_val": "排便管理BI(現在値)",
    "adl_transfer_bed_chair_wc_fim_start_val": "移乗(ベッド等)FIM(開始時)", "adl_transfer_bed_chair_wc_fim_current_val": "移乗(ベッド等)FIM(現在値)",
    "adl_transfer_toilet_fim_start_val": "移乗(トイレ)FIM(開始時)", "adl_transfer_toilet_fim_current_val": "移乗(トイレ)FIM(現在値)",
    "adl_transfer_tub_shower_fim_start_val": "移乗(浴槽等)FIM(開始時)", "adl_transfer_tub_shower_fim_current_val": "移乗(浴槽等)FIM(現在値)",
    "adl_transfer_bi_start_val": "移乗BI(開始時)", "adl_transfer_bi_current_val": "移乗BI(現在値)",
    "adl_locomotion_walk_walkingAids_wc_fim_start_val": "移動(歩行/車椅子)FIM(開始時)", "adl_locomotion_walk_walkingAids_wc_fim_current_val": "移動(歩行/車椅子)FIM(現在値)", "adl_locomotion_walk_walkingAids_wc_bi_start_val": "移動BI(開始時)", "adl_locomotion_walk_walkingAids_wc_bi_current_val": "移動BI(現在値)",
    "adl_locomotion_stairs_fim_start_val": "階段FIM(開始時)", "adl_locomotion_stairs_fim_current_val": "階段FIM(現在値)", "adl_locomotion_stairs_bi_start_val": "階段BI(開始時)", "adl_locomotion_stairs_bi_current_val": "階段BI(現在値)",
    "adl_comprehension_fim_start_val": "理解FIM(開始時)", "adl_comprehension_fim_current_val": "理解FIM(現在値)",
    "adl_expression_fim_start_val": "表出FIM(開始時)", "adl_expression_fim_current_val": "表出FIM(現在値)",
    "adl_social_interaction_fim_start_val": "社会的交流FIM(開始時)", "adl_social_interaction_fim_current_val": "社会的交流FIM(現在値)",
    "adl_problem_solving_fim_start_val": "問題解決FIM(開始時)", "adl_problem_solving_fim_current_val": "問題解決FIM(現在値)",
    "adl_memory_fim_start_val": "記憶FIM(開始時)", "adl_memory_fim_current_val": "記憶FIM(現在値)",
    "nutrition_height_chk": "身長測定", "nutrition_height_val": "身長(cm)",
    "nutrition_weight_chk": "体重測定", "nutrition_weight_val": "体重(kg)",
    "nutrition_bmi_chk": "BMI計算", "nutrition_bmi_val": "BMI",
    "nutrition_method_oral_chk": "栄養補給(経口)", "nutrition_method_oral_meal_chk": "経口栄養(食事)", "nutrition_method_oral_supplement_chk": "経口栄養(補助食品)",
    "nutrition_method_tube_chk": "経管栄養", "nutrition_method_iv_chk": "静脈栄養", "nutrition_method_iv_peripheral_chk": "末梢静脈栄養", "nutrition_method_iv_central_chk": "中心静脈栄養", "nutrition_method_peg_chk": "胃ろう",
    "nutrition_swallowing_diet_slct": "嚥下調整食の必要性", "nutrition_swallowing_diet_code_txt": "嚥下調整食コード",
    "nutrition_status_assessment_slct": "栄養状態評価", "nutrition_status_assessment_other_txt": "その他の栄養状態評価",
    "nutrition_required_energy_val": "必要熱量(kcal)", "nutrition_required_protein_val": "必要タンパク質量(g)",
    "nutrition_total_intake_energy_val": "総摂取熱量(kcal)", "nutrition_total_intake_protein_val": "総摂取タンパク質量(g)",
    "social_care_level_status_chk": "介護保険状況", "social_care_level_applying_chk": "介護保険(申請中)",
    "social_care_level_support_chk": "要支援認定", "social_care_level_support_num1_slct": "要支援1", "social_care_level_support_num2_slct": "要支援2",
    "social_care_level_care_slct": "要介護認定", "social_care_level_care_num1_slct": "要介護1", "social_care_level_care_num2_slct": "要介護2", "social_care_level_care_num3_slct": "要介護3", "social_care_level_care_num4_slct": "要介護4", "social_care_level_care_num5_slct": "要介護5",
    "social_disability_certificate_physical_chk": "身体障害者手帳", "social_disability_certificate_physical_txt": "身体障害者手帳(詳細)", "social_disability_certificate_physical_type_txt": "身体障害者手帳(種別)", "social_disability_certificate_physical_rank_val": "身体障害者手帳(等級)",
    "social_disability_certificate_mental_chk": "精神障害者保健福祉手帳", "social_disability_certificate_mental_rank_val": "精神障害者保健福祉手帳(等級)",
    "social_disability_certificate_intellectual_chk": "療育手帳", "social_disability_certificate_intellectual_txt": "療育手帳(詳細)", "social_disability_certificate_intellectual_grade_txt": "療育手帳(等級)",
    "social_disability_certificate_other_chk": "その他の手帳", "social_disability_certificate_other_txt": "その他の手帳(詳細)",
    "goals_planned_hospitalization_period_chk": "入院期間の予定有無", "goals_planned_hospitalization_period_txt": "入院期間の予定詳細",
    "goals_discharge_destination_chk": "退院先の予定有無", "goals_discharge_destination_txt": "退院先の予定詳細",
    "goals_long_term_care_needed_chk": "長期療養の必要性",
    "goal_p_residence_chk": "住居場所の目標有無", "goal_p_residence_slct": "住居場所の選択", "goal_p_residence_other_txt": "その他の住居場所",
    "goal_p_return_to_work_chk": "復職の目標有無", "goal_p_return_to_work_status_slct": "復職状況の選択", "goal_p_return_to_work_status_other_txt": "その他の復職状況", "goal_p_return_to_work_commute_change_chk": "通勤方法の変更有無",
    "goal_p_schooling_chk": "就学の目標有無", "goal_p_schooling_status_slct": "就学状況の選択", "goal_p_schooling_status_other_txt": "その他の就学状況",
    "goal_p_schooling_destination_chk": "就学先の有無", "goal_p_schooling_destination_txt": "就学先の詳細", "goal_p_schooling_commute_change_chk": "通学方法の変更有無", "goal_p_schooling_commute_change_txt": "通学方法の変更詳細",
    "goal_p_household_role_chk": "家庭内役割の目標有無", "goal_p_household_role_txt": "家庭内役割の詳細",
    "goal_p_social_activity_chk": "社会活動の目標有無", "goal_p_social_activity_txt": "社会活動の詳細",
    "goal_p_hobby_chk": "趣味の目標有無", "goal_p_hobby_txt": "趣味の詳細",
    "goal_a_bed_mobility_chk": "活動目標(床上移動)", "goal_a_bed_mobility_level": "活動目標(床上移動)レベル",
    "goal_a_indoor_mobility_chk": "活動目標(屋内移動)", "goal_a_indoor_mobility_level": "活動目標(屋内移動)レベル",
    "goal_a_outdoor_mobility_chk": "活動目標(屋外移動)", "goal_a_outdoor_mobility_level": "活動目標(屋外移動)レベル",
    "goal_a_driving_chk": "活動目標(自動車運転)", "goal_a_driving_level": "活動目標(自動車運転)レベル",
    "goal_a_public_transport_chk": "活動目標(公共交通機関)", "goal_a_transport_level": "活動目標(公共交通機関)レベル",
    "goal_a_toileting_chk": "活動目標(排泄)", "goal_a_toileting_level": "活動目標(排泄)レベル",
    "goal_a_eating_chk": "活動目標(食事)", "goal_a_eating_level": "活動目標(食事)レベル",
    "goal_a_grooming_chk": "活動目標(整容)", "goal_a_grooming_level": "活動目標(整容)レベル",
    "goal_a_dressing_chk": "活動目標(更衣)", "goal_a_dressing_level": "活動目標(更衣)レベル",
    "goal_a_bathing_chk": "活動目標(入浴)", "goal_a_bathing_level": "活動目標(入浴)レベル",
    "goal_a_housework_meal_chk": "活動目標(家事)", "goal_a_housework_level": "活動目標(家事)レベル",
    "goal_a_writing_chk": "活動目標(書字)", "goal_a_writing_level": "活動目標(書字)レベル",
    "goal_a_ict_chk": "活動目標(ICT機器)", "goal_a_ict_level": "活動目標(ICT機器)レベル",
    "goal_a_communication_chk": "活動目標(コミュニケーション)", "goal_a_communication_level": "活動目標(コミュニケーション)レベル",
    "goal_s_psychological_support_chk": "対応項目(心理的支援)",
    "goal_s_disability_acceptance_chk": "対応項目(障害受容)",
    "goal_s_psychological_other_chk": "対応項目(心理面その他)",
    "goal_s_env_home_modification_chk": "対応項目(住宅改修)",
    "goal_s_env_assistive_device_chk": "対応項目(補装具)",
    "goal_s_env_care_insurance_chk": "対応項目(介護保険)",
    "goal_s_env_disability_welfare_chk": "対応項目(障害福祉)",
    "goal_s_env_other_chk": "対応項目(環境因子その他)",
    "goal_s_3rd_party_main_caregiver_chk": "対応項目(主介護者)",
    "goal_s_3rd_party_family_structure_change_chk": "対応項目(家族構成変化)",
    "goal_s_3rd_party_household_role_change_chk": "対応項目(家庭内役割変化)",
    "goal_s_3rd_party_family_activity_change_chk": "対応項目(家族活動変化)",
    "担当者からの所見": "担当者からの所見" # PatientPersona に追加した項目
}

def _format_value_for_prompt(value):
    """プロンプト用に値を整形する (gemini_client.py の _format_value と同様)"""
    if value is None or value == "":
        return None # null値はプロンプトに含めない
    if isinstance(value, bool):
        return "あり" if value else "なし"
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return str(value)

def convert_persona_to_japanese_dict(persona_data: dict) -> dict:
    """
    PatientPersona の辞書（英語キー）を、gemini_client.py と同様の
    日本語キーのネストされた辞書に変換する。
    """
    facts = {
        "基本情報": {},
        "心身機能・構造": {},
        "基本動作": {},
        "ADL評価": {"FIM(開始時)": {}, "FIM(現在値)": {}, "BI(開始時)": {}, "BI(現在値)": {}},
        "栄養状態": {},
        "社会保障サービス": {},
        "生活状況・目標(本人・家族)": {},
        "担当者からの所見": "特になし",
    }

    for key, value in persona_data.items():
        formatted_value = _format_value_for_prompt(value)
        if formatted_value is None:
            continue
        
        jp_name = CELL_NAME_MAPPING.get(key)
        if not jp_name:
            continue # マッピングにないキーは無視

        # カテゴリ分け
        category = None
        if key in ["name", "age", "gender"] or key.startswith(("header_", "main_")):
             category = "基本情報"
        elif key.startswith("func_basic_"): 
            category = "基本動作"
        elif key.startswith("nutrition_"): 
            category = "栄養状態"
        elif key.startswith("social_"): 
            category = "社会保障サービス"
        elif key.startswith("goal_p_"): 
            category = "生活状況・目標(本人・家族)"
        elif key.startswith("func_"): 
            category = "心身機能・構造"
        elif key == "担当者からの所見":
            facts["担当者からの所見"] = formatted_value # カテゴリなしの特別扱い
            continue

        # ADL評価のカテゴリ分け
        elif key.startswith("adl_"):
            if "fim_start_val" in key:
                item_name = jp_name.replace("FIM(開始時)", "").strip()
                facts["ADL評価"]["FIM(開始時)"][item_name] = formatted_value
            elif "fim_current_val" in key:
                item_name = jp_name.replace("FIM(現在値)", "").strip()
                facts["ADL評価"]["FIM(現在値)"][item_name] = formatted_value
            elif "bi_start_val" in key:
                item_name = jp_name.replace("BI(開始時)", "").strip()
                facts["ADL評価"]["BI(開始時)"][item_name] = formatted_value
            elif "bi_current_val" in key:
                item_name = jp_name.replace("BI(現在値)", "").strip()
                facts["ADL評価"]["BI(現在値)"][item_name] = formatted_value
            continue # ADLは特別処理したので次へ

        if category:
            facts[category][jp_name] = formatted_value

    # 空のカテゴリやサブカテゴリを最終的に削除
    final_facts = {k: v for k, v in facts.items() if v} # 値が空のカテゴリを削除
    if "ADL評価" in final_facts:
        final_facts["ADL評価"] = {k: v for k, v in final_facts["ADL評価"].items() if v}
        if not final_facts["ADL評価"]:
            del final_facts["ADL評価"]
    
    return final_facts

# --- ここまで日本語キー変換ロジック ---


# プロンプトテンプレート
LORA_GENERATION_PROMPT_TEMPLATE = """
あなたは、LoRAファインチューニング用の高品質な教師データを作成する専門家です。
以下の【入力データ】（患者ペルソナと関連論文）を基に、**リハビリテーション実施計画書の全項目**を生成してください。
出力は、指定されたJSONスキーマに厳密に従ってください。

【入力データ】
{input_data_json}

【指示】
上記の入力データを基に、臨床的に妥当で、一貫性のあるリハビリテーション実施計画書（`RehabPlanSchema`）を完成させよ。
ペルソナの背景や希望、論文の知見を最大限に反映すること。
"""

def process_full_plan_generation(job_data: dict, gemini_api_key: str) -> dict:
    """
    【新版】リハビリ計画書（全項目）を一括生成する関数
    ペルソナの入力キーを日本語に変換する処理を含む
    """
    print(f"  [Pipeline 2] LoRAデータ生成ジョブ(一括)を開始: {job_data.get('job_id')}")
    client = genai.Client(api_key=gemini_api_key)

    # 1. 必要なファイルを読み込む
    source_markdown_path = os.path.join("output", "pipeline_1_rag_source", job_data['source_markdown'])
    persona_path = os.path.join("output", "pipeline_2_lora_finetune", "personas", job_data['source_persona'])
    
    try:
        with open(source_markdown_path, 'r', encoding='utf-8') as f:
            article_text = f.read()
        with open(persona_path, 'r', encoding='utf-8') as f:
            # persona_data は英語キーの辞書
            persona_data = json.load(f)
    except FileNotFoundError as e:
        print(f"    -> エラー: 必要なファイルが見つかりません。 {e}")
        raise
    except Exception as e:
        print(f"    -> エラー: ファイル読み込み中にエラー。 {e}")
        raise

    # 2. ★入力データ (ペルソナ) を日本語キーに変換★
    # PatientPersona モデル (英語キー) を gemini_client.py と同じ形式 (日本語キー) に変換
    patient_persona_jp = convert_persona_to_japanese_dict(persona_data)

    # 3. データセットの "input" 部分を作成
    # (実際のアプリケーションのプロンプト形式に合わせる)
    input_data_for_dataset = {
        "患者情報": patient_persona_jp,
        "関連論文": article_text[:10000], # RAGコンテキストとして論文を渡す（トークン数考慮）
    }
    input_data_json_string = json.dumps(input_data_for_dataset, ensure_ascii=False, indent=2)

    # 4. プロンプトの構築
    prompt = LORA_GENERATION_PROMPT_TEMPLATE.format(
        input_data_json=input_data_json_string,
    )
    
    print(f"    -> スキーマ 'RehabPlanSchema' に基づき全項目を一括生成します。")

    parsed_response = None 

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash-latest", # 全項目生成は高機能モデル推奨
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": RehabPlanSchema # ★計画書全体のスキーマ(英語キー)を指定
                }
        )

        if hasattr(response, 'parsed') and response.parsed:
            parsed_response = response.parsed
        
        elif hasattr(response, 'text') and response.text:
            print("    -> API応答の自動パースに失敗。手動でのJSONクリーンアップを試みます...")
            try:
                clean_text = response.text.strip().lstrip("```json").rstrip("```").strip()
                json_data = json.loads(clean_text)
                parsed_response = RehabPlanSchema(**json_data)
                print("    -> 手動クリーンアップ成功。")
            
            except Exception as parse_e:
                print(f"    -> 手動クリーンアップ失敗: {parse_e}")
                debug_info = {
                    "message": "APIからのパース可能な応答がありませんでした (手動パースも失敗)。",
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "N/A",
                    "response_text": response.text,
                    "manual_parse_error": str(parse_e)
                }
                raise ValueError(json.dumps(debug_info, ensure_ascii=False))
        
        if parsed_response is None:
            debug_info = {
                "message": "APIからパース可能な応答がありませんでした (応答テキストも空またはパース不能)。",
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "N/A",
                "prompt_feedback": str(response.prompt_feedback),
                "response_text": response.text if hasattr(response, 'text') else "N/A"
            }
            raise ValueError(json.dumps(debug_info, ensure_ascii=False))

    except Exception as e:
        print(f"    -> Gemini API呼び出し中にエラーが発生しました。詳細: {e}")
        raise e
    
    # 5. Alpaca形式のJSONLを作成
    alpaca_record = {
        "instruction": "患者ペルソナと関連論文に基づき、包括的なリハビリテーション実施計画書を生成せよ。",
        "input": input_data_for_dataset, # ★入力は「日本語キーのペルソナ」と「論文」★
        "output": parsed_response.model_dump() # ★出力は「英語キーの計画書項目」★
    }

    # 6. ハブ（run_dataset_generation）に結果を返す
    return {
        "content": json.dumps(alpaca_record, ensure_ascii=False, default=str), # default=str で date オブジェクトもシリアル化
        "extension": ".jsonl",
    }