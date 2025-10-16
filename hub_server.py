import os
import time
import threading
import re
import json
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from core.job_manager import JobManager
from core.result_handler import ResultHandler
from schemas import SEQUENTIAL_GENERATION_ORDER
from utils.jstage_client import JStageClient

# .envファイルから環境変数を読み込む
load_dotenv()
RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
PROCESSED_MARKDOWN_LOG = "output/processed_markdown.log"
DEAD_LETTER_QUEUE_LOG = "output/logs/dead_letter_queue.jsonl"
GENERATION_TARGETS = [
    {"age_group": "70代", "gender": "女性"},
    # {"age_group": "80代", "gender": "男性"},
    # {"age_group": "60代", "gender": "女性"},
]
PROCESSED_JSTAGE_LOG = "output/processed_jstage_dois.log" # 新しいログファイル
SEARCH_KEYWORDS = ["リハビリテーション", "理学療法", "作業療法"] # 検索キーワード
SEARCH_INTERVAL_SECONDS = 3600 # 1時間に1回検索

# アプリケーションの初期化
app = Flask(__name__)
job_manager = JobManager()
result_handler = ResultHandler(base_output_dir="output")
jstage_client = JStageClient()

def jstage_search_monitor():
    """
    J-STAGE APIを定期的に検索し、新しい論文が見つかったら
    パイプライン1のジョブを投入する。
    """
    print("[J-STAGE Monitor] 論文の自動検索を開始します...")
    processed_dois = set()

    try:
        with open(PROCESSED_JSTAGE_LOG, 'r', encoding='utf-8') as f:
            processed_dois = set(line.strip() for line in f)
        print(f"[J-STAGE Monitor] {len(processed_dois)}件の処理済みDOIをログから読み込みました。")
    except FileNotFoundError:
        pass

    while True:
        print("\n" + "="*50)
        print(f"[{time.ctime()}] 定期的な論文検索を実行します...")
        
        for keyword in SEARCH_KEYWORDS:
            articles = jstage_client.search_articles(keyword, count=20) # 各キーワードで最大20件
            
            for article in articles:
                doi = article.get('doi')
                if doi not in processed_dois:
                    print(f"[J-STAGE Monitor] 新規論文を発見: {article['title']}")
                    
                    job_data = {
                        'pipeline': 'rag_source',
                        'url': article['url'],
                        'metadata': {
                            'title': article['title'],
                            'doi': article['doi']
                        }
                    }
                    job_manager.add_job(job_data)
                    
                    processed_dois.add(doi)
                    with open(PROCESSED_JSTAGE_LOG, 'a', encoding='utf-8') as f:
                        f.write(doi + '\n')
        
        print(f"[{time.ctime()}] 論文検索完了。次の検索まで {SEARCH_INTERVAL_SECONDS / 60:.0f} 分待機します。")
        print("="*50 + "\n")
        time.sleep(SEARCH_INTERVAL_SECONDS)

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

def get_failed_jobs():
    """DLQログファイルを読み込み、失敗したジョブのリストを返す"""
    failed_jobs = []
    if not os.path.exists(DEAD_LETTER_QUEUE_LOG):
        return failed_jobs
    
    with open(DEAD_LETTER_QUEUE_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                failed_jobs.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"警告: DLQログの不正な行をスキップします: {line}")
    
    failed_jobs.reverse() # 新しいものを上に表示
    return failed_jobs


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


# 管理用UI
@app.route("/", methods=["GET"])
def dashboard():
    """失敗ジョブ一覧と再実行機能を追加したダッシュボード"""
    stats = job_manager.get_stats()
    failed_jobs = get_failed_jobs()

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
            setTimeout(() => { window.location.reload(); }, 10000); // 更新間隔を10秒に延長

            function resubmitJob(jobContext) {
                if (!confirm('このジョブを再実行しますか？')) {
                    return;
                }
                fetch('/resubmit-job', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jobContext)
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    window.location.reload();
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('再実行リクエストに失敗しました。');
                });
            }
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

        <h2>失敗したジョブ (Dead Letter Queue)</h2>
        {% if failed_jobs %}
            <table>
                <thead>
                    <tr>
                        <th>発生日時</th>
                        <th>パイプライン</th>
                        <th>エラー内容</th>
                        <th>アクション</th>
                    </tr>
                </thead>
                <tbody>
                    {% for job in failed_jobs %}
                    <tr>
                        <td>{{ job.timestamp }}</td>
                        <td>{{ job.pipeline_name }}</td>
                        <td><pre class="error-message">{{ job.error_info.message | tojson(indent=2) }}</pre></td>
                        <td>
                            <button onclick='resubmitJob({{ job.job_context_for_resubmit | tojson }})'>再実行</button>
                        </td>
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
    return render_template_string(html, stats=stats, failed_jobs=failed_jobs)


