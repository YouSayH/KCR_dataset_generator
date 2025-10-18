# import os
# import time
# import threading
# import re
# import json
# from flask import Flask, request, jsonify, render_template_string
# from dotenv import load_dotenv
# from core.job_manager import JobManager
# from core.result_handler import ResultHandler
# from schemas import SEQUENTIAL_GENERATION_ORDER
# from utils.jstage_client import JStageClient

# # .envファイルから環境変数を読み込む
# load_dotenv()
# RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
# PROCESSED_MARKDOWN_LOG = "output/processed_markdown.log"
# DEAD_LETTER_QUEUE_LOG = "output/logs/dead_letter_queue.jsonl"
# GENERATION_TARGETS = [
#     {"age_group": "70代", "gender": "女性"},
#     {"age_group": "70代", "gender": "男性"},
#     {"age_group": "70代", "gender": "女性"},
#     {"age_group": "70代", "gender": "男性"},
#     {"age_group": "60代", "gender": "女性"},
#     {"age_group": "60代", "gender": "男性"},
#     {"age_group": "60代", "gender": "女性"},
#     {"age_group": "60代", "gender": "男性"},
#     {"age_group": "80代", "gender": "女性"},
#     {"age_group": "80代", "gender": "男性"},
#     {"age_group": "80代", "gender": "女性"},
#     {"age_group": "80代", "gender": "男性"},
#     {"age_group": "10代", "gender": "女性"},
#     {"age_group": "10代", "gender": "男性"},
#     {"age_group": "20代", "gender": "女性"},
#     {"age_group": "20代", "gender": "男性"},
#     {"age_group": "30代", "gender": "女性"},
#     {"age_group": "30代", "gender": "男性"},
#     {"age_group": "40代", "gender": "女性"},
#     {"age_group": "40代", "gender": "男性"},
#     {"age_group": "50代", "gender": "女性"},
#     {"age_group": "50代", "gender": "男性"},
#     {"age_group": "90代", "gender": "女性"},
#     {"age_group": "90代", "gender": "男性"},
# ]
# PROCESSED_JSTAGE_LOG = "output/processed_jstage_dois.log" # 新しいログファイル
# SEARCH_KEYWORDS = ["変形性膝関節症 運動療法 効果"
#                    , "変形性股関節症 運動療法 システマティックレビュー"
#                    , "変形性膝関節症 保存療法 ガイドライン"
#                    ,"変形性股関節症 ADL指導"
#                    ,"手指変形性関節症 リハビリテーション"
#                    ,"変形性膝関節症 大腿四頭筋 筋力増強"
#                    ,"変形性股関節症 水中運動"
#                    ,"変形性膝関節症 バランス訓練"
#                    ,"人工膝関節置換術 TKA リハビリテーション プロトコル"
#                    ,"人工股関節置換術 THA 術後リハビリテーション"
#                    ,"人工膝関節置換術後 ADL 獲得"
#                    ,"人工股関節置換術後 脱臼予防"
#                    ,"TKA ROM制限 改善"
#                    ,"THA 術後歩行分析"
#                    ,"変形性膝関節症 疼痛管理 物理療法"
#                    ,"変形性股関節症 外転筋強化"
#                    ,"変形性膝関節症 足底板 効果"
#                    ,"変形性足関節症 リハビリテーション"
#                    ,"変形性肩関節症 運動療法"
#                    ,"人工関節置換術 術前リハビリテーション 効果"
#                    ,"変形性膝関節症 QOL評価 WOMAC"
#                    ,"慢性腰痛 運動療法 メタアナリシス"
#                    ,"椎間板ヘルニア 保存療法"
#                    ,"腰部脊柱管狭窄症 リハビリテーション"
#                    ,"頚椎症性神経根症 運動療法"
#                    ,"非特異的腰痛 コアトレーニング"
#                    ,"椎間板ヘルニア マッケンジー法"
#                    ,"脊椎すべり症 運動療法"
#                    ,"頚椎症性脊髄症 術後リハビリ"
#                    ,"脊椎圧迫骨折 リハビリテーション"
#                    ,"脊柱側弯症 運動療法 シュロス法"
#                    ,"腰椎分離症 リハビリテーション"
#                    ,"仙腸関節障害 評価 治療"
#                    ,"腰痛 腰椎安定化運動"
#                    ,"頚部痛 徒手療法"
#                    ,"脊椎固定術後 リハビリテーション"
#                     ,"腰痛 認知行動療法"
#                    ,"ぎっくり腰 急性腰痛 介入"
#                    ,"胸郭出口症候群 リハビリテーション"
#                    ,"腰痛 ガイドライン 比較"
#                    ,"脊髄損傷 運動器リハビリテーション"
#                    ,"腰痛 予後予測因子"
#                    ,"大腿骨頸部骨折 術後リハビリテーション"
#                    ,"橈骨遠位端骨折 リハビリテーション"
#                    ,"足関節骨折 術後 荷重時期"
#                    ,"上腕骨近位端骨折 保存療法"
#                    ,"鎖骨骨折 リハビリテーション"
#                    ,"骨盤骨折 リハビリテーション"
#                 ,"膝蓋骨骨折 術後ROM訓練"
#                    ,"中足骨骨折 荷重 プロトコル"
#                    ,"高齢者 骨折予防 運動"
#                    ,"大腿骨頸部骨折 早期離床 効果"
#                    ,"橈骨遠位端骨折 複合性局所疼痛症候群 CRPS 予防"
#                    ,"足関節骨折 固有受容性 感覚訓練"
#                    ,"上腕骨外科頸骨折 振り子運動"
#                    ,"脛骨高原骨折 リハビリテーション"
#                    ,"踵骨骨折 術後リハビリ"
#                    ,"肘頭骨折 リハビリテーション"
#                    ,"疲労骨折 リハビリテーション"
#                    ,"偽関節 治療 物理療法"
#                 ,"骨癒合遷延 リハビリテーション"
#                    ,"小児骨折 リハビリテーション"
#                    ,"骨粗鬆症性椎体骨折 体幹装具"
#                    ,"前十字靭帯損傷 ACL 術後リハビリテーション"
#                    ,"半月板損傷 術後 プロトコル"
#                    ,"腱板損傷 リハビリテーション"
#                    ,"アキレス腱断裂 術後リハビリ"
#                    ,"足関節捻挫 リハビリテーション"
#                    ,"肉離れ ハムストリングス リハビリテーション"
#                    ,"野球肘 投球障害肘 リハビリテーション"
#                    ,"テニス肘 外側上顆炎 運動療法"
#                    ,"シンスプリント 運動療法"
#                                       ,"膝蓋腱炎 ジャンパー膝 リハビリテーション"
#                    ,"肩関節脱臼 リハビリテーション"
#                    ,"グロインペイン 鼠径部痛 運動療法"
#                    ,"ACL損傷 予防トレーニング"
#                    ,"投球障害肩 リハビリテーション"
#                    ,"手首 TFCC損傷 保存療法"
#                    ,"オスグッド・シュラッター病 アスレティックリハビリテーション"
#                    ,"離断性骨軟骨炎 リハビリテーション"
#                    ,"スポーツ復帰基準 システマティックレビュー"
#                    ,"有痛性外脛骨 リハビリテーション"
#                    ,"脳震盪 スポーツ復帰 プロトコル"
#                    ,"肩関節周囲炎 五十肩 運動療法"
#                                       ,"ばね指 腱鞘炎 保存療法"
#                    ,"手根管症候群 リハビリテーション"
#                    ,"ドケルバン病 腱鞘炎 運動療法"
#                    ,"足底腱膜炎 運動療法"
#                    ,"腱板炎 棘上筋腱炎 運動療法"
#                    ,"アキレス腱炎 リハビリテーション"
#                    ,"鵞足炎 運動療法"
#                    ,"腸脛靭帯炎 ランナー膝 リハビリテーション"
#                    ,"モートン病 保存療法"
#                    ,"肩峰下インピンジメント症候群 運動療法"
#                    ,"SLAP損傷 リハビリテーション"
#                    ,"ベーカー嚢腫 運動療法"
#                                       ,"滑液包炎 リハビリテーション"
#                    ,"肘部管症候群 保存療法"
#                    ,"弾発股 リハビリテーション"
#                    ,"上腕二頭筋長頭腱炎 運動療法"
#                    ,"癒着性関節包炎 可動域訓練"
#                    ,"肉離れ RICE処置 エビデンス"
#                    ,"捻挫 靭帯損傷 POLICE処置"
#                    ,"軟部組織損傷 メカニカルストレス"
#                    ,"運動療法 筋力増強 エビデンス"
#                    ,"ストレッチング 効果 システマティックレビュー"
#                    ,"徒手療法 マニピュレーション 効果"
#                    ,"物理療法 電気刺激 TENS 効果"
#                                       ,"固有受容性神経筋促通法 PNF 効果"
#                    ,"水中運動療法 浮力 抵抗"
#                    ,"衝撃波治療 ESWT 腱板炎"
#                    ,"超音波療法 骨折治癒"
#                                       ,"牽引療法 頚椎症 効果"
#                    ,"テーピング 足関節捻挫 予防"
#                    ,"装具療法 膝OA 効果"
#                    ,"運動イメージ 脳卒中 運動器"
#                                       ,"バーチャルリアリティ VR リハビリテーション"
#                    ,"ウェアラブルデバイス 歩行分析"
#                    ,"再生医療 軟骨損傷 リハビリ"
#                    ,"体外衝撃波 足底腱膜炎"
#                                       ,"ハイボルテージ電気刺激 疼痛緩和"
#                    ,"筋膜リリース 効果"
#                    ,"マッサージ 筋疲労 回復"
#                    ,"バランストレーニング 高齢者 転倒予防"
#                                       ,"コアスタビリティ 腰痛予防"
#                    ,"クローズドカイネティックチェーン CKC 膝関節"
#                    ,"オープンカイネティックチェーン OKC"
#                    ,"プリオメトリクストレーニング スポーツ復帰"
#                                       ,"ファンクショナルトレーニング 高齢者"
#                    ,"間欠的免荷 トレッドミル 歩行練習"
#                    ,"バイオフィードバック 筋再教育"
#                    ,"多裂筋トレーニング 腰痛"
#                                       ,"インナーマッスル 肩関節 安定性"
#                    ,"赤外線療法 血行改善"
#                    ,"運動学習 リハビリテーション 応用"
#                    ,"デュアルタスクトレーニング 転倒予防"
#                                       ,"振動刺激トレーニング 筋力増強"
#                    ,"ノルディックハムストリングス 肉離れ予防"
#                    ,"認知行動療法 慢性疼痛"
#                    ,"ミラーセラピー 運動器疾患"
#                                       ,"治療的運動 連鎖"
#                    ,"遠隔リハビリテーション 効果"
#                    ,"超音波ガイド下 筋膜リリース"
#                    ,"低周波治療器 鎮痛メカニズム"
#                                       ,"モビライゼーション 関節可動域"
#                    ,"運動処方 FITT原則"
#                    ,"嫌気性運動 無酸素運動 リハビリ"
#                    ,"有酸素運動 運動器疾患 効果"
#                                       ,"レジスタンストレーニング 高齢者"
#                    ,"ホリスティックアプローチ リハビリテーション"
#                    ,"セルフ・エフィカシー 運動療法 継続"
#                    ,"関節可動域測定 ROM 信頼性"
#                                       ,"徒手筋力テスト MMT 妥当性"
#                    ,"歩行分析 3次元動作解析"
#                    ,"筋電図 EMG 表面筋電図 臨床応用"
#                    ,"疼痛評価 VAS NRS 信頼性"
#                                       ,"タイムアップアンドゴーテスト TUG 転倒予測"
#                    ,"6分間歩行テスト 6MWT 基準値"
#                    ,"SF-36 QOL評価 運動器疾患"
#                    ,"Functional Reach Test FRT 妥当性"
#                                       ,"Berg Balance Scale BBS 信頼性"
#                     ,"日本整形外科学会治療成績判定基準 JOAスコア"
#                    ,"超音波診断装置 運動器 評価"
#                    ,"姿勢評価 アライメント"
#                    ,"予後予測 運動器リハビリテーション"
#                    ,"運動器不安定症 診断基準"
#                    ,"サルコペニア 評価 介入"
#                    ,"フレイル 運動療法"
#                    ,"ロコモティブシンドローム 予防"
#                    ,"機能的自立度評価法 FIM 運動項目"
#                    ,"Patient-reported outcome PRO 運動器"
#                    ,"廃用症候群 リハビリテーション"
#                    ,"運動器検診 学校保健"
#                    ,"転倒予防 ガイドライン"
#                    ,"クリニカルパス 運動器疾患"
#                    ,"エビデンスに基づく理学療法 EBP"
#                    ,"産業理学療法 腰痛予防"
#                    ,"小児整形外科 リハビリテーション"
#                    ,"義肢 装具 リハビリテーション"
#                    ,"関節リウマチ 運動療法"
#                    ,"強直性脊椎炎 リハビリテーション"
#                    ,"線維筋痛症 運動療法"
#                    ,"痛みの神経科学教育 PNE"
#                    ,"運動恐怖感 評価 kinesiophobia"
#                    ,"リハビリテーション リスク管理"
#                    ,"運動連鎖 kinetic chain"
#                    ,"身体活動量 評価 加速度計"
#                    ,"運動機能障害 分類 ICF"
#                    ,"スクリーニングテスト FMS"
#                    ,"運動器超音波 エコー 評価"
#                    ,"片脚立位時間 バランス評価"
#                    ,"SPPB 高齢者機能評価"
#                    ,"エビデンスレベル ピラミッド"
#                    ,"臨床実践ガイドライン 運動器"
#                    ,"筋硬度 測定"
#                    ,"運動療法 中止基準"
#                    ,"リハビリテーションにおけるクリニカルリーズニング"
#                    ,"破局的思考 慢性疼痛"
#                    ,"運動器疾患 心理的要因"
#                    ,"運動器リハビリテーション 教育入院"
#                    ,"地域包括ケアシステム 運動器"
#                    ,"介護予防 運動プログラム"
#                    ,"脳卒中 片麻痺 運動器 リハビリテーション"
#                    ,"パーキンソン病 運動器症状 運動療法"
#                    ,"がんサバイバー 運動器機能障害 リハビリテーション"
#                    ,"呼吸器疾患 運動器併存 リハビリテーション"
#                    ,"糖尿病 足部病変 運動器 評価"
#                    ,"変形性膝関節症 リハビリテーション ガイドライン"
#                    ,"大腿骨頸部骨折 術後リハビリテーション クリニカルパス"
#                    ,"腰部脊柱管狭窄症 保存療法 エビデンス"
#                    ,"肩関節周囲炎（五十肩）病期別 運動療法"
#                    ,"前十字靭帯(ACL)再建術後 リハビリテーションプロトコル"
#                    ,"腱板断裂 保存療法 適応 基準"
#                    ,"腰椎椎間板ヘルニア 保存療法 リハビリテーション"
#                    ,"足関節捻挫 重症度別 リハビリテーション"
#                    ,"橈骨遠位端骨折 術後リハビリ"
#                    ,"脊椎圧迫骨折 リハビリテーション 禁忌"
#                    ,"人工股関節全置換術(THA) 術後リハビリテーション"
#                    ,"スポーツ傷害 予防プログラム システマティックレビュー"
#                    ,"慢性足関節不安定症 リハビリテーション"
#                    ,"アキレス腱断裂 保存療法 術後療法 比較"
#                    ,"上腕骨近位端骨折 リハビリテーション"
#                    ,"投球障害肩 リハビリテーション プログラム"
#                    ,"テニス肘（外側上顆炎）リハビリテーション"
#                    ,"手根管症候群 保存療法"
#                    ,"足底腱膜炎 リハビリテーション"
#                    ,"骨粗鬆症 運動療法 ガイドライン"
#                    ,"関節リウマチ 運動器リハビリテーション"
#                    ,"ハムストリングス肉離れ リハビリテーション"
#                    ,"シンスプリント（脛骨過労性骨膜炎）治療"
#                    ,"グロインペイン（鼠径部痛症候群）リハビリテーション"
#                    ,"関節可動域測定(ROM) 角度計 信頼性"
#                    ,"徒手筋力テスト(MMT) 検者間信頼性"
#                    ,"Timed Up and Go Test (TUG) カットオフ値 転倒予測"
#                    ,"6分間歩行試験 (6MWT) 健常値 基準値"
#                    ,"Berg Balance Scale (BBS) 妥当性"
#                    ,"Functional Reach Test (FRT) 測定方法"
#                    ,"Visual Analog Scale (VAS) 疼痛評価 信頼性"
#                    ,"日本整形外科学会 疾患別JOAスコア"
#                    ,"WOMAC 変形性関節症 評価"
#                    ,"DASH score 上肢機能評価"
#                    ,"SPPB (Short Physical Performance Battery) 高齢者機能評価"
#                    ,"筋硬度 測定 信頼性"
#                    ,"運動器不安定症 評価基準"
#                    ,"サルコペニア 評価基準 EWGSOP2"
#                    ,"フレイル 評価 CHS基準"
#                    ,"運動恐怖感 評価票 TSK"
#                    ,"疼痛破局的思考 評価 PCS"
#                    ,"歩行分析 3次元動作解析 臨床応用"
#                    ,"表面筋電図 筋活動 評価"
#                    ,"超音波診断装置 筋厚 評価"
#                    ,"評価バッテリー 膝関節疾患"
#                    ,"肩関節機能評価 スコア 比較"
#                    ,"股関節機能評価 HAGOS"
#                    ,"足部・足関節 機能評価 FAAM"
#                    ,"脊椎機能評価 Roland-Morris Disability Questionnaire"
#                    ,"片脚立位時間 バランス評価 基準値"
#                    ,"握力測定 臨床的意義"
#                    ,"身体組成計 InBody 筋量評価"
#                    ,"圧痛計 アルゴメーター 信頼性"
#                    ,"機能的動作スクリーニング FMS"
#                    ,"Hop test 膝機能評価"
#                    ,"臨床的に意味のある最小変化量 (MCID) TUG"
#                    ,"Patient-Reported Outcome Measures (PROMs) 運動器"
#                    ,"評価における天井効果 床効果"
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                 #    ,""
#                    ] # 検索キーワード
# SEARCH_INTERVAL_SECONDS = 3600 # 1時間に1回検索

