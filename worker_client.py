# import os
# import time
# import requests
# import socket
# from dotenv import load_dotenv

# # パイプライン処理関数のインポート
# from pipelines.pipeline_1_rag_source import process_pipeline_1

# # from pipelines.pipeline_2_lora_finetune import process_pipeline_2 # 将来追加
# # from pipelines.pipeline_3_parser_finetune import process_pipeline_3 # 将来追加
# # from pipelines.pipeline_4_embedding_finetune import process_pipeline_4 # 将来追加
# from utils.persona_generator import generate_persona
# from pipelines.pipeline_2_lora_finetune import process_lora_data_generation
# from pipelines.pipeline_3_parser_finetune import process_parser_finetune_data_generation

# # .envファイルから環境変数を読み込む
# load_dotenv()

# # ワーカーの設定
# HUB_URL = f"http://{os.getenv('HUB_HOST', '127.0.0.1')}:{os.getenv('HUB_PORT', 5000)}"
# POLLING_INTERVAL = int(os.getenv("WORKER_POLLING_INTERVAL", 10))
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
#     raise ValueError("`config.ini`ファイルに有効なGEMINI_API_KEYを設定してください。")

# # ワーカーを識別するための一意なIDを生成
# WORKER_ID = f"{socket.gethostname()}-{os.getpid()}"

# print("～～～ ワーカークライアント起動 ～～～")
# print(f"ワーカーID: {WORKER_ID}")
# print(f"接続先ハブ: {HUB_URL}")
# print("～～～～～～～～～～～～～～～～～～～")


# def dispatch_job(job_data: dict):
#     """ジョブのパイプライン名に応じて、適切な処理関数を呼び出す"""
#     pipeline = job_data.get("pipeline")
#     print(f"   処理を開始します... (パイプライン: {pipeline})")

#     if pipeline == "rag_source":
#         return process_pipeline_1(job_data, GEMINI_API_KEY)
#     elif pipeline == "persona_generation":
#         # ペルソナ生成関数を呼び出す
#         persona_obj = generate_persona(
#             paper_theme=job_data["paper_theme"],
#             age_group=job_data["age_group"],
#             gender=job_data["gender"],
#             gemini_api_key=GEMINI_API_KEY,
#         )
#         # 結果をJSON文字列として返す
#         return {"content": persona_obj.model_dump_json(indent=2, ensure_ascii=False), "extension": ".json"}
#     elif pipeline == "lora_data_generation":
#         return process_lora_data_generation(job_data, GEMINI_API_KEY)
#     elif pipeline == "parser_finetune":
#         return process_parser_finetune_data_generation(job_data, GEMINI_API_KEY)
#     else:
#         raise ValueError(f"'{pipeline}'は未定義のパイプラインです。")


# # メインの処理ループ
# def main_loop():
#     while True:
#         job = None
#         result_payload = None  # ループの開始時にリセット
#         try:
#             # 1. ジョブを取得
#             print(f"\n[{time.ctime()}] ハブにジョブを問い合わせています...")
#             response = requests.get(f"{HUB_URL}/get-job", params={"worker_id": WORKER_ID}, timeout=10)

#             if response.status_code == 200:
#                 job = response.json()
#                 print(f"-> ジョブ受信: {job['job_id']}")

#                 # 2. ジョブを処理
#                 result_content = dispatch_job(job)

#                 # 成功した場合の処理結果
#                 result_payload = {
#                     "job_id": job["job_id"],
#                     "pipeline": job["pipeline"],
#                     "status": "completed",
#                     "result": result_content,
#                 }
#                 print("   処理成功。結果をハブに送信します。")

#             elif response.status_code == 204:
#                 print(f"-> 現在、処理可能なジョブはありません。{POLLING_INTERVAL}秒後に再試行します。")
#                 time.sleep(POLLING_INTERVAL)
#                 continue  # ループの先頭に戻る
#             else:
#                 print(f"エラー: ハブから予期しない応答がありました (ステータスコード: {response.status_code})")
#                 time.sleep(POLLING_INTERVAL)
#                 continue

