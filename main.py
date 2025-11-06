import sys
import os
import argparse  # argparse をインポート
from dotenv import load_dotenv

# 定義を run_pipeline_1_rag_source.py から移動
DEFAULT_SEARCH_COUNT_PER_KEYWORD = 800 # 実験用に20のまま
DEFAULT_MAX_QUERIES = 5000
DEFAULT_MAX_PAPERS_PER_KEYWORD = 1000 # 実験用に20のまま

# search_keywords.py のリスト名と、引数で使う短い名前を対応させる
KEYWORD_LIST_MAP = {
    "m": "MAIN_DISEASE_KEYWORDS",
    "s": "SURGERY_PROCEDURE_KEYWORDS",
    "c": "COMPLICATION_SEQUELAE_KEYWORDS",
    "ph": "PHASE_KEYWORDS",
    "po": "PATIENT_POPULATION_KEYWORDS",
    "g": "GOAL_KEYWORDS",
    "e": "EVALUATION_KEYWORDS",
    "t": "REHAB_TECHNIQUE_KEYWORDS",
    "mo": "REHAB_MODALITY_KEYWORDS",
}


def check_api_key():
    """GEMINI_API_KEYが設定されているか確認"""
    load_dotenv()
    if os.getenv("GEMINI_API_KEY") is None or os.getenv("GEMINI_API_KEY") == "YOUR_GOOGLE_API_KEY_HERE":
        print("エラー: .env ファイルに GEMINI_API_KEY が設定されていません。")
        print("https://ai.google.dev/gemini-api/docs/api-key?hl=ja を参考にAPIキーを取得し、.envファイルを作成してください。")
        sys.exit(1)


def main():
    """
    データセット生成のメインスクリプト。
    argparse を使用して実行するパイプラインを選択します。
    """
    # 1. メインのパーサーを作成
    parser = argparse.ArgumentParser(description="データセット生成スクリプト")
    # 2. サブコマンド（サブパーサー）を追加
    subparsers = parser.add_subparsers(dest="command", required=True, help="実行するコマンド")

    # 3. "p1" コンドのパーサーを作成
    parser_p1 = subparsers.add_parser("p1", help="論文を収集し、RAG用Markdownを生成する")
    parser_p1.add_argument(
        "--count",
        type=int,
        default=DEFAULT_SEARCH_COUNT_PER_KEYWORD,
        help=f"1回のリクエスト（1ページ）あたりの最大検索件数 (API上限1000, デフォルト: {DEFAULT_SEARCH_COUNT_PER_KEYWORD})",
    )
    parser_p1.add_argument(
        "--max-papers-per-keyword",
        type=int,
        default=DEFAULT_MAX_PAPERS_PER_KEYWORD,
        help=f"1つのキーワードで取得する論文の総数の上限 (デフォルト: {DEFAULT_MAX_PAPERS_PER_KEYWORD})",
    )
    
    parser_p1.add_argument(
        "--max-queries",
        type=int,
        default=DEFAULT_MAX_QUERIES,
        help=f"1回の実行で処理する最大クエリ数 (デフォルト: {DEFAULT_MAX_QUERIES})",
    )

    parser_p1.add_argument(
        "--query-mode",
        type=str,
        default="single",
        choices=["single", "combination"],
        help=(
            "検索クエリの生成モードを選択 (default: single)。"
            "'single': --keyword-lists で指定されたリストの単一キーワードのみ（安全・推奨）。"
            "'combination': 全リストのキーワードを総当たりで組み合わせる（非推奨・IPブロックのリスク有）。"
        ),
    )
    parser_p1.add_argument(
        "--keyword-lists",
        nargs="+",  # 1つ以上の引数をリストとして受け取る
        default=["m", "s"],
        choices=["all"] + list(KEYWORD_LIST_MAP.keys()),
        help=(
            f"singleモード時に使用するキーワードリスト (default: m s)。"
            f"'all' ですべてのリストを選択可能。選択肢: {list(KEYWORD_LIST_MAP.keys())}"
        ),
    )

    parser_p1.add_argument(
        "--resume",
        action="store_true",  # この引数が指定されると True になる
        help="中断した箇所から処理を再開します。'output/pipeline_1_processed_keywords.log' を参照します。"
    )

    # 4. "p234" コマンドのパーサーを作成
    subparsers.add_parser("p234", help="既存のMarkdownから各種データセット(P2, P3, P4)を生成する")

    # 5. 引数を解析
    args = parser.parse_args()

    # APIキーのチェックを一度だけ実行
    check_api_key()

    # 6. コマンドに基づいて処理を分岐
    if args.command == "p1":
        print("[メイン] パイプライン1 (RAGソース生成) を開始します...")
        try:
            import run_pipeline_1_rag_source

            # main(args) の代わりに、リネームした run(args) を呼び出す
            # argparse が解析した args オブジェクトをそのまま渡す
            run_pipeline_1_rag_source.run(args, KEYWORD_LIST_MAP) # 第2引数を追加
        except ImportError:
            print("エラー: run_pipeline_1_rag_source.py が見つかりません。")
            print(f"  [詳細] これが本当の原因である可能性が高いです: {e}")
        except Exception as e:
            print(f"パイプライン1の実行中に予期せぬエラーが発生しました: {e}")

    elif args.command == "p234":
        print("[メイン] パイプライン2, 3, 4 (各種データセット生成) を開始します...")
        try:
            import run_dataset_generation

            run_dataset_generation.main()
        except ImportError:
            print("エラー: run_dataset_generation.py が見つかりません。")
            print(f"  [詳細] これが本当の原因である可能性が高いです: {e}")
        except Exception as e:
            print(f"データセット生成中に予期せぬエラーが発生しました: {e}")


if __name__ == "__main__":
    main()