# # アプリケーションの初期化
# app = Flask(__name__)
# job_manager = JobManager()
# result_handler = ResultHandler(base_output_dir="output")
# jstage_client = JStageClient()

# def jstage_search_monitor():
#     """
#     J-STAGE APIを定期的に検索し、新しい論文が見つかったら
#     パイプライン1のジョブを投入する。
#     """
#     print("[J-STAGE Monitor] 論文の自動検索を開始します...")
#     processed_dois = set()

#     try:
#         with open(PROCESSED_JSTAGE_LOG, 'r', encoding='utf-8') as f:
#             processed_dois = set(line.strip() for line in f)
#         print(f"[J-STAGE Monitor] {len(processed_dois)}件の処理済みDOIをログから読み込みました。")
#     except FileNotFoundError:
#         pass

#     while True:
#         print("\n" + "="*50)
#         print(f"[{time.ctime()}] 定期的な論文検索を実行します...")

#         for keyword in SEARCH_KEYWORDS:
#             articles = jstage_client.search_articles(keyword, count=20) # 各キーワードで最大20件

#             for article in articles:
#                 doi = article.get('doi')
#                 if doi not in processed_dois:
#                     print(f"[J-STAGE Monitor] 新規論文を発見: {article['title']}")

#                     job_data = {
#                         'pipeline': 'rag_source',
#                         'url': article['url'],
#                         'metadata': {
#                             'title': article['title'],
#                             'doi': article['doi']
#                         }
#                     }
#                     job_manager.add_job(job_data)

