import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from google import genai
import json
# schemas.py から PatientMasterSchema のフィールド定義を借用するためにインポート
from schemas import PatientMasterSchema

# --- 1. Pydanticによるペルソナのスキーマ定義 ---
# PatientMasterSchema をほぼそのまま流用し、PatientPersona とする
# (署名など、患者の状態記述に不要な項目は除外)

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

# 2. Geminiに投げるためのメタプロンプト (プロンプトは前回提案したものでOK)
PERSONA_GENERATION_PROMPT_TEMPLATE = """
あなたは経験豊富な臨床家であり、脚本家でもあります。
以下の【関連論文の内容】を読み、その内容に**最もふさわしい、臨床的にあり得るリアルな架空の患者プロフィール**を**1人分**創作してください。

このプロフィールは、リハビリテーション実施計画書（P2 LoRA）の**入力(Input)**データ、およびカルテ抽出（P3 Parser）の**出力(Output)**データとして使用されます。
そのため、必ず指定されたJSONスキーマに厳密に従い、**スキーマで定義されている全ての項目について、臨床的に妥当な値を創作または判断して埋めてください**。特にブール型 (`_chk` で終わる項目など) は `true` か `false` を明確に設定してください。情報がない場合は `null` としてください。

【関連論文のテーマ】
{paper_theme}

【関連論文の内容】
{paper_content}

【生成するプロファイルの要件】
- **臨床的整合性**: 論文のテーマ（疾患、術式、患者集団）と完全に一致する「算定病名」「年齢」「性別」を設定してください。
- **客観的データの創作**: 論文の内容とペルソナの背景に基づき、臨床的に妥当な「発症日・手術日」「リハ開始日」「FIM点数」「身長」「体重」などの客観的データを**創作**してください。
- **心身機能の具体化**: 「心身機能・構造」セクションの**各項目（特にブール型の `_chk` 項目）**について、論文内容や設定した基本情報（疾患、年齢など）から**最も可能性の高い状態**を判断し、`true` または `false` を設定してください。関連する詳細記述 (`_txt` など) も適切に創作してください。
- **背景の具体化**: 参加目標や趣味に関する項目 (`goal_p_..._txt`) には、その人らしさが伝わる背景（職業、家族構成、趣味）と、本人の具体的な希望・目標を**文章で**記述してください。
- **一貫性**: 「心身機能・構造」の記述（特に `true` にした項目）は、「ADL評価」のFIM/BIスコアや「基本動作」のレベルと論理的に一貫している必要があります。（例：麻痺の有無が `true` なら、関連するADL項目（移動、更衣など）の点数は低くなるはずです）

出力は、指定されたJSONスキーマ（`PatientPersona`）に厳密に従ってください。
"""

def generate_persona(paper_theme: str, paper_content: str, gemini_api_key: str) -> PatientPersona:
    """
    論文テーマと内容から、Geminiを使って【最大限拡張版】患者ペルソナを1つ生成する。
    """

    client = genai.Client(api_key=gemini_api_key)

    prompt = PERSONA_GENERATION_PROMPT_TEMPLATE.format(
            paper_theme=paper_theme,
            paper_content=paper_content # 論文内容を渡す
        )

    print("\n～～～ ペルソナ生成リクエスト（最大限拡張版） ～～～")
    print(f"テーマ: {paper_theme}")
    print(f"関連論文(冒頭):\n{paper_content[:300]}...")
    print("～～～～～～～～～～～～～～～～～～")

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", # スキーマが巨大なためProモデルが必須
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": PatientPersona, # ★最大限拡張されたスキーマを指定
            "temperature": 1.0 # 創造性と安定性のバランス
        },
    )

    if not hasattr(response, "parsed") or not response.parsed:
        # パース失敗時のデバッグ情報
        debug_info = {
            "message": "APIからパース可能な応答がありませんでした。",
            "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "N/A",
            "prompt_feedback": str(response.prompt_feedback),
            "response_text": response.text if hasattr(response, "text") else "N/A"
        }
        raise ValueError(f"ペルソナ生成に失敗しました: {json.dumps(debug_info, ensure_ascii=False)}")

    return response.parsed

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
        persona_1 = generate_persona(
            paper_theme="前十字靭帯(ACL)損傷 術後",
            paper_content=dummy_paper_content_1,
            gemini_api_key=api_key
        )
        print("\n～～～ 生成されたペルソナ（最大限拡張版） ～～～")
        # exclude_none=True で、値がNoneの項目はJSONに出力しない（見やすくするため）
        print(persona_1.model_dump_json(indent=2, ensure_ascii=False, by_alias=True, exclude_none=True))

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")