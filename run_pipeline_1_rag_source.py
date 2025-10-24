import os
import time
import itertools
import logging
import random

from utils.jstage_client import JStageClient
from pipelines.pipeline_1_rag_source import process_pipeline_1
from core.result_handler import ResultHandler
import search_keywords as kw

# 定数
# 出力先
RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
PROCESSED_JSTAGE_LOG = os.path.join("output", "processed_jstage_dois.log")
PROCESSED_KEYWORDS_LOG = os.path.join("output", "pipeline_1_processed_keywords.log") # パスを output 内に修正

# APIリクエスト間のスリープ時間（秒）
SEARCH_API_SLEEP = 1.0
PROCESS_DOI_SLEEP = 1.0

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("pipeline_1.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def load_processed_dois(log_path: str) -> set:
    """処理済みのDOIをログファイルから読み込む"""
    processed_dois = set()
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            processed_dois = set(line.strip() for line in f)
        logger.info(f"[P1] {len(processed_dois)}件の処理済みDOIをログから読み込みました。")
    except FileNotFoundError:
        logger.warning("[P1] 処理済みDOIログファイルが見つかりません。新規に作成します。")
    return processed_dois


def log_processed_doi(log_path: str, doi: str):
    """処理済みのDOIをログファイルに追記する"""
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(doi + "\n")


def load_processed_keywords(log_path: str) -> set:
    """処理済みのキーワードをログファイルから読み込む"""
    processed_keywords = set()
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            processed_keywords = set(line.strip() for line in f)
        logger.info(f"[P1] {len(processed_keywords)}件の処理済みキーワードをログから読み込みました。")
    else:
        logger.info("[P1] 処理済みキーワードログファイルが見つかりません。新規に作成します。")
    return processed_keywords


def log_processed_keyword(log_path: str, keyword: str):
    """処理済みのキーワードをログファイルに追記する"""
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(keyword + "\n")


def get_queries_to_run(args, keyword_list_map, processed_keywords: set) -> list:
    """
    コマンドライン引数に基づいて実行対象の検索クエリリストを生成する。
    処理済みのキーワードは除外する。
    """
    logger.info("[P1] 実行対象の検索クエリを準備中...")

    target_list_names = []
    if 'all' in args.keyword_lists:
        target_list_names = list(keyword_list_map.keys())
        logger.info("[P1] ... 'all' が指定されたため、すべてのキーワードリストを定義順に使用します。")
    else:
        target_list_names = args.keyword_lists
        logger.info(f"[P1] ... 対象リスト: {target_list_names}")

    # 順序を保持するため、setではなくlistを使用する
    ordered_queries = []
    for short_name in target_list_names:
        list_variable_name = keyword_list_map.get(short_name)
        if list_variable_name:
            keyword_list = getattr(kw, list_variable_name, [])
            ordered_queries.extend(keyword_list)  # extendでリストの順序を維持したまま追加
            logger.info(f"[P1] ... '{list_variable_name}' から {len(keyword_list)} 件のキーワードを追加。")
        else:
            logger.warning(f"[P1] ... 不明なリスト名: {short_name}")

    # 重複を削除しつつ、順序は保持する
    unique_ordered_queries = list(dict.fromkeys(ordered_queries))
    total_unique_queries = len(unique_ordered_queries)
    logger.info(f"[P1] 重複を除いた合計 {total_unique_queries} 件のユニークなクエリを生成しました。")

    # シャッフルロジックを完全に削除
    logger.info("[P1] キーワードリストの定義順で実行します。")

    # --- 処理済みキーワードの除外 ---
    if processed_keywords:
        queries_to_run = [q for q in unique_ordered_queries if q not in processed_keywords]
        skipped_count = total_unique_queries - len(queries_to_run)
        logger.info(f"[P1] ログに基づき、処理済みのキーワード {skipped_count} 件をスキップします。")
    else:
        queries_to_run = unique_ordered_queries

    logger.info(f"[P1] 今回の実行対象クエリは {len(queries_to_run)} 件です。")
    return queries_to_run


def run_search_loop(
    queries_to_run: list,
    jstage_client: JStageClient,
    result_handler: ResultHandler,
    gemini_api_key: str,
    processed_dois: set,
    search_count: int, # 1ページあたりの取得件数 (args.count)
    max_papers_per_keyword: int # 1キーワードあたりの総取得上限 (args.max_papers_per_keyword)
):
    """
    生成されたクエリリストに基づいて検索と処理のメインループを実行する
    """
    total_queries = len(queries_to_run)
    new_files_created = 0

    for i, query in enumerate(queries_to_run):
        logger.info(f"\n[P1] ({i + 1}/{total_queries}) クエリ実行中: '{query}'")

        # 実行しようとしているキーワードをログに記録
        log_processed_keyword(PROCESSED_KEYWORDS_LOG, query)
        
        start_index = 1
        total_hits_for_this_query = 0 # このクエリの総ヒット数（初回APIで設定）
        
        # ページネーションループ
        while True:
            # 1. ユーザー指定の総取得上限を超えていたら、このキーワードは終了
            if start_index > max_papers_per_keyword:
                logger.info(f"  -> ユーザー指定の上限 ({max_papers_per_keyword}件) に達したため、このクエリを終了します。")
                break
                
            # 2. (初回ループ以外で) APIの総ヒット数を超えていたら、このキーワードは終了
            if total_hits_for_this_query > 0 and start_index > total_hits_for_this_query:
                logger.info(f"  -> APIの総ヒット数 ({total_hits_for_this_query}件) に達したため、このクエリを終了します。")
                break

            logger.info(f"  -> ページ取得中 (開始位置: {start_index} / 1ページの件数: {search_count})")
            
            try:
                # jstage_client.search_articles が (articles, total_hits) を返す
                articles, total_hits = jstage_client.search_articles(
                    query, 
                    count=search_count, # 1ページあたりの件数
                    start=start_index   # 開始位置
                )
                
                if start_index == 1: # 最初のループでのみ総ヒット数を記録
                    total_hits_for_this_query = total_hits
                    if total_hits == 0:
                        logger.info("  -> 論文が見つかりませんでした。")
                        break # このクエリの処理を終了

                time.sleep(SEARCH_API_SLEEP)

            except Exception as search_e:
                logger.error(f"  -> !! 検索エラー: クエリ '{query}' (開始位置 {start_index}) で失敗しました。詳細: {search_e}")
                break # このクエリの処理を終了

            if not articles:
                logger.info("  -> このページの論文が見つかりませんでした。クエリを終了します。")
                break # ページネーションループを終了

            # 取得した論文リストの処理 (既存ロジック)
            for article in articles:
                doi = article.get("doi")
                if not doi:
                    logger.warning("  -> スキップ (DOIなし)")
                    continue

                safe_filename = doi.replace("/", "_") + ".md"
                markdown_path = os.path.join(RAG_SOURCE_DIR, safe_filename)

                if doi in processed_dois or os.path.exists(markdown_path):
                    logger.info(f"  -> スキップ (既存): {doi}")
                    if doi not in processed_dois:
                         log_processed_doi(PROCESSED_JSTAGE_LOG, doi) # 念のためログにも記録
                    continue

                logger.info(f"  -> 新規処理: {article['title']} ({doi})")


                job_data = {
                    "pipeline": "rag_source",
                    "url": article.get("url", ""), # Use .get for safety
                    "metadata": {
                        "title": article.get("title", "N/A"), # Use .get for safety
                        "doi": doi,
                        "journal": article.get("journal", "N/A"), # ★追加★
                        "published_date": article.get("published_date", "N/A") # ★追加★
                    },
                }

                try:
                    result_content = process_pipeline_1(job_data, gemini_api_key)
                    result_handler.save_result(
                        job_id=f"p1_{safe_filename}", pipeline_name="rag_source",
                        result_data=result_content, custom_filename=safe_filename,
                    )
                    log_processed_doi(PROCESSED_JSTAGE_LOG, doi)
                    processed_dois.add(doi)
                    new_files_created += 1
                    time.sleep(PROCESS_DOI_SLEEP)
                except Exception as e:
                    logger.error(f"  -> !! 処理エラー: {doi} の処理中に失敗しました。詳細: {e}")
            
            # ループ継続判定: 次の開始位置を計算
            start_index += search_count

    return new_files_created


def run(args, keyword_list_map):
    """
    パイプライン1（RAGソース生成）を実行します。
    """
    logger.info("[P1] J-STAGE論文の検索とRAGソースの生成を開始します...")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.error("[P1] エラー: GEMINI_API_KEYが設定されていません。")
        return

    os.makedirs(RAG_SOURCE_DIR, exist_ok=True)

    # resumeオプションがない場合は、キーワード進捗ログをリセットする
    if not args.resume and os.path.exists(PROCESSED_KEYWORDS_LOG):
        os.remove(PROCESSED_KEYWORDS_LOG)
        logger.info(f"[P1] --resumeオプションがないため、キーワード進捗ログ '{PROCESSED_KEYWORDS_LOG}' をリセットしました。")

    processed_dois = load_processed_dois(PROCESSED_JSTAGE_LOG)
    processed_keywords = load_processed_keywords(PROCESSED_KEYWORDS_LOG) if args.resume else set()

    jstage_client = JStageClient()
    result_handler = ResultHandler(base_output_dir="output")

    all_queries_list = get_queries_to_run(args, keyword_list_map, processed_keywords)

    max_queries = args.max_queries
    if max_queries <= 0 or len(all_queries_list) < max_queries:
        max_queries = len(all_queries_list)
        if len(all_queries_list) == 0:
            logger.info("[P1] 実行対象の検索クエリが0件です。処理を終了します。")
            return
        logger.info(f"全 {max_queries} 件のクエリを実行します。")
    else:
        logger.info(f"全 {len(all_queries_list)} 件のクエリから、先頭 {max_queries} 件を実行します。")

    queries_to_run = all_queries_list[:max_queries]

    new_files_created = run_search_loop(
        queries_to_run=queries_to_run,
        jstage_client=jstage_client,
        result_handler=result_handler,
        gemini_api_key=gemini_api_key,
        processed_dois=processed_dois,
        search_count=args.count,
        max_papers_per_keyword=args.max_papers_per_keyword
    )

    logger.info("\n" + "=" * 50)
    logger.info("パイプライン1 実行完了")
    logger.info(f"新規作成ファイル数: {new_files_created} 件")
    logger.info(f"RAGソースフォルダ: {RAG_SOURCE_DIR}")
    logger.info("=" * 50)