#                     processed_dois.add(doi)
#                     with open(PROCESSED_JSTAGE_LOG, 'a', encoding='utf-8') as f:
#                         f.write(doi + '\n')

#         print(f"[{time.ctime()}] 論文検索完了。次の検索まで {SEARCH_INTERVAL_SECONDS / 60:.0f} 分待機します。")
#         print("="*50 + "\n")
#         time.sleep(SEARCH_INTERVAL_SECONDS)

# # パイプライン2ジョブ生成ロジック
# def extract_theme_from_markdown(filepath: str) -> str:
#     """Markdownファイルからより賢くテーマを抽出する"""
#     try:
#         with open(filepath, "r", encoding="utf-8") as f:
#             content = f.read(2000)  # 検索範囲を調整

#         # YAMLフロントマターをスキップする
#         if content.startswith("---"):
#             end_marker = content.find("---", 3)
#             if end_marker != -1:
#                 content = content[end_marker + 3 :]

#         # H1見出し (#) を最優先で探す
#         h1_match = re.search(r"^#\s*(.*?)\n", content, re.MULTILINE)
#         if h1_match:
#             theme = h1_match.group(1).strip().replace("\n", " ")
#             if all(keyword not in theme for keyword in ["はじめに", "要旨", "おわりに"]):
#                 return theme

