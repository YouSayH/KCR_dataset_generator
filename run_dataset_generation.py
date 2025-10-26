import os
import json
import uuid
import time
from dotenv import load_dotenv

# 既存のロジックをインポート
from utils.persona_generator import generate_persona

# from pipelines.pipeline_2_lora_finetune import process_lora_data_generation # 古い関数
from pipelines.pipeline_2_lora_finetune import process_full_plan_generation  # 新しい一括生成関数

from pipelines.pipeline_3_parser_finetune import process_parser_finetune_data_generation
from pipelines import pipeline_4_embedding_finetune
# from schemas import SEQUENTIAL_GENERATION_ORDER # P2では不要になった


# --- 定数 ---
RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
PERSONA_DIR = "output/pipeline_2_lora_finetune/personas"
LORA_DIR = "output/pipeline_2_lora_finetune"
# LORA_ITEM_DATASET_DIR = os.path.join(LORA_DIR, "datasets_by_item") # 項目別は使用しない
LORA_DATASET_FILE = os.path.join(LORA_DIR, "full_plan_dataset.jsonl")  # 単一ファイルに集約
PARSER_DIR = "output/pipeline_3_parser_finetune"
EMBEDDING_DIR = "output/pipeline_4_embedding_finetune"


def setup_directories():
    """
    必要なすべての出力ディレクトリを作成します。
    """
    print("[P234] ステップ1/3: 出力先フォルダを確認・作成します...")
    os.makedirs(PERSONA_DIR, exist_ok=True)
    os.makedirs(LORA_DIR, exist_ok=True)
    # os.makedirs(LORA_ITEM_DATASET_DIR, exist_ok=True) # 項目別は使用しない
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

    # total_jobs = len(md_files) * len(GENERATION_TARGETS) # 古い計算
    total_jobs = len(md_files)  # 新しい計算 (1論文1ジョブ)
    print(f"[P234] {len(md_files)}件のMarkdownファイル（論文）に基づき、{total_jobs}件のジョブを処理します。")

    processed_count = 0
    for md_file in md_files:
        processed_count += 1
        print(f"\n--- ジョブ {processed_count}/{total_jobs} ---")
        print(f"  論文: {md_file}")

        # --- ファイル名とIDの定義 ---
        # どのPCで実行しても同じID/ファイル名が生成されるようにする
        base_name = f"{md_file.replace('.md', '')}"  # 年齢・性別を除外

        # P2: ペルソナファイル (P2, P3の共通の前提条件)
        persona_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_name}-persona"))
        persona_filename = f"{persona_job_id}.json"
        persona_path = os.path.join(PERSONA_DIR, persona_filename)

        # P2: LoRA「完了目印」ファイル
        lora_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_name}-lora"))
        lora_done_marker_path = os.path.join(LORA_DIR, f"{lora_job_id}.done.marker")  # 完了目印ファイル

        # P3: Parserデータファイル
        parser_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_name}-parser"))
        parser_path = os.path.join(PARSER_DIR, f"{parser_job_id}.jsonl")

        # --- ステップ 1: ペルソナ生成 (P2, P3の前提条件) ---
        if not os.path.exists(persona_path):
            print(f"[実行中] {base_name}")
            try:
                print("  -> (1/3) 論文に最適なペルソナを生成中...")
                source_markdown_path = os.path.join(RAG_SOURCE_DIR, md_file)
                try:
                    with open(source_markdown_path, "r", encoding="utf-8") as f:
                        # 論文内容全体を渡す（最大トークン数を考慮し、ある程度で切る）
                        paper_content_for_persona = f.read(20000)  # ペルソナ生成の品質のため、多めに渡す
                except FileNotFoundError:
                    print(f"  -> !! エラー: Markdownファイルが見つかりません: {source_markdown_path}")
                    continue
                except Exception as read_e:
                    print(f"  -> !! エラー: Markdownファイルの読み込み中にエラー: {read_e}")
                    continue

                persona_obj = generate_persona(
                    paper_theme=md_file.replace(".md", ""),
                    paper_content=paper_content_for_persona,
                    gemini_api_key=gemini_api_key,
                )

                with open(persona_path, "w", encoding="utf-8") as f:
                    json.dump(persona_obj, f, indent=2, ensure_ascii=False, default=str)
                print(f"  -> (1/3) ペルソナを保存しました: {persona_filename}")
            except Exception as e:
                print(f"  -> !! エラー: {base_name} のペルソナ生成中に失敗。")
                print(f"     詳細: {e}")
                print("     このジョブ（論文）をスキップして次に進みます。")
                continue
        else:
            print(f"[チェック] {base_name} のペルソナは既に存在します。")

        # --- ステップ 2: LoRAデータ生成 (P2) ---
        if not os.path.exists(lora_done_marker_path):
            print(f"  -> (2/3) LoRAデータ（フル計画書）を生成中 (ID: {lora_job_id})...")
            try:
                step_job_data = {
                    "job_id": lora_job_id,
                    "source_markdown": md_file,
                    "source_persona": persona_filename,
                }
                # P2の新しい一括生成ロジックを呼び出し
                step_result = process_full_plan_generation(step_job_data, gemini_api_key)

                # 完了したJSONL行（1行）を、集約ファイルに「追記」する
                jsonl_record_str = step_result["content"]
                with open(LORA_DATASET_FILE, "a", encoding="utf-8") as f:
                    f.write(jsonl_record_str + "\n")

                # 処理が正常に完了したことを示す「目印ファイル」を作成する
                with open(lora_done_marker_path, "w", encoding="utf-8") as f:
                    f.write(f"Processed on {time.ctime()}\n")

                print(f"  -> (2/3) LoRAデータを '{LORA_DATASET_FILE}' に追記完了。")

            except Exception as e:
                print(f"  -> !! エラー: {base_name} のP2 (LoRA) 処理中に失敗。")
                print(f"     詳細: {e}")
                # P3の処理は継続するため、ここでは continue しない
        else:
            print(f"  -> (2/3) LoRAデータ (目印ファイル: {lora_job_id}.done.marker) は既に存在します。")

        # --- ステップ 3: Parserデータ生成 (P3) ---
        if not os.path.exists(parser_path):
            print("  -> (3/3) Parserデータ（資料→ペルソナ）を生成中...")
            try:
                p3_job_data = {
                    "job_id": parser_job_id,
                    "source_markdown": md_file,  # 論文コンテキストも渡す
                    "source_persona": persona_filename,
                }
                # P3のロジックを呼び出し (pipeline_3_parser_finetune.py側が変更されている前提)
                parser_result = process_parser_finetune_data_generation(p3_job_data, gemini_api_key)

                # P3はジョブごとに1ファイル（1行）を保存
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
    print(f"P2 (LoRA) データセット: {LORA_DATASET_FILE}")
    print(f"P3 (Parser) データセット: {PARSER_DIR}")
    print(f"P4 (Embedding) データセット: {EMBEDDING_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
