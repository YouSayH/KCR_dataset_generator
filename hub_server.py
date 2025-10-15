import os
import time
import threading
import re
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from core.job_manager import JobManager
from core.result_handler import ResultHandler

# .envファイルから環境変数を読み込む
load_dotenv()
RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
PROCESSED_MARKDOWN_LOG = "output/processed_markdown.log"
GENERATION_TARGETS = [
    {"age_group": "70代", "gender": "女性"},
    {"age_group": "80代", "gender": "男性"},
    {"age_group": "60代", "gender": "女性"},
]

# アプリケーションの初期化
app = Flask(__name__)
job_manager = JobManager()
result_handler = ResultHandler(base_output_dir="output")


# パイプライン2ジョブ生成ロジック
def extract_theme_from_markdown(filepath: str) -> str:
    """Markdownファイルからより賢くテーマを抽出する"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(2000)  # 検索範囲を調整

        # YAMLフロントマターをスキップする
        if content.startswith("---"):
            end_marker = content.find("---", 3)
            if end_marker != -1:
                content = content[end_marker + 3 :]

        # H1見出し (#) を最優先で探す
        h1_match = re.search(r"^#\s*(.*?)\n", content, re.MULTILINE)
        if h1_match:
            theme = h1_match.group(1).strip().replace("\n", " ")
            if all(keyword not in theme for keyword in ["はじめに", "要旨", "おわりに"]):
                return theme

        # H2見出し (##) を次に探す
        h2_matches = re.findall(r"^##\s*(.*?)\n", content, re.MULTILINE)
        for theme in h2_matches:
            theme = theme.strip().replace("\n", " ")  # 改行をスペースに置換
            if all(keyword not in theme for keyword in ["要旨", "はじめに", "おわりに", "まとめ", "結論"]):
                return theme

    except Exception as e:
        print(f"[ThemeExtractor] テーマ抽出中にエラー: {e}")

    # 最終手段
    return os.path.basename(os.path.splitext(filepath)[0])


def markdown_folder_monitor():
    """
    RAGソースフォルダを監視し、新しいMarkdownファイルが見つかったら
    ペルソナ生成ジョブを投入する。
    """
    print("[Monitor] Markdownフォルダの監視を開始します...")
    processed_files = set()

    # 過去に処理したファイルのログを読み込む
    try:
        with open(PROCESSED_MARKDOWN_LOG, "r", encoding="utf-8") as f:
            processed_files = set(line.strip() for line in f)
        print(f"[Monitor] {len(processed_files)}件の処理済みファイルをログから読み込みました。")
    except FileNotFoundError:
        pass

    while True:
        try:
            if not os.path.exists(RAG_SOURCE_DIR):
                time.sleep(10)
                continue

            for filename in os.listdir(RAG_SOURCE_DIR):
                if filename.endswith(".md") and filename not in processed_files:
                    print(f"[Monitor] 新規Markdownファイルを検出: {filename}")
                    filepath = os.path.join(RAG_SOURCE_DIR, filename)

                    paper_theme = extract_theme_from_markdown(filepath)
                    print(f"  -> 抽出されたテーマ: {paper_theme}")

                    # 定義されたターゲットごとにペルソナ生成ジョブを作成
                    for target in GENERATION_TARGETS:
                        job_data = {
                            "pipeline": "persona_generation",  # ★新しいパイプライン名
                            "paper_theme": paper_theme,
                            "age_group": target["age_group"],
                            "gender": target["gender"],
                            "source_markdown": filename,  # 元となったファイル名を記録
                        }
                        job_manager.add_job(job_data)

                    # 処理済みとして記録
                    processed_files.add(filename)
                    with open(PROCESSED_MARKDOWN_LOG, "a", encoding="utf-8") as f:
                        f.write(filename + "\n")

        except Exception as e:
            print(f"[Monitor] フォルダ監視中にエラーが発生しました: {e}")

        time.sleep(30)  # 30秒ごとにチェック


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
    submission = request.json
    job_id = submission.get("job_id")
    status = submission.get("status")
    pipeline = submission.get("pipeline")
    original_job_data = job_manager.jobs.get(job_id, {}).get("data", {})

    if not all([job_id, status, pipeline]):
        return jsonify({"error": "job_id, status, pipelineは必須です"}), 400

    if status == "completed":
        result = submission.get("result", {})
        # パイプライン2以降は、結果をファイルに保存するだけでなく、
        # 次のステップのジョブを生成する必要があるかもしれない（将来実装）
        saved_filename = f"{job_id}{result.get('extension', '.txt')}"
        result_handler.save_result(job_id, pipeline, result, custom_filename=saved_filename)
        job_manager.update_job_status(job_id, "completed")

        # ここからが重要
        # もし完了したのがペルソナ生成ジョブなら、次のLoRAデータ生成ジョブを作る
        if pipeline == "persona_generation":
            print(f"[Hub] ペルソナ生成完了({job_id})。次のLoRAデータ生成ジョブを作成します。")
            # 元のジョブ情報から、どの論文とペルソナを組み合わせるかを知る
            source_markdown = original_job_data.get("source_markdown")
            generated_persona_file = saved_filename

            if source_markdown and generated_persona_file:
                # ここで仕様書通り、逐次生成のジョブを投入する
                # まずは最初のステップ（CurrentAssessment）のジョブだけを投入
                lora_job_data = {
                    "pipeline": "lora_data_generation",
                    "source_markdown": source_markdown,
                    "source_persona": generated_persona_file,
                    "target_step": 0,  # 生成グループのインデックス (0 = CurrentAssessment)
                    "previous_results": {},  # 最初のステップなので空
                }
                job_manager.add_job(lora_job_data)
            else:
                print("[Hub] 警告: LoRAジョブの作成に必要な情報が不足しています。")

    elif status == "failed":
        error_info = submission.get("error", {})
        result_handler.save_error(job_id, pipeline, error_info)
        job_manager.update_job_status(job_id, "failed", message=error_info.get("message"))

    return jsonify({"message": "結果受理"}), 200


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
    host = os.getenv("HUB_HOST", "127.0.0.1")
    port = int(os.getenv("HUB_PORT", 5000))

    # フォルダ監視スレッドをバックグラウンドで開始
    monitor_thread = threading.Thread(target=markdown_folder_monitor, daemon=True)
    monitor_thread.start()

    app.run(host=host, port=port, debug=False)