#         # H2見出し (##) を次に探す
#         h2_matches = re.findall(r"^##\s*(.*?)\n", content, re.MULTILINE)
#         for theme in h2_matches:
#             theme = theme.strip().replace("\n", " ")  # 改行をスペースに置換
#             if all(keyword not in theme for keyword in ["要旨", "はじめに", "おわりに", "まとめ", "結論"]):
#                 return theme

#     except Exception as e:
#         print(f"[ThemeExtractor] テーマ抽出中にエラー: {e}")

#     # 最終手段
#     return os.path.basename(os.path.splitext(filepath)[0])


# def markdown_folder_monitor():
#     """
#     RAGソースフォルダを監視し、新しいMarkdownファイルが見つかったら
#     ペルソナ生成ジョブを投入する。
#     """
#     print("[Monitor] Markdownフォルダの監視を開始します...")
#     processed_files = set()

#     # 過去に処理したファイルのログを読み込む
#     try:
#         with open(PROCESSED_MARKDOWN_LOG, "r", encoding="utf-8") as f:
#             processed_files = set(line.strip() for line in f)
#         print(f"[Monitor] {len(processed_files)}件の処理済みファイルをログから読み込みました。")
#     except FileNotFoundError:
#         pass

#     while True:
#         try:
#             if not os.path.exists(RAG_SOURCE_DIR):
#                 time.sleep(10)
#                 continue

#             for filename in os.listdir(RAG_SOURCE_DIR):
#                 if filename.endswith(".md") and filename not in processed_files:
#                     print(f"[Monitor] 新規Markdownファイルを検出: {filename}")
#                     filepath = os.path.join(RAG_SOURCE_DIR, filename)

#                     paper_theme = extract_theme_from_markdown(filepath)
#                     print(f"  -> 抽出されたテーマ: {paper_theme}")

#                     # 定義されたターゲットごとにペルソナ生成ジョブを作成
#                     for target in GENERATION_TARGETS:
#                         job_data = {
#                             "pipeline": "persona_generation",  # ★新しいパイプライン名
#                             "paper_theme": paper_theme,
#                             "age_group": target["age_group"],
#                             "gender": target["gender"],
#                             "source_markdown": filename,  # 元となったファイル名を記録
#                         }
#                         job_manager.add_job(job_data)

#                     # 処理済みとして記録
#                     processed_files.add(filename)
#                     with open(PROCESSED_MARKDOWN_LOG, "a", encoding="utf-8") as f:
#                         f.write(filename + "\n")

#         except Exception as e:
#             print(f"[Monitor] フォルダ監視中にエラーが発生しました: {e}")

#         time.sleep(30)  # 30秒ごとにチェック

# def get_failed_jobs():
#     """DLQログファイルを読み込み、失敗したジョブのリストを返す"""
#     failed_jobs = []
#     if not os.path.exists(DEAD_LETTER_QUEUE_LOG):
#         return failed_jobs

#     with open(DEAD_LETTER_QUEUE_LOG, 'r', encoding='utf-8') as f:
#         for line in f:
#             try:
#                 failed_jobs.append(json.loads(line))
#             except json.JSONDecodeError:
#                 print(f"警告: DLQログの不正な行をスキップします: {line}")

#     failed_jobs.reverse() # 新しいものを上に表示
#     return failed_jobs


# # APIエンドポイントの定義
# @app.route("/get-job", methods=["GET"])
# def get_job():
#     """ワーカーがジョブを取得するためのエンドポイント"""
#     worker_id = request.args.get("worker_id", "unknown_worker")
#     job = job_manager.get_job(worker_id)
#     if job:
#         return jsonify(job)
#     else:
#         # 未処理のジョブがない場合は、コンテンツなしを返す
#         return "", 204


# # 管理用UI
# @app.route("/", methods=["GET"])
# def dashboard():
#     """失敗ジョブ一覧と再実行機能を追加したダッシュボード"""
#     stats = job_manager.get_stats()
#     failed_jobs = get_failed_jobs()