@app.route('/resubmit-job', methods=['POST'])
def resubmit_job():
    """失敗したジョブのコンテキストを受け取り、再度キューに投入するAPI"""
    job_context = request.json
    if not job_context:
        return jsonify({"message": "再実行するジョブのコンテキストがありません。"}), 400
    
    new_job_id = job_manager.add_job(job_context)
    message = f"ジョブを新しいID '{new_job_id}' で再投入しました。"
    print(f"[Hub] {message}")
    
    return jsonify({"message": message}), 200

# @app.route("/submit-result", methods=["POST"])
# def submit_result():
#     submission = request.json
#     job_id = submission.get("job_id")
#     status = submission.get("status")
#     pipeline = submission.get("pipeline")
#     original_job_data = job_manager.jobs.get(job_id, {}).get("data", {})

#     if not all([job_id, status, pipeline]):
#         return jsonify({"error": "job_id, status, pipelineは必須です"}), 400

#     if status == "completed":
#         result = submission.get("result", {})
#         # パイプライン2以降は、結果をファイルに保存するだけでなく、
#         # 次のステップのジョブを生成する必要があるかもしれない（将来実装）
#         saved_filename = f"{job_id}{result.get('extension', '.txt')}"
#         result_handler.save_result(job_id, pipeline, result, custom_filename=saved_filename)
#         job_manager.update_job_status(job_id, "completed")

#         # ここからが重要
#         # もし完了したのがペルソナ生成ジョブなら、次のLoRAデータ生成ジョブを作る
#         if pipeline == "persona_generation":
#             print(f"[Hub] ペルソナ生成完了({job_id})。次のLoRAデータ生成ジョブを作成します。")
#             # 元のジョブ情報から、どの論文とペルソナを組み合わせるかを知る
#             source_markdown = original_job_data.get("source_markdown")
#             generated_persona_file = saved_filename

#             if source_markdown and generated_persona_file:
#                 # ここで仕様書通り、逐次生成のジョブを投入する
#                 # まずは最初のステップ（CurrentAssessment）のジョブだけを投入
#                 lora_job_data = {
#                     "pipeline": "lora_data_generation",
#                     "source_markdown": source_markdown,
#                     "source_persona": generated_persona_file,
#                     "target_step": 0,  # 生成グループのインデックス (0 = CurrentAssessment)
#                     "previous_results": {},  # 最初のステップなので空
#                 }
#                 job_manager.add_job(lora_job_data)
#             else:
#                 print("[Hub] 警告: LoRAジョブの作成に必要な情報が不足しています。")

#     elif status == "failed":
#         error_info = submission.get("error", {})
#         result_handler.save_error(job_id, pipeline, error_info)
#         job_manager.update_job_status(job_id, "failed", message=error_info.get("message"))

#     return jsonify({"message": "結果受理"}), 200


@app.route('/submit-result', methods=['POST'])
def submit_result():
    submission = request.json
    job_id = submission.get('job_id')
    status = submission.get('status')
    pipeline = submission.get('pipeline')
    original_job_data = job_manager.jobs.get(job_id, {}).get('data', {})

    if not all([job_id, status, pipeline]):
        return jsonify({"error": "job_id, status, pipelineは必須です"}), 400

    if status == 'completed':
        result = submission.get('result', {})
        
        custom_filename = None
        if result.get('extension') != '.jsonl':
             custom_filename = f"{job_id}{result.get('extension', '.txt')}"
        result_handler.save_result(job_id, pipeline, result, custom_filename=custom_filename)
        
        job_manager.update_job_status(job_id, 'completed')

        if pipeline == 'persona_generation':
            handle_persona_completion(original_job_data, custom_filename)
        
        elif pipeline == 'lora_data_generation':
            handle_lora_step_completion(original_job_data, result)


    elif status == 'failed':
        error_info = submission.get('error', {})
        result_handler.save_error(job_id, pipeline, error_info, original_job_data)
        job_manager.update_job_status(job_id, 'failed', message=error_info.get('message'))
    
    return jsonify({"message": "結果受理"}), 200


