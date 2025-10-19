# main.py (リファクタリング後)
import sys
import os
import argparse  # argparse をインポート
from dotenv import load_dotenv

# --- 定義を run_pipeline_1_rag_source.py から移動 ---
DEFAULT_SEARCH_COUNT_PER_KEYWORD = 10
DEFAULT_MAX_QUERIES = 5000


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

    # 3. "p1" コマンドのパーサーを作成
    parser_p1 = subparsers.add_parser("p1", help="論文を収集し、RAG用Markdownを生成する")
    parser_p1.add_argument(
        "--count",
        type=int,
        default=DEFAULT_SEARCH_COUNT_PER_KEYWORD,
        help=f"1クエリあたりの最大検索件数 (デフォルト: {DEFAULT_SEARCH_COUNT_PER_KEYWORD})",
    )
    parser_p1.add_argument(
        "--max-queries",
        type=int,
        default=DEFAULT_MAX_QUERIES,
        help=f"1回の実行で処理する最大クエリ数 (デフォルト: {DEFAULT_MAX_QUERIES})",
    )

    # 4. "p234" コマンドのパーサーを作成
    subparsers.add_parser("p234", help="既存のMarkdownから各種データセット(P2, P3, P4)を生成する")

    # 5. 引数を解析
    args = parser.parse_args()

    # --- APIキーのチェックを一度だけ実行 ---
    check_api_key()

    # 6. コマンドに基づいて処理を分岐
    if args.command == "p1":
        print("[メイン] パイプライン1 (RAGソース生成) を開始します...")
        try:
            import run_pipeline_1_rag_source

            # main(args) の代わりに、リネームした run(args) を呼び出す
            # argparse が解析した args オブジェクトをそのまま渡す
            run_pipeline_1_rag_source.run(args)
        except ImportError:
            print("エラー: run_pipeline_1_rag_source.py が見つかりません。")
        except Exception as e:
            print(f"パイプライン1の実行中に予期せぬエラーが発生しました: {e}")

    elif args.command == "p234":
        print("[メイン] パイプライン2, 3, 4 (各種データセット生成) を開始します...")
        try:
            import run_dataset_generation

            run_dataset_generation.main()
        except ImportError:
            print("エラー: run_dataset_generation.py が見つかりません。")
        except Exception as e:
            print(f"データセット生成中に予期せぬエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