#     html = """
#     <!Doctype html>
#     <html lang="ja">
#     <head>
#         <meta charset="utf-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <title>データセット生成ハブサーバー</title>
#         <style>
#             body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; padding: 0 20px; }
#             h1, h2 { color: #111; }
#             .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; }
#             .stat-card { background: #f9f9f9; border: 1px solid #ddd; padding: 20px; border-radius: 8px; text-align: center; }
#             .stat-card h3 { margin-top: 0; }
#             .stat-card .number { font-size: 2.5em; font-weight: bold; }
#             .progress-bar { background: #e0e0e0; border-radius: 5px; overflow: hidden; height: 25px; margin: 20px 0; }
#             .progress-bar-inner { height: 100%; background: #4caf50; transition: width 0.5s; text-align: center; color: white; line-height: 25px; }
#         </style>
#         <script>
#             setTimeout(() => { window.location.reload(); }, 10000); // 更新間隔を10秒に延長

#             function resubmitJob(jobContext) {
#                 if (!confirm('このジョブを再実行しますか？')) {
#                     return;
#                 }
#                 fetch('/resubmit-job', {
#                     method: 'POST',
#                     headers: { 'Content-Type': 'application/json' },
#                     body: JSON.stringify(jobContext)
#                 })
#                 .then(response => response.json())
#                 .then(data => {
#                     alert(data.message);
#                     window.location.reload();
#                 })
#                 .catch(error => {
#                     console.error('Error:', error);
#                     alert('再実行リクエストに失敗しました。');
#                 });
#             }
#         </script>
#     </head>
#     <body>
#         <h1>司令塔 (Hub) ダッシュボード</h1>
#         <p>このページは5秒ごとに自動更新されます。</p>

#         <h2>ジョブ進捗</h2>
#         <div class="stats">
#             <div class="stat-card"><h3>総ジョブ数</h3><div class="number">{{ stats.total }}</div></div>
#             <div class="stat-card" style="background:#fffbe6;"><h3>未処理</h3><div class="number">{{ stats.pending }}</div></div>
#             <div class="stat-card" style="background:#e3f2fd;"><h3>処理中</h3><div class="number">{{ stats.processing }}</div></div>
#             <div class="stat-card" style="background:#e8f5e9;"><h3>完了</h3><div class="number">{{ stats.completed }}</div></div>
#             <div class="stat-card" style="background:#ffebee;"><h3>失敗</h3><div class="number">{{ stats.failed }}</div></div>
#         </div>

#         {% if stats.total > 0 %}
#         <div class="progress-bar">
#             <div class="progress-bar-inner" style="width: {{ (stats.completed / stats.total) * 100 }}%;">
#                 {{ '%.1f'|format((stats.completed / stats.total) * 100) }}%
#             </div>
#         </div>
#         {% endif %}

#         <h2>失敗したジョブ (Dead Letter Queue)</h2>
#         {% if failed_jobs %}
#             <table>
#                 <thead>
#                     <tr>
#                         <th>発生日時</th>
#                         <th>パイプライン</th>
#                         <th>エラー内容</th>
#                         <th>アクション</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#                     {% for job in failed_jobs %}
#                     <tr>
#                         <td>{{ job.timestamp }}</td>
#                         <td>{{ job.pipeline_name }}</td>
#                         <td><pre class="error-message">{{ job.error_info.message | tojson(indent=2) }}</pre></td>
#                         <td>
#                             <button onclick='resubmitJob({{ job.job_context_for_resubmit | tojson }})'>再実行</button>
#                         </td>
#                     </tr>
#                     {% endfor %}
#                 </tbody>
#             </table>
#         {% else %}
#             <p>失敗したジョブはありません。</p>
#         {% endif %}
#     </body>
#     </html>
#     """
#     return render_template_string(html, stats=stats, failed_jobs=failed_jobs)


# @app.route('/resubmit-job', methods=['POST'])
# def resubmit_job():
#     """失敗したジョブのコンテキストを受け取り、再度キューに投入するAPI"""
#     job_context = request.json
#     if not job_context:
#         return jsonify({"message": "再実行するジョブのコンテキストがありません。"}), 400

#     new_job_id = job_manager.add_job(job_context)
#     message = f"ジョブを新しいID '{new_job_id}' で再投入しました。"
#     print(f"[Hub] {message}")

#     return jsonify({"message": message}), 200

# # @app.route("/submit-result", methods=["POST"])
# # def submit_result():
# #     submission = request.json
# #     job_id = submission.get("job_id")
# #     status = submission.get("status")
# #     pipeline = submission.get("pipeline")
# #     original_job_data = job_manager.jobs.get(job_id, {}).get("data", {})

# #     if not all([job_id, status, pipeline]):
# #         return jsonify({"error": "job_id, status, pipelineは必須です"}), 400

# #     if status == "completed":
# #         result = submission.get("result", {})
# #         # パイプライン2以降は、結果をファイルに保存するだけでなく、
# #         # 次のステップのジョブを生成する必要があるかもしれない（将来実装）
# #         saved_filename = f"{job_id}{result.get('extension', '.txt')}"
# #         result_handler.save_result(job_id, pipeline, result, custom_filename=saved_filename)
# #         job_manager.update_job_status(job_id, "completed")

# #         # ここからが重要
# #         # もし完了したのがペルソナ生成ジョブなら、次のLoRAデータ生成ジョブを作る
# #         if pipeline == "persona_generation":
# #             print(f"[Hub] ペルソナ生成完了({job_id})。次のLoRAデータ生成ジョブを作成します。")
# #             # 元のジョブ情報から、どの論文とペルソナを組み合わせるかを知る
# #             source_markdown = original_job_data.get("source_markdown")
# #             generated_persona_file = saved_filename

# #             if source_markdown and generated_persona_file:
# #                 # ここで仕様書通り、逐次生成のジョブを投入する
# #                 # まずは最初のステップ（CurrentAssessment）のジョブだけを投入
# #                 lora_job_data = {
# #                     "pipeline": "lora_data_generation",
# #                     "source_markdown": source_markdown,
# #                     "source_persona": generated_persona_file,
# #                     "target_step": 0,  # 生成グループのインデックス (0 = CurrentAssessment)
# #                     "previous_results": {},  # 最初のステップなので空
# #                 }
# #                 job_manager.add_job(lora_job_data)
# #             else:
# #                 print("[Hub] 警告: LoRAジョブの作成に必要な情報が不足しています。")

