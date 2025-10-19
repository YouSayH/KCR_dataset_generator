import os
import json
import uuid
import time
from dotenv import load_dotenv

# 既存のロジックをインポート
from utils.persona_generator import generate_persona
from pipelines.pipeline_2_lora_finetune import process_lora_data_generation
from pipelines.pipeline_3_parser_finetune import process_parser_finetune_data_generation
from pipelines import pipeline_4_embedding_finetune
from schemas import SEQUENTIAL_GENERATION_ORDER

# --- 手動設定: 作業分担のためのペルソナ定義 ---
#
# ここをPCごとに編集することで、作業を分担できます。
# 例：Aさんは70代、Bさんは60代を担当する
#


GENERATION_TARGETS = [
    {"age_group": "70代", "gender": "女性"},
    # {"age_group": "70代", "gender": "男性"},
    # {"age_group": "70代", "gender": "女性"},
    # {"age_group": "70代", "gender": "男性"},
    # {"age_group": "60代", "gender": "女性"},
    # {"age_group": "60代", "gender": "男性"},
    # {"age_group": "60代", "gender": "女性"},
    # {"age_group": "60代", "gender": "男性"},
    # {"age_group": "80代", "gender": "女性"},
    # {"age_group": "80代", "gender": "男性"},
    # {"age_group": "80代", "gender": "女性"},
    # {"age_group": "80代", "gender": "男性"},
    # {"age_group": "10代", "gender": "女性"},
    # {"age_group": "10代", "gender": "男性"},
    # {"age_group": "20代", "gender": "女性"},
    # {"age_group": "20代", "gender": "男性"},
    # {"age_group": "30代", "gender": "女性"},
    # {"age_group": "30代", "gender": "男性"},
    # {"age_group": "40代", "gender": "女性"},
    # {"age_group": "40代", "gender": "男性"},
    # {"age_group": "50代", "gender": "女性"},
    # {"age_group": "50代", "gender": "男性"},
    # {"age_group": "90代", "gender": "女性"},
    # {"age_group": "90代", "gender": "男性"},
]

# --- 定数 ---
RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
PERSONA_DIR = "output/pipeline_2_lora_finetune/personas"
LORA_DIR = "output/pipeline_2_lora_finetune"
# LoRAの項目別データセットの保存先
LORA_ITEM_DATASET_DIR = os.path.join(LORA_DIR, "datasets_by_item")
PARSER_DIR = "output/pipeline_3_parser_finetune"
EMBEDDING_DIR = "output/pipeline_4_embedding_finetune"


def setup_directories():
    """
    必要なすべての出力ディレクトリを作成します。
    """
    print("[P234] ステップ1/3: 出力先フォルダを確認・作成します...")
    os.makedirs(PERSONA_DIR, exist_ok=True)
    os.makedirs(LORA_DIR, exist_ok=True)
    os.makedirs(LORA_ITEM_DATASET_DIR, exist_ok=True)  # 項目別データセット用フォルダ
    os.makedirs(PARSER_DIR, exist_ok=True)
    os.makedirs(EMBEDDING_DIR, exist_ok=True)


