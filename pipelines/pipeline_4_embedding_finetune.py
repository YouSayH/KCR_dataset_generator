import os
import re
import json
import random
from rank_bm25 import BM25Okapi

# --- 設定 ---
INPUT_DIR = "output/pipeline_1_rag_source"
OUTPUT_DIR = "output/pipeline_4_embedding_finetune"
OUTPUT_FILENAME = "triplets.jsonl"
MIN_PARAGRAPH_LENGTH = 20 # この文字数未満の段落はpositiveとして採用しない
SHORT_PARAGRAPH_THRESHOLD = 50 # この文字数未満の段落は短いと判断
EXCLUDED_HEADERS = ["要旨", "はじめに", "おわりに", "まとめ", "結論"] # 除外する一般的な見出し

def extract_positive_pairs(directory: str) -> tuple[list[tuple[str, str]], list[str]]:
    """
    Markdownファイル群から [見出し, 段落] のペアを抽出する。
    
    Returns:
        (positive_pairs, corpus): 
            - positive_pairs: (query, positive) のタプルのリスト
            - corpus: positiveとして抽出された全段落のリスト
    """
    print(f"'{directory}' から正解ペアを抽出中...")
    positive_pairs = []
    corpus = []

    if not os.path.exists(directory):
        print(f"警告: 入力ディレクトリ '{directory}' が存在しません。")
        return [], []

    for filename in os.listdir(directory):
        if not filename.endswith(".md"):
            continue
        
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # YAMLフロントマターをスキップ
        if content.startswith('---'):
            end_marker = content.find('---', 3)
            if end_marker != -1:
                content = content[end_marker + 3:]

        # H2, H3, H4の見出しで分割
        # re.splitは区切り文字もリストに含めるため、(見出し, 本文) のペアを作りやすい
        sections = re.split(r'\n(##|###|####)\s', content)
        
        # 最初のセクション（見出しの前）は無視し、見出しと本文のペアを処理
        for i in range(1, len(sections), 2):
            header = sections[i+1].split('\n', 1)[0].strip()
            body = sections[i+1].split('\n', 1)[1] if '\n' in sections[i+1] else ""
            
            if header in EXCLUDED_HEADERS:
                continue

            
            paragraphs = [p.strip() for p in body.strip().split('\n\n') if p.strip()]
            if not paragraphs:
                continue
                
            first_paragraph = paragraphs[0]
            
            # 段落が短い場合に次の段落と結合
            if len(first_paragraph) < SHORT_PARAGRAPH_THRESHOLD and len(paragraphs) > 1:
                positive_text = first_paragraph + " " + paragraphs[1]
            else:
                positive_text = first_paragraph

            if len(positive_text) >= MIN_PARAGRAPH_LENGTH:
                query = header
                positive = positive_text.replace('\n', ' ')
                
                positive_pairs.append((query, positive))
                corpus.append(positive)

    print(f"-> {len(positive_pairs)} 件の正解ペアを抽出しました。")
    return positive_pairs, corpus

def main():
    """
    パイプライン4のメイン処理を実行する。
    """
    # --- 1. 正解ペア [query, positive] の全件抽出 ---
    positive_pairs, corpus = extract_positive_pairs(INPUT_DIR)
    if not positive_pairs:
        print("処理対象のMarkdownファイルが見つからなかったため、処理を終了します。")
        return

    # --- 2. Hard Negative MiningのためのBM25インデックス構築 ---
    print("Hard Negative MiningのためのBM25インデックスを構築中...")
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    print("-> インデックス構築完了。")

    # --- 3. トリプレット [query, positive, negative] の生成と保存 ---
    print("トリプレットを生成し、ファイルに保存中...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    
    count = 0
    with open(output_filepath, 'w', encoding='utf-8') as f:
        for query, positive in positive_pairs:
            tokenized_query = query.split(" ")
            
            # BM25でキーワードが似ている上位10件のドキュメントを取得
            top_10_docs = bm25.get_top_n(tokenized_query, corpus, n=10)
            
            # 上位10件から、正解文(positive)そのものを除外
            hard_negatives_pool = [doc for doc in top_10_docs if doc != positive]
            
            negative = None
            if hard_negatives_pool:
                # 候補があれば、その中からランダムに1つ選ぶ
                negative = random.choice(hard_negatives_pool)
            else:
                # 候補がなければ（非常に稀なケース）、コーパス全体からランダムに選ぶ
                # ただし、positive自体は選ばないようにする
                temp_corpus = [doc for doc in corpus if doc != positive]
                if temp_corpus:
                    negative = random.choice(temp_corpus)

            if negative:
                triplet = {
                    "query": query,
                    "positive": positive,
                    "negative": negative
                }
                f.write(json.dumps(triplet, ensure_ascii=False) + '\n')
                count += 1

    print(f"-> {count} 件のトリプレットを '{output_filepath}' に保存しました。")
    print("\nパイプライン4の処理が完了しました。")


if __name__ == '__main__':
    # `rank_bm25`が`requirements.txt`に含まれていることを確認してください
    main()