# #     elif status == "failed":
# #         error_info = submission.get("error", {})
# #         result_handler.save_error(job_id, pipeline, error_info)
# #         job_manager.update_job_status(job_id, "failed", message=error_info.get("message"))

# #     return jsonify({"message": "結果受理"}), 200


# @app.route('/submit-result', methods=['POST'])
# def submit_result():
#     submission = request.json
#     job_id = submission.get('job_id')
#     status = submission.get('status')
#     pipeline = submission.get('pipeline')
#     original_job_data = job_manager.jobs.get(job_id, {}).get('data', {})

#     if not all([job_id, status, pipeline]):
#         return jsonify({"error": "job_id, status, pipelineは必須です"}), 400

#     if status == 'completed':
#         result = submission.get('result', {})

#         custom_filename = None
#         if result.get('extension') != '.jsonl':
#              custom_filename = f"{job_id}{result.get('extension', '.txt')}"
#         result_handler.save_result(job_id, pipeline, result, custom_filename=custom_filename)

#         job_manager.update_job_status(job_id, 'completed')

#         if pipeline == 'persona_generation':
#             handle_persona_completion(original_job_data, custom_filename)

#         elif pipeline == 'lora_data_generation':
#             handle_lora_step_completion(original_job_data, result)


#     elif status == 'failed':
#         error_info = submission.get('error', {})
#         result_handler.save_error(job_id, pipeline, error_info, original_job_data)
#         job_manager.update_job_status(job_id, 'failed', message=error_info.get('message'))

#     return jsonify({"message": "結果受理"}), 200


# # def handle_persona_completion(original_job_data, saved_persona_filename):
# #     """ペルソナ生成が完了した後の処理"""
# #     print("[Hub] ペルソナ生成完了。LoRAデータ生成の最初のステップを開始します。")
# #     source_markdown = original_job_data.get("source_markdown")

# #     if source_markdown and saved_persona_filename:
# #         lora_job_data = {
# #             "pipeline": "lora_data_generation",
# #             "source_markdown": source_markdown,
# #             "source_persona": saved_persona_filename,
# #             "target_step": 0,
# #             "previous_results": {},
# #         }
# #         job_manager.add_job(lora_job_data)
# #     else:
# #         print("[Hub] 警告: LoRAジョブ作成に必要な情報が不足しています。")


# def handle_persona_completion(original_job_data, saved_persona_filename):
#     """ペルソナ生成が完了した後の処理"""
#     source_markdown = original_job_data.get('source_markdown')
#     if not source_markdown or not saved_persona_filename:
#         print(f"[Hub] 警告: 次のステップのジョブ作成に必要な情報が不足しています。")
#         return

#     # --- LoRAデータ生成の最初のステップ(0番目)を開始 ---
#     print(f"[Hub] ペルソナ生成完了。LoRAデータ生成の最初のステップを開始します。")
#     lora_job_data = {
#         'pipeline': 'lora_data_generation',
#         'source_markdown': source_markdown,
#         'source_persona': saved_persona_filename,
#         'target_step': 0, # 設計図の0番目からスタート
#         'previous_results': {},
#     }
#     job_manager.add_job(lora_job_data)

#     # --- 情報抽出(Parser)用データ生成ジョブも並行して開始 ---
#     print(f"[Hub] 同時に、情報抽出(Parser)用データ生成ジョブも開始します。")
#     parser_job_data = {
#         'pipeline': 'parser_finetune',
#         'source_markdown': source_markdown,
#         'source_persona': saved_persona_filename,
#     }
#     job_manager.add_job(parser_job_data)


# def handle_lora_step_completion(original_job_data, worker_result):
#     """【新版】LoRAデータ生成の1項目が完了した後の処理"""
#     next_step_data = worker_result.get('next_step_data', {})
#     next_step = next_step_data.get('next_step')

#     # 設計図(SEQUENTIAL_GENERATION_ORDER)の最後まで到達したかチェック
#     if next_step is not None and next_step < len(SEQUENTIAL_GENERATION_ORDER):
#         print(f"[Hub] LoRAステップ {next_step - 1} 完了。次のステップ {next_step} のジョブを作成します。")

#         # これまでの生成結果をすべて引き継ぐ
#         all_previous_results = original_job_data.get('previous_results', {})
#         newly_generated_items = next_step_data.get('generated_items', {})
#         all_previous_results.update(newly_generated_items)

#         # 次のステップのジョブを作成
#         next_lora_job_data = {
#             'pipeline': 'lora_data_generation',
#             'source_markdown': original_job_data.get('source_markdown'),
#             'source_persona': original_job_data.get('source_persona'),
#             'target_step': next_step,
#             'previous_results': all_previous_results,
#         }
#         job_manager.add_job(next_lora_job_data)
#     else:
#         # 全項目が完了
#         print(f"[Hub] ★★★ LoRA 全項目({len(SEQUENTIAL_GENERATION_ORDER)}件)の逐次生成が完了しました。 ★★★ (Source: {original_job_data.get('source_markdown')})")


# # サーバーの起動
# if __name__ == "__main__":
#     host = os.getenv("HUB_HOST", "127.0.0.1")
#     port = int(os.getenv("HUB_PORT", 5000))

#     # フォルダ監視スレッドをバックグラウンドで開始
#     md_monitor = threading.Thread(target=markdown_folder_monitor, daemon=True)
#     md_monitor.start()

#     jstage_monitor = threading.Thread(target=jstage_search_monitor, daemon=True)
#     jstage_monitor.start()

#     app.run(host=host, port=port, debug=False)


import os
import time
import threading
import re
import json
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from dotenv import load_dotenv
from collections import defaultdict

# プロジェクトのコアファイルからのインポート
from core.job_manager import JobManager
from core.result_handler import ResultHandler
from schemas import SEQUENTIAL_GENERATION_ORDER
from utils.jstage_client import JStageClient

# .envファイルから環境変数を読み込む
load_dotenv()

# --- 定数と設定 ---
RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
PROCESSED_MARKDOWN_LOG = "output/processed_markdown.log"
DEAD_LETTER_QUEUE_LOG = "output/logs/dead_letter_queue.jsonl"
PROCESSED_JSTAGE_LOG = "output/processed_jstage_dois.log"
SEARCH_INTERVAL_SECONDS = 3600