def run_p2_and_p3():
    """
    パイプライン2（LoRA）とパイプライン3（Parser）のデータセットを生成します。
    """
    print("\n[P234] ステップ2/3: P2 (LoRA) および P3 (Parser) のデータセットを生成します...")
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("[P234] エラー: GEMINI_API_KEYが設定されていません。")
        return

    if not os.path.exists(RAG_SOURCE_DIR):
        print(f"[P234] エラー: {RAG_SOURCE_DIR} が見つかりません。")
        print("先に `python main.py p1` を実行して、RAGソースファイルを作成してください。")
        return

    md_files = [f for f in os.listdir(RAG_SOURCE_DIR) if f.endswith(".md")]
    if not md_files:
        print(f"[P234] 警告: {RAG_SOURCE_DIR} にMarkdownファイルがありません。")
        return

    total_jobs = len(md_files) * len(GENERATION_TARGETS)
    print(
        f"[P234] {len(md_files)}件のMarkdownと{len(GENERATION_TARGETS)}件のペルソナ、合計{total_jobs}件のジョブを処理します。"
    )

    processed_count = 0
    for md_file in md_files:
        for target in GENERATION_TARGETS:
            processed_count += 1
            print(f"\n--- ジョブ {processed_count}/{total_jobs} ---")

            # --- ファイル名とIDの定義 ---
            # どのPCで実行しても同じID/ファイル名が生成されるようにする
            base_name = f"{md_file.replace('.md', '')}_{target['age_group']}_{target['gender']}"

            # P2: ペルソナファイル (P2, P3の共通の前提条件)
            persona_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_name}-persona"))
            persona_filename = f"{persona_job_id}.json"
            persona_path = os.path.join(PERSONA_DIR, persona_filename)

            # P2: LoRA「完了目印」ファイル
            # このファイル（UUID.jsonl）の存在有無で、P2の差分実行を判断する
            lora_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_name}-lora"))
            lora_done_marker_path = os.path.join(LORA_DIR, f"{lora_job_id}.done.marker")  # 完了目印ファイル

            # P3: Parserデータファイル
            parser_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_name}-parser"))
            parser_path = os.path.join(PARSER_DIR, f"{parser_job_id}.jsonl")

            # --- ステップ 1: ペルソナ生成 (P2, P3の前提条件) ---
            if not os.path.exists(persona_path):
                print(f"[実行中] {base_name}")
                try:
                    print("  -> (1/3) ペルソナを生成中...")
                    # --- ▼▼▼ Markdownファイルの内容を読み込む処理を追加 ▼▼▼ ---
                    source_markdown_path = os.path.join(RAG_SOURCE_DIR, md_file) # Markdownファイルのフルパスを取得
                    try:
                        with open(source_markdown_path, 'r', encoding='utf-8') as f:
                            # ファイル全体ではなく、最初の数千文字など、必要な部分だけを渡す
                            # ここでは例として最初の4000文字を渡します
                            paper_content_for_persona = f.read(4000)
                    except FileNotFoundError:
                        print(f"  -> !! エラー: Markdownファイルが見つかりません: {source_markdown_path}")
                        paper_content_for_persona = "" # ファイルがない場合は空文字を渡す
                    except Exception as read_e:
                        print(f"  -> !! エラー: Markdownファイルの読み込み中にエラー: {read_e}")
                        paper_content_for_persona = "" # 読み込み失敗時も空文字

                    # --- ▲▲▲ Markdown読み込み追加ここまで ▲▲▲ ---

                    persona_obj = generate_persona(
                        paper_theme=md_file.replace(".md", ""),
                        age_group=target["age_group"],
                        gender=target["gender"],
                        # --- ▼▼▼ 読み込んだ論文内容を引数として渡す ▼▼▼ ---
                        paper_content=paper_content_for_persona,
                        # --- ▲▲▲ 引数追加ここまで ▲▲▲ ---
                        gemini_api_key=gemini_api_key,
                    )
                    with open(persona_path, "w", encoding="utf-8") as f:
                        f.write(persona_obj.model_dump_json(indent=2, ensure_ascii=False))
                    print(f"  -> (1/3) ペルソナを保存しました: {persona_filename}")
                except Exception as e:
                    print(f"  -> !! エラー: {base_name} のペルソナ生成中に失敗。")
                    print(f"     詳細: {e}") # エラー詳細を表示（エラーメッセージ確認用）
                    print("     このジョブ（ペルソナ）をスキップして次に進みます。")
                    continue
            else:
                print(f"[チェック] {base_name} のペルソナは既に存在します。")

            # --- ステップ 2: LoRAデータ生成 (P2) ---
            if not os.path.exists(lora_done_marker_path):
                print(f"  -> (2/3) LoRAデータを逐次生成中 (ID: {lora_job_id})...")
                try:
                    lora_jsonl_records_buffer = []  # このジョブで生成した全項目のJSONL行を一時的に溜める
                    accumulated_generated_text = {}  # 次のステップに渡す「生成済みテキスト」

                    # 逐次生成ループ
                    for current_step in range(len(SEQUENTIAL_GENERATION_ORDER)):
                        field_name, _ = SEQUENTIAL_GENERATION_ORDER[current_step]
                        print(f"      - LoRAステップ {current_step + 1}/{len(SEQUENTIAL_GENERATION_ORDER)} ({field_name})...")

                        step_job_data = {
                            "job_id": lora_job_id,
                            "source_markdown": md_file,
                            "source_persona": persona_filename,
                            "target_step": current_step,
                            "previous_results": accumulated_generated_text,
                        }
                        # P2のロジックを呼び出し
                        step_result = process_lora_data_generation(step_job_data, gemini_api_key)

                        # メモリに一時保存 (項目名, JSONL文字列)
                        jsonl_record_str = step_result["content"]
                        lora_jsonl_records_buffer.append((field_name, jsonl_record_str))

                        # 次ステップ用のテキストを蓄積
                        accumulated_generated_text.update(step_result["next_step_data"]["generated_items"])

                    # ループが正常に完了した後、全項目のデータを対応するファイルに「追記」する
                    print("      -> 全ステップ完了。項目別ファイルに追記します...")
                    for field_name, jsonl_record_str in lora_jsonl_records_buffer:
                        # ★ここが重要★ 項目ごとのファイルに追記する
                        lora_item_path = os.path.join(LORA_ITEM_DATASET_DIR, f"{field_name}.jsonl")
                        with open(lora_item_path, "a", encoding="utf-8") as f:
                            f.write(jsonl_record_str + "\n")

                    # 処理が正常に完了したことを示す「目印ファイル」を作成する
                    with open(lora_done_marker_path, "w", encoding="utf-8") as f:
                        f.write(f"Processed on {time.ctime()}\n")

                    print("  -> (2/3) LoRAデータを項目別ファイルに追記完了。")

                except Exception as e:
                    print(f"  -> !! エラー: {base_name} のP2 (LoRA) 処理中に失敗。")
                    print(f"     詳細: {e}")
                    # P3の処理は継続するため、ここでは continue しない
            else:
                print(f"  -> (2/3) LoRAデータ (目印ファイル: {lora_job_id}.done.marker) は既に存在します。")

            # --- ステップ 3: Parserデータ生成 (P3) ---
            if not os.path.exists(parser_path):
                print("  -> (3/3) Parserデータを生成中...")
                try:
                    p3_job_data = {
                        "job_id": parser_job_id,
                        "source_markdown": md_file,
                        "source_persona": persona_filename,
                    }
                    # P3のロジックを呼び出し
                    parser_result = process_parser_finetune_data_generation(p3_job_data, gemini_api_key)

                    # P3は項目別ではないので、そのままID名で保存
                    with open(parser_path, "w", encoding="utf-8") as f:
                        f.write(parser_result["content"])
                    print(f"  -> (3/3) Parserデータを保存しました: {parser_job_id}.jsonl")

                except Exception as e:
                    print(f"  -> !! エラー: {base_name} のP3 (Parser) 処理中に失敗。")
                    print(f"     詳細: {e}")
                    # 次のジョブに進む
                    continue
            else:
                print("  -> (3/3) Parserデータは既に存在します。")


def run_p4():
    """
    パイプライン4（Embedding）のデータセットを生成します。
    これはRAGソース全体から1つのファイルを作るバッチ処理です。
    """
    print("\n[P234] ステップ3/3: P4 (Embedding) のデータセットを生成します...")
    try:
        # P4のmain()は、INPUT_DIR (RAG_SOURCE_DIR) を直接参照するため、
        # 引数なしで呼び出すだけで動作します。
        pipeline_4_embedding_finetune.main()
    except Exception as e:
        print(f"[P234] !! エラー: P4の実行に失敗しました: {e}")


def main():
    """
    データセット生成（P2, P3, P4）のメインロジック。
    """
    start_time = time.time()
    setup_directories()
    run_p2_and_p3()
    run_p4()
    end_time = time.time()

    print("\n" + "=" * 50)
    print("パイプライン 2, 3, 4 実行完了")
    print(f"合計所要時間: {end_time - start_time:.2f} 秒")
    print(f"P2 (LoRA) データセット: {LORA_ITEM_DATASET_DIR}")
    print(f"P3 (Parser) データセット: {PARSER_DIR}")
    print(f"P4 (Embedding) データセット: {EMBEDDING_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
