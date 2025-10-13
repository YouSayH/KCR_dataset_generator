import os
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from core.job_manager import JobManager
from core.result_handler import ResultHandler

# .envファイルから環境変数を読み込む
load_dotenv()

# アプリケーションの初期化
app = Flask(__name__)
job_manager = JobManager()
result_handler = ResultHandler(base_output_dir="output")


# テスト用のダミーデータ生成
def populate_dummy_jobs():
    """起動時に動作確認用のダミージョブを投入する"""
    print("テスト用のダミージョブを投入しています...")
    dummy_urls = [
        "https://www.jstage.jst.go.jp/article/rika/33/3/33_425/_pdf",
        "https://www.jstage.jst.go.jp/article/rika/20/3/20_3_227/_pdf",
        "https://www.jstage.jst.go.jp/article/jjrmc/54/3/54_201/_pdf",
    ]
    for url in dummy_urls:
        job_data = {
            "pipeline": "rag_source",  # パイプライン1のジョブ
            "url": url,
            "metadata": {"title": f"Dummy Title for {url}"},
        }
        job_manager.add_job(job_data)
    print(f"{len(dummy_urls)}件のダミージョブを投入しました。")


# APIエンドポイントの定義
@app.route("/get-job", methods=["GET"])
def get_job():
    """ワーカーがジョブを取得するためのエンドポイント"""
    worker_id = request.args.get("worker_id", "unknown_worker")
    job = job_manager.get_job(worker_id)
    if job:
        return jsonify(job)
    else:
        # 未処理のジョブがない場合は、コンテンツなしを返す
        return "", 204


@app.route("/submit-result", methods=["POST"])
def submit_result():
    """ワーカーが処理結果を送信するためのエンドポイント"""
    submission = request.json
    job_id = submission.get("job_id")
    status = submission.get("status")

    if not job_id or not status:
        return jsonify({"error": "job_idとstatusは必須です"}), 400

    if status == "completed":
        pipeline = submission.get("pipeline")
        result = submission.get("result", {})
        result_handler.save_result(job_id, pipeline, result)
        job_manager.update_job_status(job_id, "completed")
    elif status == "failed":
        pipeline = submission.get("pipeline")
        error_info = submission.get("error", {})
        result_handler.save_error(job_id, pipeline, error_info)
        job_manager.update_job_status(job_id, "failed", message=error_info.get("message"))
    else:
        return jsonify({"error": f"不正なステータスです: {status}"}), 400

    return jsonify({"message": f"ジョブ {job_id} の結果を受理しました"}), 200


# 管理用UI
@app.route("/", methods=["GET"])
def dashboard():
    """簡易的な管理ダッシュボードを表示する"""
    stats = job_manager.get_stats()

    html = """
    <!Doctype html>
    <html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>データセット生成ハブサーバー</title>
        <style>
            body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; padding: 0 20px; }
            h1, h2 { color: #111; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; }
            .stat-card { background: #f9f9f9; border: 1px solid #ddd; padding: 20px; border-radius: 8px; text-align: center; }
            .stat-card h3 { margin-top: 0; }
            .stat-card .number { font-size: 2.5em; font-weight: bold; }
            .progress-bar { background: #e0e0e0; border-radius: 5px; overflow: hidden; height: 25px; margin: 20px 0; }
            .progress-bar-inner { height: 100%; background: #4caf50; transition: width 0.5s; text-align: center; color: white; line-height: 25px; }
        </style>
        <script>
            setTimeout(() => { window.location.reload(); }, 5000);
        </script>
    </head>
    <body>
        <h1>司令塔 (Hub) ダッシュボード</h1>
        <p>このページは5秒ごとに自動更新されます。</p>
        
        <h2>ジョブ進捗</h2>
        <div class="stats">
            <div class="stat-card"><h3>総ジョブ数</h3><div class="number">{{ stats.total }}</div></div>
            <div class="stat-card" style="background:#fffbe6;"><h3>未処理</h3><div class="number">{{ stats.pending }}</div></div>
            <div class="stat-card" style="background:#e3f2fd;"><h3>処理中</h3><div class="number">{{ stats.processing }}</div></div>
            <div class="stat-card" style="background:#e8f5e9;"><h3>完了</h3><div class="number">{{ stats.completed }}</div></div>
            <div class="stat-card" style="background:#ffebee;"><h3>失敗</h3><div class="number">{{ stats.failed }}</div></div>
        </div>
        
        {% if stats.total > 0 %}
        <div class="progress-bar">
            <div class="progress-bar-inner" style="width: {{ (stats.completed / stats.total) * 100 }}%;">
                {{ '%.1f'|format((stats.completed / stats.total) * 100) }}%
            </div>
        </div>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, stats=stats)


# サーバーの起動
if __name__ == "__main__":
    # config.iniから設定を読み込み
    host = os.getenv("HUB_HOST", "127.0.0.1")
    port = int(os.getenv("HUB_PORT", 5000))

    # 起動時にダミージョブを投入
    populate_dummy_jobs()

    # Flaskサーバーを起動
    # debug=Falseにしないと、起動時にpopulate_dummy_jobsが2回実行されることがある
    app.run(host=host, port=port, debug=False)
