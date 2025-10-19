承知いたしました。キャンバスではなく、こちらのチャットで回答します。

先ほど作成した `README.md` の目次のリンクが正しく機能していなかったため、修正したものを改めてこちらに記載します。

-----

# KCR Dataset Generator

リハビリテーション実施計画書を自動生成するAI（ローカルSLM）のファインチューニングに必要な、高品質なデータセットを体系的に自動生成するためのツールです。

## 目次

  - [1. はじめに](https://www.google.com/search?q=%231-%E3%81%AF%E3%81%98%E3%82%81%E3%81%AB)
  - [2. アーキテクチャ](https://www.google.com/search?q=%232-%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3)
  - [3. セットアップ](https://www.google.com/search?q=%233-%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97)
      - [前提条件](https://www.google.com/search?q=%23%E5%89%8D%E6%8F%90%E6%9D%A1%E4%BB%B6)
      - [手順](https://www.google.com/search?q=%23%E6%89%8B%E9%A0%86)
  - [4. 使い方 - ワークフロー](https://www.google.com/search?q=%234-%E4%BD%BF%E3%81%84%E6%96%B9---%E3%83%AF%E3%83%BC%E3%82%AF%E3%83%95%E3%83%AD%E3%83%BC)
      - [ステップ 1: RAGソースの生成 (p1)](https://www.google.com/search?q=%23%E3%82%B9%E3%83%86%E3%83%83%E3%83%97-1-rag%E3%82%BD%E3%83%BC%E3%82%B9%E3%81%AE%E7%94%9F%E6%88%90-p1)
      - [ステップ 2: `output` フォルダの同期（手動）](https://www.google.com/search?q=%23%E3%82%B9%E3%83%86%E3%83%83%E3%83%97-2-output-%E3%83%95%E3%82%A9%E3%83%AB%E3%83%80%E3%81%AE%E5%90%8C%E6%9C%9F%E6%89%8B%E5%8B%95)
      - [ステップ 3: データセットの生成 (p234) - 作業分担](https://www.google.com/search?q=%23%E3%82%B9%E3%83%86%E3%83%83%E3%83%97-3-%E3%83%87%E3%83%BC%E3%82%BF%E3%82%BB%E3%83%83%E3%83%88%E3%81%AE%E7%94%9F%E6%88%90-p234---%E4%BD%9C%E6%A5%AD%E5%88%86%E6%8B%85)
      - [ステップ 4: 生成結果の集約（手動）](https://www.google.com/search?q=%23%E3%82%B9%E3%83%86%E3%83%83%E3%83%97-4-%E7%94%9F%E6%88%90%E7%B5%90%E6%9E%9C%E3%81%AE%E9%9B%86%E7%B4%84%E6%89%8B%E5%8B%95)
  - [5. 生成されるデータセット](https://www.google.com/search?q=%235-%E7%94%9F%E6%88%90%E3%81%95%E3%82%8C%E3%82%8B%E3%83%87%E3%83%BC%E3%82%BF%E3%82%BB%E3%83%83%E3%83%88)
  - [6. トラブルシューティング](https://www.google.com/search?q=%236-%E3%83%88%E3%83%A9%E3%83%96%E3%83%AB%E3%82%B7%E3%83%A5%E3%83%BC%E3%83%86%E3%82%A3%E3%83%B3%E3%82%B0)

## 1\. はじめに

本プロジェクトの目的は、リハビリテーション実施計画書の作成を支援するAIエンジンを、クラウドAPIから\*\*完全にローカルで動作する小規模言語モデル（SLM）\*\*へと移行させることです。そのために不可欠な、高品質なファインチューニング用データセットを体系的かつ大規模に自動生成します。

## 2\. アーキテクチャ

このツールは、各PCが独立して動作するスタンドアロン型の設計を採用しています。PC間の直接的なネットワーク連携は行わず、生成されたデータ（論文など）は手動で同期します。

プロセスは大きく分けて2つのコマンドで実行されます。

1.  **`python main.py p1`**:

      * J-STAGEからリハビリテーション関連の論文を自動で検索・収集します。
      * 収集した論文を、AIが知識源として利用しやすい構造化Markdown形式（RAGソース）に変換し、`output/pipeline_1_rag_source/` に保存します。

2.  **`python main.py p234`**:

      * `p1`で収集した論文データを元に、AIモデルの学習に必要な3種類のデータセットを生成します。
          * **P2**: 計画書の各項目を生成するためのLoRA用データセット (`output/pipeline_2_lora_finetune/`)
          * **P3**: カルテのような自由記述文から情報を抽出するためのSLM用データセット (`output/pipeline_3_parser_finetune/`)
          * **P4**: RAGの検索精度を向上させるためのEmbeddingモデル用データセット (`output/pipeline_4_embedding_finetune/`)

## 3\. セットアップ

### 前提条件

  * Python 3.10 以降

### 手順

1.  **リポジトリのクローン:**

    ```bash
    git clone <repository_url>
    cd KCR_dataset_generator
    ```

2.  **仮想環境の作成と有効化:**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windowsの場合
    # source venv/bin/activate  # macOS/Linuxの場合
    ```

3.  **依存ライブラリのインストール:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **APIキーの設定:**

      * プロジェクトのルートディレクトリに `.env` という名前のファイルを作成します。
      * ファイル内に、Google AI Studioから取得したAPIキーを以下のように記述します。
        ```
        GEMINI_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
        ```

## 4\. 使い方 - ワークフロー

### ステップ 1: RAGソースの生成 (p1)

まず、ファインチューニングの元となる論文データを収集します。この作業は1台のPC（メインのデスクトップPCなど、性能の高いマシン）で行うことを推奨します。

#### 基本的な使い方

`--keyword-lists` オプションで、`search_keywords.py` に定義されているキーワードリストのエイリアス（`m`, `s`など）を指定して実行します。

```bash
# 「疾患(m)」と「術式(s)」のキーワードで論文を収集
python main.py p1 --keyword-lists m s
```

  * **キーワードリストのエイリアス:**
      * `m`: 疾患名
      * `s`: 術式
      * `c`: 合併症
      * `ph`: 時期
      * `po`: 対象集団
      * `g`: 目標
      * `e`: 評価
      * `t`: 手技
      * `mo`: モダリティ
      * `all`: 全てのリスト

#### **【重要】中断と再開の方法**

このプロセスは大量のAPIを消費するため、無料枠の上限（`429 RESOURCE_EXHAUSTED` エラー）で中断することがあります。その場合は、**ファイルは一切編集せず**、以下の手順で再開してください。

1.  **中断:** APIエラーでスクリプトが停止したら、そのままにします。
2.  **再開:** APIの制限がリセットされた後（例：翌日）、**前回と全く同じコマンドに `--resume` を追加して実行します。**
    ```bash
    # 中断した箇所から自動で再開する
    python main.py p1 --keyword-lists m s --resume
    ```

スクリプトは `output/pipeline_1_processed_keywords.log`（実行済みキーワードの記録）と `output/processed_jstage_dois.log`（完了済み論文の記録）を自動で読み込み、未完了のタスクから処理を再開します。

### ステップ 2: `output` フォルダの同期（手動）

`p1` の実行が完了したら、生成された論文データを、次の `p234` の作業を行うすべてのPCにコピーします。

1.  `p1` を実行したPCの `output` フォルダを、USBメモリなどで他のPCに丸ごとコピーします。
2.  これにより、すべてのPCが同じ論文データを参照する状態になります。

### ステップ 3: データセットの生成 (p234) - 作業分担

各PCで `p234` を実行し、データセット生成を分担します。

#### 作業分担の定義

  * **各PCで** `run_dataset_generation.py` ファイルをテキストエディタで開きます。
  * ファイル上部の `GENERATION_TARGETS` リストを編集し、PCごとに担当するペルソナ（年代・性別）を割り振ります。

**例：デスクトップPC（RTX 4070 Super搭載機）**

```python
# run_dataset_generation.py
GENERATION_TARGETS = [
    {"age_group": "70代", "gender": "女性"},
    {"age_group": "70代", "gender": "男性"},
    {"age_group": "60代", "gender": "女性"},
    {"age_group": "60代", "gender": "男性"},
    {"age_group": "80代", "gender": "女性"},
    {"age_group": "80代", "gender": "男性"},
    # ... 他の年代をコメントアウトまたは削除 ...
]
```

**例：ノートPC（Core i5搭載機）**

```python
# run_dataset_generation.py
GENERATION_TARGETS = [
    {"age_group": "10代", "gender": "女性"},
    {"age_group": "10代", "gender": "男性"},
    {"age_group": "20代", "gender": "女性"},
    {"age_group": "20代", "gender": "男性"},
    # ... 他の年代をコメントアウトまたは削除 ...
]
```

#### データセット生成の実行

  * 作業を分担した**すべてのPC**で、以下のコマンドを実行します。
    ```bash
    python main.py p234
    ```
  * このプロセスも中断・再開に対応しています。中断した場合は、再度同じコマンドを実行すれば、生成済みのファイルは自動でスキップされます。

### ステップ 4: 生成結果の集約（手動）

すべてのPCで `p234` の実行が完了したら、生成されたデータセットを1台のPC（メインのデスクトップPCなど）に集約します。

1.  各作業PCの以下のフォルダ内にあるファイルを、メインPCの同じ場所にあるフォルダにすべてコピー（マージ）してください。
      * `output/pipeline_2_lora_finetune/personas/`
      * `output/pipeline_2_lora_finetune/datasets_by_item/`
      * `output/pipeline_3_parser_finetune/`
2.  ファイル名は重複しないように設計されているため、単純なファイルコピーで安全に集約できます。

これで、ファインチューニングに使用するすべてのデータセットがメインPCの `output` フォルダ内に揃います。

## 5\. 生成されるデータセット

最終的に、`output` フォルダには以下のデータセットが格納されます。

| フォルダパス | 内容 |
| :--- | :--- |
| `output/pipeline_1_rag_source/` | RAGの知識源となる、論文ごとの構造化Markdownファイル。 |
| `output/pipeline_2_lora_finetune/personas/` | データ生成の元となる、架空の患者ペルソナのJSONファイル。 |
| `output/pipeline_2_lora_finetune/datasets_by_item/` | 計画書の項目ごとに分かれた、LoRAファインチューニング用のJSONLファイル。 |
| `output/pipeline_3_parser_finetune/` | 情報抽出モデルのファインチューニング用JSONLファイル。 |
| `output/pipeline_4_embedding_finetune/` | Embeddingモデルのファインチューニング用JSONLファイル（トリプレット形式）。 |

## 6\. トラブルシューティング

  * **`429 RESOURCE_EXHAUSTED` エラー:**

      * **原因:** Gemini APIの無料利用枠の上限に達しました。
      * **対策:** 時間をおいて（通常は翌日）、`--resume` オプションを付けてコマンドを再実行してください。

  * **`500 Internal Server Error`:**

      * **原因:** Gemini APIサーバー側の一時的な問題です。
      * **対策:** スクリプトは自動でエラーを記録し、処理を続行します。もし同じファイルで何度も失敗する場合は、その論文の処理をスキップするか、時間をおいて `--resume` で再試行してください。