#         except Exception as e:
#             # 処理中または通信中に発生したあらゆる例外をキャッチ
#             print(f"\nエラーが発生しました: {e}")
#             if job:
#                 # 失敗した場合の処理結果
#                 result_payload = {
#                     "job_id": job["job_id"],
#                     "pipeline": job.get("pipeline", "unknown"),
#                     "status": "failed",
#                     "error": {"message": str(e), "worker_id": WORKER_ID},
#                 }
#                 print("   処理失敗。エラーをハブに送信します。")
#             else:
#                 # ジョブ取得前のエラーなら何もしない
#                 pass

#             time.sleep(POLLING_INTERVAL)

#         # 3. 結果をハブに送信 (成功・失敗問わず、ペイロードがあれば)
#         if result_payload:
#             try:
#                 requests.post(f"{HUB_URL}/submit-result", json=result_payload, timeout=30)
#                 print("-> 送信完了。")
#             except requests.exceptions.RequestException as req_e:
#                 print(f"!! 重大エラー: ハブへの結果送信に失敗しました: {req_e}")
#                 print(f"   -> ジョブ {job['job_id']} の結果が失われた可能性があります。")


# if __name__ == "__main__":
#     main_loop()


import os
import time
import requests
import socket
import json
import threading
import uuid
from dotenv import load_dotenv
from pathlib import Path

# パイプライン処理関数のインポート
from pipelines.pipeline_1_rag_source import process_pipeline_1
from utils.persona_generator import generate_persona
from pipelines.pipeline_2_lora_finetune import process_lora_data_generation
from pipelines.pipeline_3_parser_finetune import process_parser_finetune_data_generation
from schemas import SEQUENTIAL_GENERATION_ORDER

# .envファイルから環境変数を読み込む
load_dotenv()

# --- ワーカー設定 ---
HUB_URL = f"http://{os.getenv('HUB_HOST', '127.0.0.1')}:{os.getenv('HUB_PORT', 5000)}"
POLLING_INTERVAL = int(os.getenv("WORKER_POLLING_INTERVAL", 30))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- ローカルディレクトリ設定 ---
ASSETS_DIR = Path("worker_assets")
RAG_SOURCE_CACHE_DIR = ASSETS_DIR / "rag_source"
PROGRESS_DIR = Path("worker_progress")
OUTBOX_DIR = Path("worker_outbox")
OUTPUT_DIR = Path("output")  # 成果物の最終保存先

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
    raise ValueError("`.env`ファイルに有効なGEMINI_API_KEYを設定してください。")

WORKER_ID = f"{socket.gethostname()}-{os.getpid()}"

# --- 初期化処理 ---
RAG_SOURCE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
PROGRESS_DIR.mkdir(exist_ok=True)
OUTBOX_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "pipeline_2_lora_finetune" / "personas").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "pipeline_3_parser_finetune").mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "pipeline_2_lora_finetune").mkdir(parents=True, exist_ok=True)


print("～～～ 自律型ワーカークライアント起動 ～～～")
print(f"ワーカーID: {WORKER_ID}")
print(f"接続先ハブ: {HUB_URL}")
print("～～～～～～～～～～～～～～～～～～～～～～")