GENERATION_TARGETS = [
    {"age_group": "70代", "gender": "女性"},
    {"age_group": "70代", "gender": "男性"},
    {"age_group": "60代", "gender": "女性"},
    {"age_group": "60代", "gender": "男性"},
    {"age_group": "80代", "gender": "女性"},
    {"age_group": "80代", "gender": "男性"},
    {"age_group": "10代", "gender": "女性"},
    {"age_group": "10代", "gender": "男性"},
    {"age_group": "20代", "gender": "女性"},
    {"age_group": "20代", "gender": "男性"},
    {"age_group": "30代", "gender": "女性"},
    {"age_group": "30代", "gender": "男性"},
    {"age_group": "40代", "gender": "女性"},
    {"age_group": "40代", "gender": "男性"},
    {"age_group": "50代", "gender": "女性"},
    {"age_group": "50代", "gender": "男性"},
    {"age_group": "90代", "gender": "女性"},
    {"age_group": "90代", "gender": "男性"},
]
SEARCH_KEYWORDS = [
    "変形性膝関節症 運動療法 効果",
    "変形性股関節症 運動療法 システマティックレビュー",
    "人工膝関節置換術 TKA リハビリテーション プロトコル",
    "大腿骨頸部骨折 術後リハビリテーション",
]

# --- アプリケーションの初期化 ---
app = Flask(__name__)
job_manager = JobManager()
result_handler = ResultHandler(base_output_dir="output")
jstage_client = JStageClient()


# --- バックグラウンド処理 ---
def jstage_search_monitor():
    print("[J-STAGE Monitor] 論文の自動検索を開始します...")
    processed_dois = set()
    try:
        with open(PROCESSED_JSTAGE_LOG, "r", encoding="utf-8") as f:
            processed_dois = set(line.strip() for line in f)
        print(f"[J-STAGE Monitor] {len(processed_dois)}件の処理済みDOIをログから読み込みました。")
    except FileNotFoundError:
        pass
    while True:
        print(f"\n[{time.ctime()}] 定期的な論文検索を実行します...")
        for keyword in SEARCH_KEYWORDS:
            articles = jstage_client.search_articles(keyword, count=10)
            for article in articles:
                doi = article.get("doi")
                if doi and doi not in processed_dois:
                    print(f"[J-STAGE Monitor] 新規論文を発見: {article['title']}")
                    job_data = {
                        "pipeline": "rag_source",
                        "url": article["url"],
                        "metadata": {"title": article["title"], "doi": article["doi"]},
                    }
                    job_manager.add_job(job_data)
                    processed_dois.add(doi)
                    with open(PROCESSED_JSTAGE_LOG, "a", encoding="utf-8") as f:
                        f.write(doi + "\n")
        print(f"[{time.ctime()}] 論文検索完了。次の検索まで {SEARCH_INTERVAL_SECONDS / 60:.0f} 分待機します。")
        time.sleep(SEARCH_INTERVAL_SECONDS)


def markdown_folder_monitor():
    print("[Monitor] Markdownフォルダの監視を開始します...")
    processed_files = set()
    try:
        with open(PROCESSED_MARKDOWN_LOG, "r", encoding="utf-8") as f:
            processed_files = set(line.strip() for line in f)
        print(f"[Monitor] {len(processed_files)}件の処理済みファイルをログから読み込みました。")
    except FileNotFoundError:
        pass
    while True:
        try:
            if os.path.exists(RAG_SOURCE_DIR):
                for filename in os.listdir(RAG_SOURCE_DIR):
                    if filename.endswith(".md") and filename not in processed_files:
                        print(f"[Monitor] 新規Markdownファイルを検出: {filename}")
                        processed_files.add(filename)
                        with open(PROCESSED_MARKDOWN_LOG, "a", encoding="utf-8") as f:
                            f.write(filename + "\n")
        except Exception as e:
            print(f"[Monitor] フォルダ監視中にエラー: {e}")
        time.sleep(30)


