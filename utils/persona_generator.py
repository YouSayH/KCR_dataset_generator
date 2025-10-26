import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, Type # Type をインポート
from datetime import date
from google import genai
from google.genai import types # types をインポート
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable # エラーハンドリング用
import json
import time # sleep用にインポート

# schemas.py から PatientMasterSchema と分割スキーマ群をインポート
# from schemas import PatientMasterSchema, PATIENT_INFO_EXTRACTION_GROUPS
from schemas import (
    PatientMasterSchema, PERSONA_GENERATION_STAGES_7,
    PersonaStage_BasicAndSocial, PersonaStage_GeneralFuncAndNutrition, # ステージ1, 2用
    PersonaStage_Merged_2_MotorAndCognitive,                           # ステージ3用
    PersonaStage_ADL,                                                  # ステージ4用
    PersonaStage_Goals,                                                # ステージ5用 ★追加/確認★
    PersonaStage_Goal_Activity,                                        # ステージ6用 ★追加/確認★
    PersonaStage_Goal_ContextFactors                                   # ステージ7用
)

# --- 1. Pydanticによるペルソナのスキーマ定義 ---
# (PatientPersonaクラスの定義は変更なしのため省略)
class PatientPersona(BaseModel):
    """
    【最大限拡張版】リハビリテーション計画のシミュレーションに使用する、詳細な架空の患者ペルソナ。
    PatientMasterSchemaに基づき、患者の状態記述に関連するほぼ全ての項目を含む。
    このデータは、P2(LoRA)では入力として、P3(Parser)では出力として使用される。
    """
    # --- Patientモデル由来 ---
    name: Optional[str] = PatientMasterSchema.model_fields['name']
    age: Optional[int] = PatientMasterSchema.model_fields['age']
    gender: Optional[str] = Field(None, description="患者の性別。'男性'なら'男'、'女性'なら'女'と出力してください。") # PatientMasterSchemaにはないが基本情報として重要

    # --- RehabilitationPlanモデル由来 (PatientMasterSchemaから抜粋・調整) ---
    # 【1枚目】ヘッダー・基本情報 (一部)
    header_evaluation_date: Optional[date] = PatientMasterSchema.model_fields['header_evaluation_date']
    header_disease_name_txt: Optional[str] = PatientMasterSchema.model_fields['header_disease_name_txt']
    header_treatment_details_txt: Optional[str] = PatientMasterSchema.model_fields['header_treatment_details_txt']
    header_onset_date: Optional[date] = PatientMasterSchema.model_fields['header_onset_date']
    header_rehab_start_date: Optional[date] = PatientMasterSchema.model_fields['header_rehab_start_date']
    header_therapy_pt_chk: Optional[bool] = PatientMasterSchema.model_fields['header_therapy_pt_chk']
    header_therapy_ot_chk: Optional[bool] = PatientMasterSchema.model_fields['header_therapy_ot_chk']
    header_therapy_st_chk: Optional[bool] = PatientMasterSchema.model_fields['header_therapy_st_chk']
    main_comorbidities_txt: Optional[str] = PatientMasterSchema.model_fields['main_comorbidities_txt']
    # main_risks_txt, main_contraindications_txt は計画書生成(P2)の出力なのでペルソナには含めない

    # 【1枚目】心身機能・構造 (ほぼ全て)
    func_consciousness_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_consciousness_disorder_chk']
    func_consciousness_disorder_jcs_gcs_txt: Optional[str] = PatientMasterSchema.model_fields['func_consciousness_disorder_jcs_gcs_txt']
    func_respiratory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_respiratory_disorder_chk']
    func_respiratory_o2_therapy_chk: Optional[bool] = PatientMasterSchema.model_fields['func_respiratory_o2_therapy_chk']
    func_respiratory_o2_therapy_l_min_txt: Optional[str] = PatientMasterSchema.model_fields['func_respiratory_o2_therapy_l_min_txt']
    func_respiratory_tracheostomy_chk: Optional[bool] = PatientMasterSchema.model_fields['func_respiratory_tracheostomy_chk']
    func_respiratory_ventilator_chk: Optional[bool] = PatientMasterSchema.model_fields['func_respiratory_ventilator_chk']
    func_circulatory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_circulatory_disorder_chk']
    func_circulatory_ef_chk: Optional[bool] = PatientMasterSchema.model_fields['func_circulatory_ef_chk']
    func_circulatory_ef_val: Optional[int] = PatientMasterSchema.model_fields['func_circulatory_ef_val']
    func_circulatory_arrhythmia_chk: Optional[bool] = PatientMasterSchema.model_fields['func_circulatory_arrhythmia_chk']
    func_circulatory_arrhythmia_status_slct: Optional[str] = Field(None, description="不整脈の有無。'yes'または'no'のいずれか。") # PatientMasterSchemaから調整
    func_risk_factors_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_factors_chk']
    func_risk_hypertension_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_hypertension_chk']
    func_risk_dyslipidemia_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_dyslipidemia_chk']
    func_risk_diabetes_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_diabetes_chk']
    func_risk_smoking_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_smoking_chk']
    func_risk_obesity_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_obesity_chk']
    func_risk_hyperuricemia_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_hyperuricemia_chk']
    func_risk_ckd_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_ckd_chk']
    func_risk_family_history_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_family_history_chk']
    func_risk_angina_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_angina_chk']
    func_risk_omi_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_omi_chk']
    func_risk_other_chk: Optional[bool] = PatientMasterSchema.model_fields['func_risk_other_chk']
    func_risk_other_txt: Optional[str] = PatientMasterSchema.model_fields['func_risk_other_txt']
    func_swallowing_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_swallowing_disorder_chk']
    func_swallowing_disorder_txt: Optional[str] = PatientMasterSchema.model_fields['func_swallowing_disorder_txt']
    func_nutritional_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_nutritional_disorder_chk']
    func_nutritional_disorder_txt: Optional[str] = PatientMasterSchema.model_fields['func_nutritional_disorder_txt']
    func_excretory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_excretory_disorder_chk']
    func_excretory_disorder_txt: Optional[str] = PatientMasterSchema.model_fields['func_excretory_disorder_txt']
    func_pressure_ulcer_chk: Optional[bool] = PatientMasterSchema.model_fields['func_pressure_ulcer_chk']
    func_pressure_ulcer_txt: Optional[str] = PatientMasterSchema.model_fields['func_pressure_ulcer_txt']
    func_pain_chk: Optional[bool] = PatientMasterSchema.model_fields['func_pain_chk']
    func_pain_txt: Optional[str] = PatientMasterSchema.model_fields['func_pain_txt']
    func_other_chk: Optional[bool] = PatientMasterSchema.model_fields['func_other_chk']
    func_other_txt: Optional[str] = PatientMasterSchema.model_fields['func_other_txt']
    func_rom_limitation_chk: Optional[bool] = PatientMasterSchema.model_fields['func_rom_limitation_chk']
    func_rom_limitation_txt: Optional[str] = PatientMasterSchema.model_fields['func_rom_limitation_txt']
    func_contracture_deformity_chk: Optional[bool] = PatientMasterSchema.model_fields['func_contracture_deformity_chk']
    func_contracture_deformity_txt: Optional[str] = PatientMasterSchema.model_fields['func_contracture_deformity_txt']
    func_muscle_weakness_chk: Optional[bool] = PatientMasterSchema.model_fields['func_muscle_weakness_chk']
    func_muscle_weakness_txt: Optional[str] = PatientMasterSchema.model_fields['func_muscle_weakness_txt']
    func_motor_dysfunction_chk: Optional[bool] = PatientMasterSchema.model_fields['func_motor_dysfunction_chk']
    func_motor_paralysis_chk: Optional[bool] = PatientMasterSchema.model_fields['func_motor_paralysis_chk']
    func_motor_involuntary_movement_chk: Optional[bool] = PatientMasterSchema.model_fields['func_motor_involuntary_movement_chk']
    func_motor_ataxia_chk: Optional[bool] = PatientMasterSchema.model_fields['func_motor_ataxia_chk']
    func_motor_parkinsonism_chk: Optional[bool] = PatientMasterSchema.model_fields['func_motor_parkinsonism_chk']
    func_motor_muscle_tone_abnormality_chk: Optional[bool] = PatientMasterSchema.model_fields['func_motor_muscle_tone_abnormality_chk']
    func_motor_muscle_tone_abnormality_txt: Optional[str] = PatientMasterSchema.model_fields['func_motor_muscle_tone_abnormality_txt']
    func_sensory_dysfunction_chk: Optional[bool] = PatientMasterSchema.model_fields['func_sensory_dysfunction_chk']
    func_sensory_hearing_chk: Optional[bool] = PatientMasterSchema.model_fields['func_sensory_hearing_chk']
    func_sensory_vision_chk: Optional[bool] = PatientMasterSchema.model_fields['func_sensory_vision_chk']
    func_sensory_superficial_chk: Optional[bool] = PatientMasterSchema.model_fields['func_sensory_superficial_chk']
    func_sensory_deep_chk: Optional[bool] = PatientMasterSchema.model_fields['func_sensory_deep_chk']
    func_speech_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_speech_disorder_chk']
    func_speech_articulation_chk: Optional[bool] = PatientMasterSchema.model_fields['func_speech_articulation_chk']
    func_speech_aphasia_chk: Optional[bool] = PatientMasterSchema.model_fields['func_speech_aphasia_chk']
    func_speech_stuttering_chk: Optional[bool] = PatientMasterSchema.model_fields['func_speech_stuttering_chk']
    func_speech_other_chk: Optional[bool] = PatientMasterSchema.model_fields['func_speech_other_chk']
    func_speech_other_txt: Optional[str] = PatientMasterSchema.model_fields['func_speech_other_txt']
    func_higher_brain_dysfunction_chk: Optional[bool] = PatientMasterSchema.model_fields['func_higher_brain_dysfunction_chk']
    func_higher_brain_memory_chk: Optional[bool] = PatientMasterSchema.model_fields['func_higher_brain_memory_chk']
    func_higher_brain_attention_chk: Optional[bool] = PatientMasterSchema.model_fields['func_higher_brain_attention_chk']
    func_higher_brain_apraxia_chk: Optional[bool] = PatientMasterSchema.model_fields['func_higher_brain_apraxia_chk']
    func_higher_brain_agnosia_chk: Optional[bool] = PatientMasterSchema.model_fields['func_higher_brain_agnosia_chk']
    func_higher_brain_executive_chk: Optional[bool] = PatientMasterSchema.model_fields['func_higher_brain_executive_chk']
    func_behavioral_psychiatric_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_behavioral_psychiatric_disorder_chk']
    func_behavioral_psychiatric_disorder_txt: Optional[str] = PatientMasterSchema.model_fields['func_behavioral_psychiatric_disorder_txt']
    func_disorientation_chk: Optional[bool] = PatientMasterSchema.model_fields['func_disorientation_chk']
    func_disorientation_txt: Optional[str] = PatientMasterSchema.model_fields['func_disorientation_txt']
    func_memory_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_memory_disorder_chk']
    func_memory_disorder_txt: Optional[str] = PatientMasterSchema.model_fields['func_memory_disorder_txt']
    func_developmental_disorder_chk: Optional[bool] = PatientMasterSchema.model_fields['func_developmental_disorder_chk']
    func_developmental_asd_chk: Optional[bool] = PatientMasterSchema.model_fields['func_developmental_asd_chk']
    func_developmental_ld_chk: Optional[bool] = PatientMasterSchema.model_fields['func_developmental_ld_chk']
    func_developmental_adhd_chk: Optional[bool] = PatientMasterSchema.model_fields['func_developmental_adhd_chk']

    # 【1枚目】基本動作 (チェックとレベル)
    func_basic_rolling_chk: Optional[bool] = PatientMasterSchema.model_fields['func_basic_rolling_chk']
    func_basic_rolling_level: Optional[str] = Field(None, description="寝返りのレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから追加
    func_basic_getting_up_chk: Optional[bool] = PatientMasterSchema.model_fields['func_basic_getting_up_chk']
    func_basic_getting_up_level: Optional[str] = Field(None, description="起き上がりのレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから追加
    func_basic_standing_up_chk: Optional[bool] = PatientMasterSchema.model_fields['func_basic_standing_up_chk']
    func_basic_standing_up_level: Optional[str] = Field(None, description="立ち上がりのレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから追加
    func_basic_sitting_balance_chk: Optional[bool] = PatientMasterSchema.model_fields['func_basic_sitting_balance_chk']
    func_basic_sitting_balance_level: Optional[str] = Field(None, description="座位保持のレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから追加
    func_basic_standing_balance_chk: Optional[bool] = PatientMasterSchema.model_fields['func_basic_standing_balance_chk']
    func_basic_standing_balance_level: Optional[str] = Field(None, description="立位保持のレベルを 'independent', 'partial_assist', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから追加
    func_basic_other_chk: Optional[bool] = PatientMasterSchema.model_fields['func_basic_other_chk']
    func_basic_other_txt: Optional[str] = PatientMasterSchema.model_fields['func_basic_other_txt']

    # 【1枚目】ADL (FIM/BI 開始時・現在値)
    adl_eating_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_eating_fim_start_val']
    adl_eating_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_eating_fim_current_val']
    adl_eating_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_eating_bi_start_val']
    adl_eating_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_eating_bi_current_val']
    adl_grooming_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_grooming_fim_start_val']
    adl_grooming_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_grooming_fim_current_val']
    adl_grooming_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_grooming_bi_start_val']
    adl_grooming_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_grooming_bi_current_val']
    adl_bathing_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_bathing_fim_start_val']
    adl_bathing_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_bathing_fim_current_val']
    adl_bathing_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_bathing_bi_start_val']
    adl_bathing_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_bathing_bi_current_val']
    adl_dressing_upper_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_dressing_upper_fim_start_val']
    adl_dressing_upper_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_dressing_upper_fim_current_val']
    adl_dressing_lower_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_dressing_lower_fim_start_val']
    adl_dressing_lower_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_dressing_lower_fim_current_val']
    adl_dressing_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_dressing_bi_start_val']
    adl_dressing_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_dressing_bi_current_val']
    adl_toileting_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_toileting_fim_start_val']
    adl_toileting_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_toileting_fim_current_val']
    adl_toileting_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_toileting_bi_start_val']
    adl_toileting_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_toileting_bi_current_val']
    adl_bladder_management_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_bladder_management_fim_start_val']
    adl_bladder_management_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_bladder_management_fim_current_val']
    adl_bladder_management_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_bladder_management_bi_start_val']
    adl_bladder_management_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_bladder_management_bi_current_val']
    adl_bowel_management_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_bowel_management_fim_start_val']
    adl_bowel_management_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_bowel_management_fim_current_val']
    adl_bowel_management_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_bowel_management_bi_start_val']
    adl_bowel_management_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_bowel_management_bi_current_val']
    adl_transfer_bed_chair_wc_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_bed_chair_wc_fim_start_val']
    adl_transfer_bed_chair_wc_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_bed_chair_wc_fim_current_val']
    adl_transfer_toilet_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_toilet_fim_start_val']
    adl_transfer_toilet_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_toilet_fim_current_val']
    adl_transfer_tub_shower_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_tub_shower_fim_start_val']
    adl_transfer_tub_shower_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_tub_shower_fim_current_val']
    adl_transfer_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_bi_start_val']
    adl_transfer_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_transfer_bi_current_val']
    adl_locomotion_walk_walkingAids_wc_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_walk_walkingAids_wc_fim_start_val']
    adl_locomotion_walk_walkingAids_wc_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_walk_walkingAids_wc_fim_current_val']
    adl_locomotion_walk_walkingAids_wc_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_walk_walkingAids_wc_bi_start_val']
    adl_locomotion_walk_walkingAids_wc_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_walk_walkingAids_wc_bi_current_val']
    adl_locomotion_stairs_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_stairs_fim_start_val']
    adl_locomotion_stairs_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_stairs_fim_current_val']
    adl_locomotion_stairs_bi_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_stairs_bi_start_val']
    adl_locomotion_stairs_bi_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_locomotion_stairs_bi_current_val']
    adl_comprehension_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_comprehension_fim_start_val']
    adl_comprehension_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_comprehension_fim_current_val']
    adl_expression_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_expression_fim_start_val']
    adl_expression_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_expression_fim_current_val']
    adl_social_interaction_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_social_interaction_fim_start_val']
    adl_social_interaction_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_social_interaction_fim_current_val']
    adl_problem_solving_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_problem_solving_fim_start_val']
    adl_problem_solving_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_problem_solving_fim_current_val']
    adl_memory_fim_start_val: Optional[int] = PatientMasterSchema.model_fields['adl_memory_fim_start_val']
    adl_memory_fim_current_val: Optional[int] = PatientMasterSchema.model_fields['adl_memory_fim_current_val']
    # adl_equipment_and_assistance_details_txt はP2の出力なのでペルソナには含めない

    # 【1枚目】栄養
    nutrition_height_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_height_chk']
    nutrition_height_val: Optional[float] = PatientMasterSchema.model_fields['nutrition_height_val']
    nutrition_weight_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_weight_chk']
    nutrition_weight_val: Optional[float] = PatientMasterSchema.model_fields['nutrition_weight_val']
    nutrition_bmi_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_bmi_chk']
    nutrition_bmi_val: Optional[float] = PatientMasterSchema.model_fields['nutrition_bmi_val']
    nutrition_method_oral_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_oral_chk']
    nutrition_method_oral_meal_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_oral_meal_chk']
    nutrition_method_oral_supplement_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_oral_supplement_chk']
    nutrition_method_tube_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_tube_chk']
    nutrition_method_iv_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_iv_chk']
    nutrition_method_iv_peripheral_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_iv_peripheral_chk']
    nutrition_method_iv_central_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_iv_central_chk']
    nutrition_method_peg_chk: Optional[bool] = PatientMasterSchema.model_fields['nutrition_method_peg_chk']
    nutrition_swallowing_diet_slct: Optional[str] = Field(None, description="嚥下調整食の必要性。'None'(不要)または'True'(必要)のいずれか。") # PatientMasterSchemaから調整
    nutrition_swallowing_diet_code_txt: Optional[str] = PatientMasterSchema.model_fields['nutrition_swallowing_diet_code_txt']
    nutrition_status_assessment_slct: Optional[str] = Field(None, description="栄養状態の評価。'no_problem', 'malnutrition', 'malnutrition_risk', 'overnutrition', 'other' のいずれか。") # PatientMasterSchemaから調整
    nutrition_status_assessment_other_txt: Optional[str] = PatientMasterSchema.model_fields['nutrition_status_assessment_other_txt']
    nutrition_required_energy_val: Optional[int] = PatientMasterSchema.model_fields['nutrition_required_energy_val']
    nutrition_required_protein_val: Optional[int] = PatientMasterSchema.model_fields['nutrition_required_protein_val']
    nutrition_total_intake_energy_val: Optional[int] = PatientMasterSchema.model_fields['nutrition_total_intake_energy_val']
    nutrition_total_intake_protein_val: Optional[int] = PatientMasterSchema.model_fields['nutrition_total_intake_protein_val']

    # 【1枚目】社会保障サービス
    social_care_level_status_chk: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_status_chk']
    social_care_level_applying_chk: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_applying_chk']
    social_care_level_support_chk: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_support_chk']
    social_care_level_support_num1_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_support_num1_slct']
    social_care_level_support_num2_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_support_num2_slct']
    social_care_level_care_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_care_slct']
    social_care_level_care_num1_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_care_num1_slct']
    social_care_level_care_num2_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_care_num2_slct']
    social_care_level_care_num3_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_care_num3_slct']
    social_care_level_care_num4_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_care_num4_slct']
    social_care_level_care_num5_slct: Optional[bool] = PatientMasterSchema.model_fields['social_care_level_care_num5_slct']
    social_disability_certificate_physical_chk: Optional[bool] = PatientMasterSchema.model_fields['social_disability_certificate_physical_chk']
    social_disability_certificate_physical_txt: Optional[str] = PatientMasterSchema.model_fields['social_disability_certificate_physical_txt']
    social_disability_certificate_physical_type_txt: Optional[str] = PatientMasterSchema.model_fields['social_disability_certificate_physical_type_txt']
    social_disability_certificate_physical_rank_val: Optional[int] = PatientMasterSchema.model_fields['social_disability_certificate_physical_rank_val']
    social_disability_certificate_mental_chk: Optional[bool] = PatientMasterSchema.model_fields['social_disability_certificate_mental_chk']
    social_disability_certificate_mental_rank_val: Optional[int] = PatientMasterSchema.model_fields['social_disability_certificate_mental_rank_val']
    social_disability_certificate_intellectual_chk: Optional[bool] = PatientMasterSchema.model_fields['social_disability_certificate_intellectual_chk']
    social_disability_certificate_intellectual_txt: Optional[str] = PatientMasterSchema.model_fields['social_disability_certificate_intellectual_txt']
    social_disability_certificate_intellectual_grade_txt: Optional[str] = PatientMasterSchema.model_fields['social_disability_certificate_intellectual_grade_txt']
    social_disability_certificate_other_chk: Optional[bool] = PatientMasterSchema.model_fields['social_disability_certificate_other_chk']
    social_disability_certificate_other_txt: Optional[str] = PatientMasterSchema.model_fields['social_disability_certificate_other_txt']

    # 【1枚目】目標・方針 (一部) - ペルソナの背景情報として重要
    # goals_1_month_txt, goals_at_discharge_txt はP2の出力なのでペルソナには含めない
    goals_planned_hospitalization_period_chk: Optional[bool] = PatientMasterSchema.model_fields['goals_planned_hospitalization_period_chk']
    goals_planned_hospitalization_period_txt: Optional[str] = PatientMasterSchema.model_fields['goals_planned_hospitalization_period_txt']
    goals_discharge_destination_chk: Optional[bool] = PatientMasterSchema.model_fields['goals_discharge_destination_chk']
    goals_discharge_destination_txt: Optional[str] = PatientMasterSchema.model_fields['goals_discharge_destination_txt']
    goals_long_term_care_needed_chk: Optional[bool] = PatientMasterSchema.model_fields['goals_long_term_care_needed_chk']
    # policy_treatment_txt, policy_content_txt はP2の出力なのでペルソナには含めない

    # 【2枚目】目標(参加) - ペルソナの背景情報として重要
    goal_p_residence_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_residence_chk']
    goal_p_residence_slct: Optional[str] = Field(None, description="住居場所の選択肢。'home_detached', 'home_apartment', 'facility', 'other' のいずれか。") # PatientMasterSchemaから調整
    goal_p_residence_other_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_residence_other_txt']
    goal_p_return_to_work_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_return_to_work_chk']
    goal_p_return_to_work_status_slct: Optional[str] = Field(None, description="復職状況の選択肢。'current_job', 'reassignment', 'new_job', 'not_possible', 'other' のいずれか。") # PatientMasterSchemaから調整
    goal_p_return_to_work_status_other_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_return_to_work_status_other_txt']
    goal_p_return_to_work_commute_change_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_return_to_work_commute_change_chk']
    goal_p_schooling_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_schooling_chk']
    goal_p_schooling_status_slct: Optional[str] = Field(None, description="就学状況の選択肢。'possible', 'needs_consideration', 'change_course', 'not_possible', 'other' のいずれか。") # PatientMasterSchemaから調整
    goal_p_schooling_status_other_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_schooling_status_other_txt']
    goal_p_schooling_destination_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_schooling_destination_chk']
    goal_p_schooling_destination_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_schooling_destination_txt']
    goal_p_schooling_commute_change_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_schooling_commute_change_chk']
    goal_p_schooling_commute_change_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_schooling_commute_change_txt']
    goal_p_household_role_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_household_role_chk']
    goal_p_household_role_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_household_role_txt'] # 背景記述用
    goal_p_social_activity_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_social_activity_chk']
    goal_p_social_activity_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_social_activity_txt'] # 背景記述用
    goal_p_hobby_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_p_hobby_chk']
    goal_p_hobby_txt: Optional[str] = PatientMasterSchema.model_fields['goal_p_hobby_txt'] # 背景記述用

    # 【2枚目】目標(活動) - ペルソナのADL状況を示すために重要
    # goal_a_..._chk/_level 項目を追加
    goal_a_bed_mobility_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_bed_mobility_chk']
    goal_a_bed_mobility_level: Optional[str] = Field(None, description="目標とする床上移動のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_indoor_mobility_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_indoor_mobility_chk']
    goal_a_indoor_mobility_level: Optional[str] = Field(None, description="目標とする屋内移動のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_outdoor_mobility_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_outdoor_mobility_chk']
    goal_a_outdoor_mobility_level: Optional[str] = Field(None, description="目標とする屋外移動のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_driving_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_driving_chk']
    goal_a_driving_level: Optional[str] = Field(None, description="目標とする自動車運転のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_public_transport_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_public_transport_chk']
    goal_a_transport_level: Optional[str] = Field(None, description="目標とする公共交通機関利用のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_toileting_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_toileting_chk']
    goal_a_toileting_level: Optional[str] = Field(None, description="目標とする排泄(移乗以外)のレベルを 'independent', 'assist' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_eating_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_eating_chk']
    goal_a_eating_level: Optional[str] = Field(None, description="目標とする食事のレベルを 'independent', 'assist', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_grooming_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_grooming_chk']
    goal_a_grooming_level: Optional[str] = Field(None, description="目標とする整容のレベルを 'independent', 'assist' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_dressing_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_dressing_chk']
    goal_a_dressing_level: Optional[str] = Field(None, description="目標とする更衣のレベルを 'independent', 'assist' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_bathing_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_bathing_chk']
    goal_a_bathing_level: Optional[str] = Field(None, description="目標とする入浴のレベルを 'independent', 'assist' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_housework_meal_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_housework_meal_chk']
    goal_a_housework_level: Optional[str] = Field(None, description="目標とする家事のレベルを 'all', 'partial', 'not_performed' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_writing_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_writing_chk']
    goal_a_writing_level: Optional[str] = Field(None, description="目標とする書字のレベルを 'independent', 'independent_after_hand_change', 'other' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_ict_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_ict_chk']
    goal_a_ict_level: Optional[str] = Field(None, description="目標とするICT機器利用のレベルを 'independent', 'assist' のいずれかで記述。") # PatientMasterSchemaから調整
    goal_a_communication_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_a_communication_chk']
    goal_a_communication_level: Optional[str] = Field(None, description="目標とするコミュニケーションのレベルを 'independent', 'assist' のいずれかで記述。") # PatientMasterSchemaから調整

    # 【2枚目】対応を要する項目 (心理・環境・人的) - ペルソナの背景情報として重要
    goal_s_psychological_support_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_psychological_support_chk']
    goal_s_disability_acceptance_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_disability_acceptance_chk']
    goal_s_psychological_other_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_psychological_other_chk']
    goal_s_env_home_modification_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_env_home_modification_chk']
    goal_s_env_assistive_device_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_env_assistive_device_chk']
    goal_s_env_care_insurance_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_env_care_insurance_chk']
    goal_s_env_disability_welfare_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_env_disability_welfare_chk']
    goal_s_env_other_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_env_other_chk']
    goal_s_3rd_party_main_caregiver_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_3rd_party_main_caregiver_chk']
    goal_s_3rd_party_family_structure_change_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_3rd_party_family_structure_change_chk']
    goal_s_3rd_party_household_role_change_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_3rd_party_household_role_change_chk']
    goal_s_3rd_party_family_activity_change_chk: Optional[bool] = PatientMasterSchema.model_fields['goal_s_3rd_party_family_activity_change_chk']

    # 担当者からの所見 (これはペルソナの一部として有用)
    担当者からの所見: Optional[str] = Field("特になし", description="このペルソナを担当する架空のセラピストからの主観的な所見や注意点")

    # 注意: _action_plan_txt 系はP2(LoRA)の出力なのでペルソナには含めない

def _build_staged_persona_prompt(
    paper_theme: str,
    paper_content: str,
    group_schema: Type[BaseModel],
    generated_data_so_far: dict
) -> str:
    """段階的ペルソナ生成用のプロンプトを構築する"""

    # これまでに生成されたデータを簡潔なサマリーにする
    summary = json.dumps(generated_data_so_far, indent=2, ensure_ascii=False, default=str) if generated_data_so_far else "まだありません。"

    # 今回の生成対象スキーマをJSON形式の文字列としてプロンプトに含める
    schema_json = json.dumps(group_schema.model_json_schema(), indent=2, ensure_ascii=False)

    return f"""あなたは経験豊富な臨床家であり、脚本家でもあります。
以下の【関連論文の内容】とその【テーマ】、そして【これまでに生成されたペルソナ情報】を読み、**続きとなる**リアルな架空の患者プロフィールを創作してください。

今回のタスクでは、以下の【JSONスキーマ】で定義されている項目**のみ**を生成対象とします。
スキーマで定義されている全ての項目について、臨床的に妥当な値を創作または判断して埋めてください。特にブール型 (`_chk` で終わる項目など) は `true` か `false` を明確に設定してください。情報がない場合は `null` としてください。

【関連論文のテーマ】
{paper_theme}

【関連論文の内容】
{paper_content}

【これまでに生成されたペルソナ情報】
{summary}

【生成するプロファイルの要件】
- **臨床的整合性**: 論文のテーマや、既に生成されたペルソナ情報と矛盾しないように値を設定してください。
- **客観的データの創作**: 論文の内容や既存のペルソナ情報に基づき、臨床的に妥当な客観的データ（FIM点数、身長、体重など）を創作してください。
- **心身機能の具体化**: （もし今回のスキーマに含まれていれば）「心身機能・構造」の各項目（特にブール型の `_chk` 項目）について、最も可能性の高い状態を判断し、`true` または `false` を設定してください。関連する詳細記述 (`_txt` など) も適切に創作してください。
- **背景の具体化**: （もし今回のスキーマに含まれていれば）参加目標や趣味に関する項目 (`goal_p_..._txt`) には、その人らしさが伝わる背景（職業、家族構成、趣味）と、本人の具体的な希望・目標を文章で記述してください。
- **一貫性**: 今回生成する内容は、既に生成されたペルソナ情報と論理的に一貫している必要があります。（例：既に「麻痺あり」と生成されていれば、関連するADL項目（移動、更衣など）の点数は低くなるはずです）

【今回生成するJSONスキーマ】
{schema_json}

出力は、上記の【今回生成するJSONスキーマ】に厳密に従ってください。
"""


def generate_persona(paper_theme: str, paper_content: str, gemini_api_key: str) -> dict: # 戻り値を PatientPersona から dict に変更
    """
    【修正版】論文テーマと内容から、Geminiを使って患者ペルソナを段階的に生成する。
    """
    client = genai.Client(api_key=gemini_api_key)
    final_persona_data = {} # 最終的な結果を格納する辞書

    print("\n～～～ ペルソナ生成リクエスト（段階的生成 - 4段階） ～～～") # メッセージを修正
    print(f"テーマ: {paper_theme}")
    print(f"関連論文(冒頭):\n{paper_content[:300]}...")
    print("～～～～～～～～～～～～～～～～～～")

    # PATIENT_INFO_EXTRACTION_GROUPS の代わりに PERSONA_GENERATION_STAGES をループ
    for group_schema in PERSONA_GENERATION_STAGES_7:
        print(f"  -> ステージ '{group_schema.__name__}' の情報を生成中...")


        # プロンプトを構築
        prompt = _build_staged_persona_prompt(
            paper_theme=paper_theme,
            paper_content=paper_content[:10000], # トークン数制限を考慮
            group_schema=group_schema,
            generated_data_so_far=final_persona_data
        )

        # API呼び出し実行 (JSONモード)
        generation_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=group_schema,
            temperature=1.0 # 創造性と安定性のバランス
        )

        # APIリトライ処理
        max_retries = 3
        backoff_factor = 2
        response = None

        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite", # スキーマが少し大きくなったので Flash で試行継続
                    contents=prompt,
                    config=generation_config
                )
                break # 成功したらループを抜ける
            except (ResourceExhausted, ServiceUnavailable) as e:
                if attempt < max_retries - 1:
                    wait_time = backoff_factor * (2 ** attempt)
                    print(f"     [警告] APIレート制限またはサーバーエラー。{wait_time}秒後に再試行します... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"     [エラー] API呼び出しが{max_retries}回失敗しました。ステージ '{group_schema.__name__}' をスキップします。")
                    response = None # エラーが発生したことを示す
                    break # ループを抜ける
            except Exception as e: # その他の予期せぬエラー
                print(f"     [エラー] ステージ '{group_schema.__name__}' の生成中に予期せぬエラー: {e}")
                response = None
                break

        if response and response.parsed:
            try:
                # Pydanticオブジェクトを辞書に変換してマージ
                group_result = response.parsed.model_dump(mode='json')
                # 値がNoneのキーはマージしない
                final_persona_data.update({k: v for k, v in group_result.items() if v is not None})
                print(f"  -> ステージ '{group_schema.__name__}' 完了。")
            except Exception as parse_e:
                print(f"     [エラー] ステージ '{group_schema.__name__}' の結果パースまたはマージ中にエラー: {parse_e}")
        else:
            # response が None の場合 (APIエラー後) または response.parsed がない場合
            print(f"  -> ステージ '{group_schema.__name__}' の生成に失敗またはスキップされました。")


        # APIレート制限対策 (ステージ間の待機時間は少し長めにしても良いかもしれません)
        time.sleep(3) # 各ステージ生成後に待機
        
    if not final_persona_data:
        raise ValueError("ペルソナ生成に失敗しました: どのステージからも有効なデータが得られませんでした。")

    # PatientPersona スキーマのフィールド順序に従って辞書を再構築
    ordered_persona_data = {}
    # Pydantic V2以降の場合:
    for field_name in PatientPersona.model_fields.keys():
        if field_name in final_persona_data:
            ordered_persona_data[field_name] = final_persona_data[field_name]
        else:
            # スキーマにあって生成結果にない場合は None を設定 (任意)
            ordered_persona_data[field_name] = None
    # Pydantic V1の場合 (もしV1を使っている場合):
    # for field_name in PatientPersona.__fields__:
    #     if field_name in final_persona_data:
    #         ordered_persona_data[field_name] = final_persona_data[field_name]
    #     else:
    #         ordered_persona_data[field_name] = None

    # オプション: 最後に完全な PatientPersona スキーマで検証
    try:
        # 検証には順序付け前のデータではなく、再構築したデータを使う
        validated_persona = PatientPersona(**ordered_persona_data)
        # 検証済みのデータを最終結果とする (Pydanticオブジェクトではなく辞書として返す場合は .model_dump() を使う)
        final_ordered_dict = validated_persona.model_dump(mode='json', exclude_none=True) # exclude_none=True で None のキーを除外
        print("\n～～～ 全ステージの生成・結合・順序付け完了 ～～～")
    except Exception as validation_e:
        print(f"\n[警告] 最終的なペルソナデータの検証中にエラーが発生しました: {validation_e}")
        print("データは生成・順序付けされましたが、完全なスキーマに適合しない可能性があります。")
        # 検証に失敗した場合でも、順序付けされた辞書を返す
        final_ordered_dict = ordered_persona_data


    # 最終的に順序付けされた辞書を返す
    return final_ordered_dict

# 3. このファイル単体で動作確認するためのテストコード
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 `GEMINI_API_KEY` が設定されていません。")

    dummy_paper_content_1 = """
    若年アスリートの前十字靭帯（ACL）損傷は、スポーツ活動への復帰を目的としたリハビリテーションが不可欠である。
    多くの場合、自家腱（膝蓋腱または半腱様筋腱）を用いた再建術が行われる。
    術後のリハビリテーションは、可動域の回復、大腿四頭筋の筋力強化、および固有受容感覚の再教育が中心となる。
    スポーツ特有の動作（カッティング、ジャンプ）の訓練は、術後6ヶ月以降に段階的に導入される。
    心理的因子（再受傷への恐怖）が復帰の妨げとなることも報告されている。
    """

    try:
        print("【テストケース1】")
        # generate_persona の戻り値は辞書になった
        persona_dict = generate_persona(
            paper_theme="前十字靭帯(ACL)損傷 術後",
            paper_content=dummy_paper_content_1,
            gemini_api_key=api_key
        )
        print("\n～～～ 生成されたペルソナ（段階的生成・結合後） ～～～")
        # exclude_none=True 相当の処理は generate_persona 内のマージで行われている
        # default=str で date オブジェクトもシリアル化
        print(json.dumps(persona_dict, indent=2, ensure_ascii=False, default=str))

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")