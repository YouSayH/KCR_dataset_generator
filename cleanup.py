import sys
import os
import glob
import re # 必要に応じてインポートを追加

def clean_single_markdown_file(filepath: str, dry_run: bool) -> bool:
    """
    単一のMarkdownファイルから、YAMLフロントマター直後の '```markdown' と、
    ファイルの最終行の '```' を安全に削除し、変更があった場合はTrueを返します。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  [エラー] ファイル読み込み中にエラーが発生しました: {e}", file=sys.stderr)
        return False

    line_to_delete_start = -1
    line_to_delete_end = -1
    
    # 1. 削除開始行 (```markdown) を特定
    yaml_delimiter_count = 0
    start_index_after_yaml = -1
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            yaml_delimiter_count += 1
            if yaml_delimiter_count == 2:
                # 2回目の '---' の次の行から検索を開始
                start_index_after_yaml = i + 1
                break

    if start_index_after_yaml != -1:
        # YAML終了行の次から、最初に見つかる非空行を探す
        for i in range(start_index_after_yaml, len(lines)):
            stripped_line = lines[i].strip()
            if stripped_line != '':
                # 見つかった非空行が '```markdown' であれば開始行として特定
                if stripped_line == '```markdown':
                    line_to_delete_start = i
                break # 最初に見つかった非空行をチェックしたらループ終了

    # 2. 削除終了行 (```) を特定
    # ファイルの末尾から逆行して最初に見つかる非空行が '```' かどうかをチェック
    for i in range(len(lines) - 1, -1, -1):
        stripped_line = lines[i].strip()
        if stripped_line != '': # 空行でなければ
            if stripped_line == '```':
                line_to_delete_end = i
            break
    
    # 3. 削除処理の実行
    if line_to_delete_start != -1 and line_to_delete_end != -1:
        # 開始と終了のパターンが両方見つかった場合のみ削除を実行
        
        print(f"  [対象] 処理対象ファイルです。")
        # 行番号は1から数えるため +1
        print(f"    - 開始行 ({line_to_delete_start + 1}): {lines[line_to_delete_start].strip()}")
        print(f"    - 終了行 ({line_to_delete_end + 1}): {lines[line_to_delete_end].strip()}")
        
        if dry_run:
            return False # ドライランなので変更なし

        # 削除処理: 開始行と終了行以外を保持する
        new_lines = []
        for i, line in enumerate(lines):
            if i != line_to_delete_start and i != line_to_delete_end:
                new_lines.append(line)

        # ファイルを上書き保存
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # 元のファイルの末尾に改行がない場合があるため、最後の行が改行で終わるか確認
                if new_lines and not new_lines[-1].endswith('\n'):
                     new_lines[-1] += '\n'
                f.writelines(new_lines)
            return True
        except Exception as e:
            print(f"  [エラー] ファイル書き込み中にエラーが発生しました: {e}", file=sys.stderr)
            return False
    else:
        # パターンに一致しない場合はスキップ
        print(f"  [スキップ] パターンに一致しないためスキップします。")
        return False
    
def main():
    # 引数リスト: 1番目の要素はスクリプト名なので、2番目以降をチェック
    args = sys.argv[1:]
    
    # ターゲットディレクトリの初期値設定
    target_dir = '.' # デフォルトはカレントディレクトリ
    
    # --dry-run オプションのチェック
    dry_run = "--dry-run" in args
    
    # ターゲットディレクトリのパスを特定
    # 引数が1つ以上あり、それがオプション (--dry-run) でない場合、それをディレクトリとする
    if len(args) > 0 and args[0] != '--dry-run':
        target_dir = args[0]
    # ただし、引数が一つでそれが --dry-run の場合はデフォルトの '.' のままにする
    # 引数が二つ以上あり、最初の引数がディレクトリ、二つ目が --dry-run の場合も最初の引数をディレクトリとする

    
    print(f"--- Markdownファイル cleanup ツール ---")
    print(f"ターゲットディレクトリ: {target_dir}")
    print(f"モード: {'ドライラン (変更なし)' if dry_run else '本番実行 (上書き保存)'}\n")
    
    # ディレクトリ内の全ての .md ファイルを検索（サブディレクトリも含む）
    # glob.globはサブディレクトリのワイルドカード検索(os.path.join(target_dir, '**', '*.md'))を
    # Windows/Linux/macOS問わず正しく実行できるようにします。
    markdown_files = glob.glob(os.path.join(target_dir, '**', '*.md'), recursive=True)
    
    if not markdown_files:
        print(f"エラー: 対象ディレクトリ '{target_dir}' にMarkdownファイルが見つかりませんでした。")
        sys.exit(1)

    print(f"合計 {len(markdown_files)} ファイルを検出しました。処理を開始します...")
    
    processed_count = 0
    modified_count = 0
    
    for i, filepath in enumerate(markdown_files):
        # パスが絶対パスでない場合に備えて正規化
        relative_path = os.path.relpath(filepath, start=target_dir)
        print(f"\n[{i+1}/{len(markdown_files)}] {relative_path}: ", end="")
        
        # 個別ファイルの処理
        modified = clean_single_markdown_file(filepath, dry_run)
        
        processed_count += 1
        if modified:
            modified_count += 1
            
    print("\n------------------------------------")
    print("処理が完了しました。")
    print(f"合計処理ファイル数: {processed_count}")
    if dry_run:
        print(f"削除パターンに一致したファイル数: {modified_count} (※ドライランのためファイル変更なし)")
    else:
        print(f"実際に変更・上書き保存したファイル数: {modified_count}")
    print("------------------------------------")

if __name__ == "__main__":
    main()