# --- Web UIおよび進捗管理ロジック ---
def get_failed_jobs():
    failed_jobs = []
    if os.path.exists(DEAD_LETTER_QUEUE_LOG):
        with open(DEAD_LETTER_QUEUE_LOG, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    failed_jobs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return sorted(failed_jobs, key=lambda x: x.get("timestamp", ""), reverse=True)


def get_progress_matrix():
    with job_manager._lock:
        matrix = defaultdict(lambda: defaultdict(dict))
        for job_id, job in job_manager.jobs.items():
            data = job.get("data", {})
            pipeline = data.get("pipeline")
            md_file = data.get("source_markdown")
            if not md_file:
                continue

            age, gender = data.get("age_group"), data.get("gender")
            persona_key = f"{age}_{gender}"

            # persona_generation, lora_chain_generation, parser_finetune のステータスを登録
            if pipeline == "persona_generation":
                matrix[md_file][persona_key]["P"] = job["status"]
            elif pipeline == "lora_chain_generation":
                matrix[md_file][persona_key]["L"] = job["status"]
            elif pipeline == "parser_finetune":
                matrix[md_file][persona_key]["A"] = job["status"]

    sorted_matrix = dict(sorted(matrix.items()))
    persona_keys = sorted(list(set(key for paper in matrix.values() for key in paper.keys())))
    return sorted_matrix, persona_keys


# --- APIエンドポイント ---
@app.route("/assets/manifest", methods=["GET"])
def get_assets_manifest():
    rag_files = [f for f in os.listdir(RAG_SOURCE_DIR) if f.endswith(".md")] if os.path.exists(RAG_SOURCE_DIR) else []
    return jsonify({"rag_source_files": rag_files, "generation_targets": GENERATION_TARGETS})


@app.route("/assets/file/<path:filename>", methods=["GET"])
def get_asset_file(filename):
    return send_from_directory(RAG_SOURCE_DIR, filename, as_attachment=True)


@app.route("/get-job", methods=["GET"])
def get_job():
    job = job_manager.get_job(request.args.get("worker_id", "unknown"))
    return jsonify(job) if job else ("", 204)


@app.route("/submit-result", methods=["POST"])
def submit_result():
    submission = request.json
    job_id, status, pipeline = submission.get("job_id"), submission.get("status"), submission.get("pipeline")
    original_job_data = submission.get("original_job_data", {})

    if not all([job_id, status, pipeline]):
        return jsonify({"error": "job_id, status, pipelineは必須です"}), 400

    if job_id not in job_manager.jobs:
        job_manager.add_job_with_id(job_id, original_job_data)

    if status == "completed":
        result = submission.get("result", {})
        custom_filename = f"{job_id}{result.get('extension', '.txt')}" if pipeline == "persona_generation" else None
        result_handler.save_result(job_id, pipeline, result, custom_filename=custom_filename)
        job_manager.update_job_status(job_id, "completed")
    elif status == "failed":
        error_info = submission.get("error", {})
        result_handler.save_error(job_id, pipeline, error_info, original_job_data)
        job_manager.update_job_status(job_id, "failed", message=error_info.get("message"))

    return jsonify({"message": "結果受理"}), 200


@app.route("/resubmit-job", methods=["POST"])
def resubmit_job():
    job_context = request.json
    if not job_context:
        return jsonify({"message": "再実行コンテキストがありません。"}), 400
    new_job_id = job_manager.add_job(job_context)
    return jsonify({"message": f"ジョブをID '{new_job_id}' で再投入しました。"}), 200


@app.route("/", methods=["GET"])
def dashboard():
    stats = job_manager.get_stats()
    failed_jobs = get_failed_jobs()
    progress_matrix, persona_keys = get_progress_matrix()
    html_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
        <title>データセット生成ハブサーバー</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 95%; margin: 20px auto; }
            h1, h2 { border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: #f9f9f9; border: 1px solid #ddd; padding: 15px; border-radius: 8px; text-align: center; }
            .stat-card h3 { margin: 0 0 10px 0; font-size: 1em; }
            .stat-card .number { font-size: 2em; font-weight: bold; }
            .status-pending { color: #6c757d; } .bg-pending { background-color: #f8f9fa; }
            .status-processing { color: #0d6efd; } .bg-processing { background-color: #e7f1ff; }
            .status-completed { color: #198754; } .bg-completed { background-color: #e8f5e9; }
            .status-failed { color: #dc3545; } .bg-failed { background-color: #ffebee; }
            .matrix-table { width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
            .matrix-table th, .matrix-table td { border: 1px solid #ddd; padding: 8px; text-align: center; font-size: 0.8em; }
            .matrix-table th { background-color: #f2f2f2; position: sticky; top: 0; z-index: 1; }
            .matrix-table td div { margin-bottom: 2px; border-radius: 4px; padding: 2px 4px; font-weight: bold; }
            .paper-name { text-align: left; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .failed-jobs-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            .failed-jobs-table th, .failed-jobs-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .error-message { white-space: pre-wrap; word-break: break-all; max-height: 100px; overflow-y: auto; background: #eee; padding: 5px; }
        </style>
        <script>
            setTimeout(() => { window.location.reload(); }, 15000);
            function resubmitJob(jobContext) {
                if (!confirm('このジョブを再実行しますか？')) return;
                fetch('/resubmit-job', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(jobContext)
                }).then(res => res.json()).then(data => { alert(data.message); window.location.reload();
                }).catch(err => alert('再実行リクエストに失敗しました。'));
            }
        </script>
    </head>
    <body>
        <h1>司令塔 (Hub) ダッシュボード</h1>
        <h2>全体サマリー</h2>
        <div class="stats">
            <div class="stat-card"><h3 class="status-pending">未処理(Hub)</h3><div class="number status-pending">{{ stats.pending }}</div></div>
            <div class="stat-card"><h3 class="status-processing">処理中(Hub)</h3><div class="number status-processing">{{ stats.processing }}</div></div>
            <div class="stat-card"><h3 class="status-completed">完了</h3><div class="number status-completed">{{ stats.completed }}</div></div>
            <div class="stat-card"><h3 class="status-failed">失敗</h3><div class="number status-failed">{{ stats.failed }}</div></div>
            <div class="stat-card"><h3>総ジョブ数</h3><div class="number">{{ stats.total }}</div></div>
        </div>
        <h2>進捗マトリクス (P: Persona, L: LoRA, A: Parser)</h2>
        <div style="overflow-x: auto;">
            <table class="matrix-table">
                <thead>
                    <tr>
                        <th style="width: 20%;">論文</th>
                        {% for pk in persona_keys %}<th>{{ pk.replace('_', ' ') }}</th>{% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for md_file, personas in matrix.items() %}
                    <tr>
                        <td class="paper-name" title="{{ md_file }}">{{ md_file }}</td>
                        {% for pk in persona_keys %}
                        <td>
                            {% set p_status = personas.get(pk, {}).get('P', 'pending') %}
                            {% set l_status = personas.get(pk, {}).get('L', 'pending') %}
                            {% set a_status = personas.get(pk, {}).get('A', 'pending') %}
                            <div class="bg-{{ p_status }} status-{{ p_status }}">P</div>
                            <div class="bg-{{ l_status }} status-{{ l_status }}">L</div>
                            <div class="bg-{{ a_status }} status-{{ a_status }}">A</div>
                        </td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <h2>失敗したジョブ (Dead Letter Queue)</h2>
        {% if failed_jobs %}
            <table class="failed-jobs-table">
                <thead><tr><th>日時</th><th>パイプライン</th><th>エラー</th><th>アクション</th></tr></thead>
                <tbody>
                    {% for job in failed_jobs %}
                    <tr>
                        <td>{{ job.timestamp }}</td>
                        <td>{{ job.pipeline_name }}<br><small>{{ job.failed_job_id }}</small></td>
                        <td><div class="error-message">{{ job.error_info.message | tojson(indent=2) }}</div></td>
                        <td>{% if job.job_context_for_resubmit %}<button onclick='resubmitJob({{ job.job_context_for_resubmit | tojson }})'>再実行</button>{% endif %}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p>失敗したジョブはありません。</p>
        {% endif %}
    </body>
    </html>
    """
    # return render_template_string(stats=stats, failed_jobs=failed_jobs, matrix=progress_matrix, persona_keys=persona_keys, html_template=html_template)
    return render_template_string(
        html_template, stats=stats, failed_jobs=failed_jobs, matrix=progress_matrix, persona_keys=persona_keys
    )


# --- サーバーの起動 ---
if __name__ == "__main__":
    host = os.getenv("HUB_HOST", "0.0.0.0")
    port = int(os.getenv("HUB_PORT", 5000))
    threading.Thread(target=markdown_folder_monitor, daemon=True).start()
    threading.Thread(target=jstage_search_monitor, daemon=True).start()
    print(f"ダッシュボードURL: http://{host}:{port}/")
    app.run(host=host, port=port, debug=False)