# --- アセット同期 ---
def sync_assets_from_hub():
    print("\n[Sync] ハブとアセットを同期中...")
    try:
        response = requests.get(f"{HUB_URL}/assets/manifest", timeout=15)
        response.raise_for_status()
        manifest = response.json()

        with open(ASSETS_DIR / "generation_targets.json", "w", encoding="utf-8") as f:
            json.dump(manifest["generation_targets"], f, ensure_ascii=False, indent=2)

        server_files = set(manifest["rag_source_files"])
        local_files = set(f.name for f in RAG_SOURCE_CACHE_DIR.iterdir())
        missing_files = server_files - local_files

        if missing_files:
            print(f"[Sync] {len(missing_files)}件の新しい論文ファイルをダウンロードします...")
            for filename in missing_files:
                print(f"  -> Downloading {filename}...")
                file_res = requests.get(f"{HUB_URL}/assets/file/{filename}", timeout=60)
                file_res.raise_for_status()
                with open(RAG_SOURCE_CACHE_DIR / filename, "wb") as f:
                    f.write(file_res.content)
            print("[Sync] 同期が完了しました。")
        else:
            print("[Sync] アセットは最新です。")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[Sync] !! ハブへの接続に失敗: {e}。ローカルのアセットで処理を続行します。")
        return False


# --- 成果物送信スレッド ---
def submitter_thread():
    while True:
        try:
            outbox_files = list(OUTBOX_DIR.glob("*.json"))
            if outbox_files:
                print(f"[Submitter] {len(outbox_files)}件の送信待機中の成果物があります。")
                for filepath in outbox_files:
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            payload = json.load(f)
                        print(f"  -> {payload.get('job_id')} を送信中...")
                        response = requests.post(f"{HUB_URL}/submit-result", json=payload, timeout=30)
                        if response.status_code == 200:
                            filepath.unlink()  # 送信成功したらファイルを削除
                            print("     送信成功。")
                        else:
                            print(f"     !! 送信失敗 (HTTP {response.status_code})。次回再試行します。")
                    except Exception as e:
                        print(f"  !! 送信処理中にエラー: {e}")
        except Exception as e:
            print(f"[Submitter] !! 送信スレッドで予期せぬエラー: {e}")
        time.sleep(20)


# --- LoRAチェーン処理 (中断・再開対応) ---
def handle_lora_chain_job(job_data: dict):
    progress_file = PROGRESS_DIR / f"{job_data['job_id']}.progress.json"
    start_step, accumulated_results = 0, {}
    if progress_file.exists():
        print("    -> 中断したLoRAジョブを発見。進捗を復元します。")
        progress_data = json.loads(progress_file.read_text(encoding="utf-8"))
        start_step = progress_data.get("next_step", 0)
        accumulated_results = progress_data.get("accumulated_results", {})

    total_steps = len(SEQUENTIAL_GENERATION_ORDER)
    for current_step in range(start_step, total_steps):
        print(f"      - LoRAステップ {current_step + 1}/{total_steps} を実行中...")
        step_job_data = {**job_data, "target_step": current_step, "previous_results": accumulated_results}

        # 従来の単一ステップ生成関数を呼び出す
        step_result = process_lora_data_generation(step_job_data, GEMINI_API_KEY)

        # 成功したら結果を蓄積
        accumulated_results.update(step_result["next_step_data"]["generated_items"])
        progress_to_save = {"next_step": current_step + 1, "accumulated_results": accumulated_results}
        progress_file.write_text(json.dumps(progress_to_save, ensure_ascii=False, indent=2), encoding="utf-8")

    print("    -> ★★★ 全LoRAステップの生成が完了しました！ ★★★")
    progress_file.unlink()
    return {"content": json.dumps(accumulated_results, ensure_ascii=False, default=str), "extension": ".jsonl"}