# def handle_persona_completion(original_job_data, saved_persona_filename):
#     """ペルソナ生成が完了した後の処理"""
#     print("[Hub] ペルソナ生成完了。LoRAデータ生成の最初のステップを開始します。")
#     source_markdown = original_job_data.get("source_markdown")

#     if source_markdown and saved_persona_filename:
#         lora_job_data = {
#             "pipeline": "lora_data_generation",
#             "source_markdown": source_markdown,
#             "source_persona": saved_persona_filename,
#             "target_step": 0,
#             "previous_results": {},
#         }
#         job_manager.add_job(lora_job_data)
#     else:
#         print("[Hub] 警告: LoRAジョブ作成に必要な情報が不足しています。")


def handle_persona_completion(original_job_data, saved_persona_filename):
    """ペルソナ生成が完了した後の処理"""
    source_markdown = original_job_data.get('source_markdown')
    if not source_markdown or not saved_persona_filename:
        print(f"[Hub] 警告: 次のステップのジョブ作成に必要な情報が不足しています。")
        return

    # --- LoRAデータ生成の最初のステップ(0番目)を開始 ---
    print(f"[Hub] ペルソナ生成完了。LoRAデータ生成の最初のステップを開始します。")
    lora_job_data = {
        'pipeline': 'lora_data_generation',
        'source_markdown': source_markdown,
        'source_persona': saved_persona_filename,
        'target_step': 0, # 設計図の0番目からスタート
        'previous_results': {},
    }
    job_manager.add_job(lora_job_data)

    # --- 情報抽出(Parser)用データ生成ジョブも並行して開始 ---
    print(f"[Hub] 同時に、情報抽出(Parser)用データ生成ジョブも開始します。")
    parser_job_data = {
        'pipeline': 'parser_finetune',
        'source_markdown': source_markdown,
        'source_persona': saved_persona_filename,
    }
    job_manager.add_job(parser_job_data)


def handle_lora_step_completion(original_job_data, worker_result):
    """【新版】LoRAデータ生成の1項目が完了した後の処理"""
    next_step_data = worker_result.get('next_step_data', {})
    next_step = next_step_data.get('next_step')

    # 設計図(SEQUENTIAL_GENERATION_ORDER)の最後まで到達したかチェック
    if next_step is not None and next_step < len(SEQUENTIAL_GENERATION_ORDER):
        print(f"[Hub] LoRAステップ {next_step - 1} 完了。次のステップ {next_step} のジョブを作成します。")
        
        # これまでの生成結果をすべて引き継ぐ
        all_previous_results = original_job_data.get('previous_results', {})
        newly_generated_items = next_step_data.get('generated_items', {})
        all_previous_results.update(newly_generated_items)

        # 次のステップのジョブを作成
        next_lora_job_data = {
            'pipeline': 'lora_data_generation',
            'source_markdown': original_job_data.get('source_markdown'),
            'source_persona': original_job_data.get('source_persona'),
            'target_step': next_step,
            'previous_results': all_previous_results,
        }
        job_manager.add_job(next_lora_job_data)
    else:
        # 全項目が完了
        print(f"[Hub] ★★★ LoRA 全項目({len(SEQUENTIAL_GENERATION_ORDER)}件)の逐次生成が完了しました。 ★★★ (Source: {original_job_data.get('source_markdown')})")


# サーバーの起動
if __name__ == "__main__":
    host = os.getenv("HUB_HOST", "127.0.0.1")
    port = int(os.getenv("HUB_PORT", 5000))

    # フォルダ監視スレッドをバックグラウンドで開始
    md_monitor = threading.Thread(target=markdown_folder_monitor, daemon=True)
    md_monitor.start()

    jstage_monitor = threading.Thread(target=jstage_search_monitor, daemon=True)
    jstage_monitor.start()

    app.run(host=host, port=port, debug=False)
