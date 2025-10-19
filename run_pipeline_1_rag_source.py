import os
import time
import itertools
import logging
import random
# 削除: import argparse
# 削除: from dotenv import load_dotenv

from utils.jstage_client import JStageClient
from pipelines.pipeline_1_rag_source import process_pipeline_1
from core.result_handler import ResultHandler
import search_keywords as kw

# --- 定数 ---
# 削除: デフォルト設定 (main.py へ移動)

# 出力先
RAG_SOURCE_DIR = "output/pipeline_1_rag_source"
PROCESSED_JSTAGE_LOG = "output/processed_jstage_dois.log"

# APIリクエスト間のスリープ時間（秒）
SEARCH_API_SLEEP = 1.0
PROCESS_DOI_SLEEP = 1.0

# --- ロギング設定 ---
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


def generate_search_queries() -> set:
    """
    キーワードリストを組み合わせて検索クエリのセットを生成する
    """
    logger.info("[P1] 検索クエリを生成中...")
    queries = set()

    # === 1. "アンカー"となる単体キーワードの追加 ===
    logger.info("[P1] ... (1/4) 疾患・術式名の単体キーワードを追加中")
    queries.update(kw.MAIN_DISEASE_KEYWORDS)
    queries.update(kw.SURGERY_PROCEDURE_KEYWORDS)

    # === 2. "アンカー" x "モディファイア" の組み合わせ (AND検索) ===
    logger.info("[P1] ... (2/4) [アンカー] x [モディファイア] の組み合わせを生成中")

    anchor_lists = [kw.MAIN_DISEASE_KEYWORDS, kw.SURGERY_PROCEDURE_KEYWORDS]
    modifier_lists = [
        kw.COMPLICATION_SEQUELAE_KEYWORDS,
        kw.PHASE_KEYWORDS,
        kw.PATIENT_POPULATION_KEYWORDS,
        kw.GOAL_KEYWORDS,
        kw.EVALUATION_KEYWORDS,
        kw.REHAB_TECHNIQUE_KEYWORDS,
        kw.REHAB_MODALITY_KEYWORDS,
    ]

    for anchor_list in anchor_lists:
        for modifier_list in modifier_lists:
            for combo in itertools.product(anchor_list, modifier_list):
                queries.add(f"{combo[0]} {combo[1]}")  # J-Stageはスペース区切りでAND検索

    # === 3. "メイン疾病" x "メイン疾病" の組み合わせ ===
    logger.info("[P1] ... (3/4) [メイン疾病] x [メイン疾病] の組み合わせ（併発）を生成中")
    for combo in itertools.combinations(kw.MAIN_DISEASE_KEYWORDS, 2):
        queries.add(f"{combo[0]} {combo[1]}")

    logger.info(f"[P1] ... (4/4) クエリのユニーク化完了。合計 {len(queries)} 件のクエリを生成しました。")
    return queries


def run_search_loop(
    queries_to_run: list,
    jstage_client: JStageClient,
    result_handler: ResultHandler,
    gemini_api_key: str,
    processed_dois: set,
    search_count: int,
):
    """
    生成されたクエリリストに基づいて検索と処理のメインループを実行する
    (main関数から分離)
    """
    total_queries = len(queries_to_run)
    new_files_created = 0

    for i, query in enumerate(queries_to_run):
        logger.info(f"\n[P1] ({i + 1}/{total_queries}) クエリ実行中: '{query}'")

        try:
            articles = jstage_client.search_articles(query, count=search_count)
            # 【リファクタリング点】検索APIへの負荷軽減
            time.sleep(SEARCH_API_SLEEP)

        except Exception as search_e:
            logger.error(f"  -> !! 検索エラー: クエリ '{query}' で失敗しました。詳細: {search_e}")
            continue  # 次のクエリへ

        if not articles:
            logger.info("  -> 論文が見つかりませんでした。")
            continue

        for article in articles:
            doi = article.get("doi")
            if not doi:
                logger.warning("  -> スキップ (DOIなし)")
                continue

            safe_filename = doi.replace("/", "_") + ".md"
            markdown_path = os.path.join(RAG_SOURCE_DIR, safe_filename)

            # --- 差分実行チェック ---
            if doi in processed_dois:
                logger.debug(f"  -> スキップ (ログ): {doi}")  # ログレベルをdebugに変更
                continue

            if os.path.exists(markdown_path):
                logger.info(f"  -> スキップ (既存): {safe_filename}")
                log_processed_doi(PROCESSED_JSTAGE_LOG, doi)
                processed_dois.add(doi)
                continue

            # --- 新規処理 ---
            logger.info(f"  -> 新規処理: {article['title']} ({doi})")

            job_data = {
                "pipeline": "rag_source",
                "url": article["url"],
                "metadata": {"title": article["title"], "doi": article["doi"]},
            }

            try:
                result_content = process_pipeline_1(job_data, gemini_api_key)

                result_handler.save_result(
                    job_id=f"p1_{safe_filename}",
                    pipeline_name="rag_source",
                    result_data=result_content,
                    custom_filename=safe_filename,
                )

                log_processed_doi(PROCESSED_JSTAGE_LOG, doi)
                processed_dois.add(doi)
                new_files_created += 1

                # PDFダウンロード等へのAPI負荷軽減
                time.sleep(PROCESS_DOI_SLEEP)

            except Exception as e:
                logger.error(f"  -> !! 処理エラー: {doi} の処理中に失敗しました。詳細: {e}")

    return new_files_created


def run(args):
    """
    パイプライン1（RAGソース生成）を実行します。
    main.py から呼び出されることを前提とします。
    """
    logger.info("[P1] J-STAGE論文の検索とRAGソースの生成を開始します...")

    # APIキーは main.py でロード済みのため、os.getenv で取得するだけ
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    # (main.pyでチェック済みだが、念のため二重チェック)
    if not gemini_api_key:
        logger.error("[P1] エラー: GEMINI_API_KEYが設定されていません。")
        return

    os.makedirs(RAG_SOURCE_DIR, exist_ok=True)

    jstage_client = JStageClient()
    result_handler = ResultHandler(base_output_dir="output")

    processed_dois = load_processed_dois(PROCESSED_JSTAGE_LOG)

    all_queries = generate_search_queries()
    all_queries_list = list(all_queries)
    random.shuffle(all_queries_list)

    # --- 引数の取得元を args オブジェクトに変更 ---
    max_queries = args.max_queries
    if len(all_queries_list) < max_queries:
        max_queries = len(all_queries_list)
        logger.info(f"生成クエリ総数が --max-queries 未満のため、全 {max_queries} 件のクエリを実行します。")
    else:
        logger.info(f"全 {len(all_queries_list)} 件のクエリから {max_queries} 件をランダムにサンプリングして実行します。")

    queries_to_run = all_queries_list[:max_queries]

    new_files_created = run_search_loop(
        queries_to_run=queries_to_run,
        jstage_client=jstage_client,
        result_handler=result_handler,
        gemini_api_key=gemini_api_key,
        processed_dois=processed_dois,
        search_count=args.count,  # args.count から取得
    )

    logger.info("\n" + "=" * 50)
    logger.info("パイプライン1 実行完了")
    logger.info(f"新規作成ファイル数: {new_files_created} 件")
    logger.info(f"RAGソースフォルダ: {RAG_SOURCE_DIR}")
    logger.info("=" * 50)