# --- タスク実行と結果のキューイング ---
def execute_task(job_id, pipeline_name, job_context):
    print(f"   処理を開始します... (ID: {job_id}, パイプライン: {pipeline_name})")
    try:
        # job_contextに常にjob_idを含めておく
        job_context_with_id = {**job_context, "job_id": job_id}

        if pipeline_name == "persona_generation":
            result_obj = generate_persona(
                paper_theme=job_context["paper_theme"],
                age_group=job_context["age_group"],
                gender=job_context["gender"],
                gemini_api_key=GEMINI_API_KEY,
            )
            result_content = result_obj.model_dump_json(indent=2, ensure_ascii=False)
            # ペルソナはローカルにも保存
            persona_path = OUTPUT_DIR / "pipeline_2_lora_finetune" / "personas" / f"{job_id}.json"
            persona_path.write_text(result_content, encoding="utf-8")
            payload_result = {"content": result_content, "extension": ".json"}

        elif pipeline_name == "lora_chain_generation":
            payload_result = handle_lora_chain_job(job_context_with_id)
            # LoRAの結果もローカルに保存
            lora_path = OUTPUT_DIR / "pipeline_2_lora_finetune" / f"{job_id}.jsonl"
            lora_path.write_text(payload_result["content"] + "\n", encoding="utf-8")

        elif pipeline_name == "parser_finetune":
            payload_result = process_parser_finetune_data_generation(job_context_with_id, GEMINI_API_KEY)
            # Parserの結果もローカルに保存
            parser_path = OUTPUT_DIR / "pipeline_3_parser_finetune" / f"{job_id}.jsonl"
            parser_path.write_text(payload_result["content"] + "\n", encoding="utf-8")

        else:
            raise ValueError(f"未定義のパイプラインです: {pipeline_name}")

        payload = {
            "job_id": job_id,
            "pipeline": pipeline_name,
            "status": "completed",
            "result": payload_result,
            "original_job_data": job_context,
        }

    except Exception as e:
        print(f"   !! エラー発生: {e}")
        payload = {
            "job_id": job_id,
            "pipeline": pipeline_name,
            "status": "failed",
            "error": {"message": str(e), "worker_id": WORKER_ID},
            "original_job_data": job_context,
        }

    outbox_file = OUTBOX_DIR / f"{job_id}.json"
    outbox_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"   -> 結果を送信待ちキューに追加しました: {outbox_file.name}")


# --- メインループ ---
def main_loop():
    sync_assets_from_hub()
    threading.Thread(target=submitter_thread, daemon=True).start()

    while True:
        print(f"\n[{time.ctime()}] ローカルで実行可能なタスクをスキャン中...")
        found_task = False
        try:
            rag_files = list(RAG_SOURCE_CACHE_DIR.glob("*.md"))
            targets = json.loads((ASSETS_DIR / "generation_targets.json").read_text(encoding="utf-8"))
        except FileNotFoundError:
            print("アセットファイルが見つかりません。ハブとの同期を待ちます。")
            time.sleep(POLLING_INTERVAL)
            sync_assets_from_hub()
            continue

        for md_file in sorted(rag_files):
            for target in targets:
                base_id_str = f"{md_file.name}-{target['age_group']}_{target['gender']}"
                persona_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_id_str}-persona"))
                lora_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_id_str}-lora"))
                parser_job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{base_id_str}-parser"))

                persona_done = (OUTPUT_DIR / "pipeline_2_lora_finetune" / "personas" / f"{persona_job_id}.json").exists()
                lora_done = (OUTPUT_DIR / "pipeline_2_lora_finetune" / f"{lora_job_id}.jsonl").exists()
                parser_done = (OUTPUT_DIR / "pipeline_3_parser_finetune" / f"{parser_job_id}.jsonl").exists()

                if not persona_done:
                    job_context = {"source_markdown": md_file.name, "paper_theme": md_file.stem, **target}
                    execute_task(persona_job_id, "persona_generation", job_context)
                    found_task = True
                    break

                if not lora_done:
                    job_context = {"source_markdown": md_file.name, "source_persona": f"{persona_job_id}.json"}
                    execute_task(lora_job_id, "lora_chain_generation", job_context)
                    found_task = True
                    break

                if not parser_done:
                    job_context = {"source_markdown": md_file.name, "source_persona": f"{persona_job_id}.json"}
                    execute_task(parser_job_id, "parser_finetune", job_context)
                    found_task = True
                    break

            if found_task:
                break

        if not found_task:
            print("-> 現在、未処理のタスクはありません。次の同期間隔まで待機します。")
            time.sleep(POLLING_INTERVAL)
            sync_assets_from_hub()


if __name__ == "__main__":
    main_loop()
