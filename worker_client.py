import os
import time
import requests
import socket
from dotenv import load_dotenv

# パイプライン処理関数のインポート
from pipelines.pipeline_1_rag_source import process_pipeline_1

# from pipelines.pipeline_2_lora_finetune import process_pipeline_2 # 将来追加
# from pipelines.pipeline_3_parser_finetune import process_pipeline_3 # 将来追加
# from pipelines.pipeline_4_embedding_finetune import process_pipeline_4 # 将来追加
from utils.persona_generator import generate_persona
from pipelines.pipeline_2_lora_finetune import process_lora_data_generation

# .envファイルから環境変数を読み込む
load_dotenv()

# ワーカーの設定
HUB_URL = f"http://{os.getenv('HUB_HOST', '127.0.0.1')}:{os.getenv('HUB_PORT', 5000)}"
POLLING_INTERVAL = int(os.getenv("WORKER_POLLING_INTERVAL", 10))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
    raise ValueError("`config.ini`ファイルに有効なGEMINI_API_KEYを設定してください。")

# ワーカーを識別するための一意なIDを生成
WORKER_ID = f"{socket.gethostname()}-{os.getpid()}"

print("～～～ ワーカークライアント起動 ～～～")
print(f"ワーカーID: {WORKER_ID}")
print(f"接続先ハブ: {HUB_URL}")
print("～～～～～～～～～～～～～～～～～～～")


def dispatch_job(job_data: dict):
    """ジョブのパイプライン名に応じて、適切な処理関数を呼び出す"""
    pipeline = job_data.get("pipeline")
    print(f"   処理を開始します... (パイプライン: {pipeline})")

    if pipeline == "rag_source":
        return process_pipeline_1(job_data, GEMINI_API_KEY)
    elif pipeline == "persona_generation":
        # ペルソナ生成関数を呼び出す
        persona_obj = generate_persona(
            paper_theme=job_data["paper_theme"],
            age_group=job_data["age_group"],
            gender=job_data["gender"],
            gemini_api_key=GEMINI_API_KEY,
        )
        # 結果をJSON文字列として返す
        return {"content": persona_obj.model_dump_json(indent=2, ensure_ascii=False), "extension": ".json"}
    elif pipeline == "lora_data_generation":
        return process_lora_data_generation(job_data, GEMINI_API_KEY)

    else:
        raise ValueError(f"'{pipeline}'は未定義のパイプラインです。")


# メインの処理ループ
def main_loop():
    while True:
        job = None
        result_payload = None  # ループの開始時にリセット
        try:
            # 1. ジョブを取得
            print(f"\n[{time.ctime()}] ハブにジョブを問い合わせています...")
            response = requests.get(f"{HUB_URL}/get-job", params={"worker_id": WORKER_ID}, timeout=10)

            if response.status_code == 200:
                job = response.json()
                print(f"-> ジョブ受信: {job['job_id']}")

                # 2. ジョブを処理
                result_content = dispatch_job(job)

                # 成功した場合の処理結果
                result_payload = {
                    "job_id": job["job_id"],
                    "pipeline": job["pipeline"],
                    "status": "completed",
                    "result": result_content,
                }
                print("   処理成功。結果をハブに送信します。")

            elif response.status_code == 204:
                print(f"-> 現在、処理可能なジョブはありません。{POLLING_INTERVAL}秒後に再試行します。")
                time.sleep(POLLING_INTERVAL)
                continue  # ループの先頭に戻る
            else:
                print(f"エラー: ハブから予期しない応答がありました (ステータスコード: {response.status_code})")
                time.sleep(POLLING_INTERVAL)
                continue

        except Exception as e:
            # 処理中または通信中に発生したあらゆる例外をキャッチ
            print(f"\nエラーが発生しました: {e}")
            if job:
                # 失敗した場合の処理結果
                result_payload = {
                    "job_id": job["job_id"],
                    "pipeline": job.get("pipeline", "unknown"),
                    "status": "failed",
                    "error": {"message": str(e), "worker_id": WORKER_ID},
                }
                print("   処理失敗。エラーをハブに送信します。")
            else:
                # ジョブ取得前のエラーなら何もしない
                pass

            time.sleep(POLLING_INTERVAL)

        # 3. 結果をハブに送信 (成功・失敗問わず、ペイロードがあれば)
        if result_payload:
            try:
                requests.post(f"{HUB_URL}/submit-result", json=result_payload, timeout=30)
                print("-> 送信完了。")
            except requests.exceptions.RequestException as req_e:
                print(f"!! 重大エラー: ハブへの結果送信に失敗しました: {req_e}")
                print(f"   -> ジョブ {job['job_id']} の結果が失われた可能性があります。")


if __name__ == "__main__":
    main_loop()
