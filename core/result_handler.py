# import os
# import json
# from datetime import datetime


# class ResultHandler:
#     """
#     ワーカーから受け取った成果物をファイルシステムに保存するクラス。
#     """

#     def __init__(self, base_output_dir: str = "output"):
#         self.base_dir = base_output_dir
#         self.pipelines_dir = {
#             "rag_source": os.path.join(self.base_dir, "pipeline_1_rag_source"),
#             "lora_finetune": os.path.join(self.base_dir, "pipeline_2_lora_finetune"),
#             "persona_generation": os.path.join(self.base_dir, "pipeline_2_lora_finetune", "personas"),
#             "lora_data_generation": os.path.join(self.base_dir, "pipeline_2_lora_finetune"),
#             "parser_finetune": os.path.join(self.base_dir, "pipeline_3_parser_finetune"),
#             "embedding_finetune": os.path.join(self.base_dir, "pipeline_4_embedding_finetune"),
#         }
#         self.logs_dir = os.path.join(self.base_dir, "logs")
#         self._create_dirs()

#     def _create_dirs(self):
#         """必要な出力ディレクトリを全て作成する。"""
#         os.makedirs(self.base_dir, exist_ok=True)
#         for path in self.pipelines_dir.values():
#             os.makedirs(path, exist_ok=True)
#         os.makedirs(self.logs_dir, exist_ok=True)

#     def save_result(self, job_id: str, pipeline_name: str, result_data: dict, custom_filename: str = None):
#         """
#         成功したジョブの結果を保存する。
#         custom_filenameが指定された場合、それを使用する。

#         Args:
#             job_id (str): ジョブID。
#             pipeline_name (str): 実行されたパイプラインの名前。
#             result_data (dict): 保存するデータ本体。'content'と'extension'キーを持つことを期待。
#         """
#         pipeline_dir = self.pipelines_dir.get(pipeline_name)
#         if not pipeline_dir:
#             raise ValueError(f"未知のパイプライン名です: {pipeline_name}")

#         content = result_data.get("content", "")
#         extension = result_data.get("extension", ".txt")

#         # JSONLの場合は追記モード、それ以外は新規作成モード
#         if extension == ".jsonl":
#             # ファイル名はパイプライン名から派生させる（例: parser_finetune.jsonl）
#             # こうすることで、1つのファイルに全ワーカーの結果が集約される
#             filename = f"{pipeline_name}_dataset.jsonl"
#             filepath = os.path.join(pipeline_dir, filename)
#             try:
#                 with open(filepath, "a", encoding="utf-8") as f:
#                     f.write(content + "\n")
#                 self._log_event("SUCCESS", job_id, pipeline_name, f"結果を {filepath} に追記しました。")
#             except Exception as e:
#                 self._log_event("ERROR", job_id, pipeline_name, f"結果のファイル書き込み中にエラー: {e}")
#         else:
#             # Markdownなど、ジョブごとに個別ファイルを作成する場合
#             filename = custom_filename if custom_filename else f"{job_id}{extension}"
#             filepath = os.path.join(pipeline_dir, filename)
#             try:
#                 with open(filepath, "w", encoding="utf-8") as f:
#                     f.write(content)
#                 self._log_event("SUCCESS", job_id, pipeline_name, f"結果を {filepath} に保存しました。")
#             except Exception as e:
#                 self._log_event("ERROR", job_id, pipeline_name, f"結果のファイル書き込み中にエラー: {e}")

#     # def save_error(self, job_id: str, pipeline_name: str, error_info: dict):
#     #     """
#     #     失敗したジョブの情報をログに記録する。
#     #     仕様書のデッドレターキュー（DLQ）の簡易的な実装。
#     #     """
#     #     error_log_path = os.path.join(self.logs_dir, "dead_letter_queue.jsonl")
#     #     log_entry = {
#     #         "timestamp": datetime.now().isoformat(),
#     #         "job_id": job_id,
#     #         "pipeline_name": pipeline_name,
#     #         "error_info": error_info,
#     #     }
#     #     with open(error_log_path, "a", encoding="utf-8") as f:
#     #         f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
#     #     self._log_event("FAILURE", job_id, pipeline_name, f"エラー情報を {error_log_path} に記録しました。")

#     def save_error(self, job_id: str, pipeline_name: str, error_info: dict, original_job_data: dict = None):
#         """
#         失敗したジョブの情報をログに記録する。
#         【新機能】再実行できるよう、元のジョブデータも一緒に保存する。
#         """
#         error_log_path = os.path.join(self.logs_dir, "dead_letter_queue.jsonl")
        
#         log_entry = {
#             "timestamp": datetime.now().isoformat(),
#             "failed_job_id": job_id, # どのジョブが失敗したか
#             "pipeline_name": pipeline_name,
#             "error_info": error_info,
#             "job_context_for_resubmit": original_job_data # ★再実行用のコンテキスト
#         }
        
#         with open(error_log_path, "a", encoding="utf-8") as f:
#             # default=str は、datetimeオブジェクトなどが含まれていてもエラーにならないようにする安全策
#             f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + "\n")
            
#         self._log_event("FAILURE", job_id, pipeline_name, f"エラー情報と再実行コンテキストを {error_log_path} に記録しました。")

#     def _log_event(self, level, job_id, pipeline, message):
#         """コンソールとファイルにイベントを記録する（簡易版）"""
#         log_message = f"[{datetime.now().isoformat()}] [{level}] Job:{job_id} ({pipeline}) - {message}"
#         print(log_message)
#         # TODO: 統合ログ管理を導入する場合は、ここにFluentdなどへの送信処理を追加



import os
import json
from datetime import datetime


class ResultHandler:
    """
    ワーカーから受け取った成果物をファイルシステムに保存するクラス。
    """

    def __init__(self, base_output_dir: str = "output"):
        self.base_dir = base_output_dir
        self.pipelines_dir = {
            "rag_source": os.path.join(self.base_dir, "pipeline_1_rag_source"),
            "persona_generation": os.path.join(self.base_dir, "pipeline_2_lora_finetune", "personas"),
            "lora_data_generation": os.path.join(self.base_dir, "pipeline_2_lora_finetune"),
            "parser_finetune": os.path.join(self.base_dir, "pipeline_3_parser_finetune"),
            "embedding_finetune": os.path.join(self.base_dir, "pipeline_4_embedding_finetune"),
            # --- ▼▼▼ この行を追加 ▼▼▼ ---
            "lora_chain_generation": os.path.join(self.base_dir, "pipeline_2_lora_finetune"),
        }
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self._create_dirs()

    def _create_dirs(self):
        """必要な出力ディレクトリを全て作成する。"""
        os.makedirs(self.base_dir, exist_ok=True)
        for path in self.pipelines_dir.values():
            os.makedirs(path, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def save_result(self, job_id: str, pipeline_name: str, result_data: dict, custom_filename: str = None):
        """
        成功したジョブの結果を保存する。
        """
        pipeline_dir = self.pipelines_dir.get(pipeline_name)
        if not pipeline_dir:
            raise ValueError(f"未知のパイプライン名です: {pipeline_name}")

        content = result_data.get("content", "")
        extension = result_data.get("extension", ".txt")

        if extension == ".jsonl":
            # 成果物が一つのファイルに追記される形式の場合
            if pipeline_name == 'lora_chain_generation':
                 # LoRAチェーンの場合は、完了した全項目を1つのファイルとして保存
                 filename = f"{job_id}.jsonl"
            else:
                 filename = f"{pipeline_name}_dataset.jsonl"
            
            filepath = os.path.join(pipeline_dir, filename)
            try:
                with open(filepath, "a", encoding="utf-8") as f:
                    f.write(content + "\n")
                self._log_event("SUCCESS", job_id, pipeline_name, f"結果を {filepath} に追記しました。")
            except Exception as e:
                self._log_event("ERROR", job_id, pipeline_name, f"結果のファイル書き込み中にエラー: {e}")
        else:
            # ジョブごとに個別ファイルを作成する場合
            filename = custom_filename if custom_filename else f"{job_id}{extension}"
            filepath = os.path.join(pipeline_dir, filename)
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self._log_event("SUCCESS", job_id, pipeline_name, f"結果を {filepath} に保存しました。")
            except Exception as e:
                self._log_event("ERROR", job_id, pipeline_name, f"結果のファイル書き込み中にエラー: {e}")

    def save_error(self, job_id: str, pipeline_name: str, error_info: dict, original_job_data: dict = None):
        """
        失敗したジョブの情報をログに記録する。
        """
        error_log_path = os.path.join(self.logs_dir, "dead_letter_queue.jsonl")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "failed_job_id": job_id,
            "pipeline_name": pipeline_name,
            "error_info": error_info,
            "job_context_for_resubmit": original_job_data
        }
        
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + "\n")
            
        self._log_event("FAILURE", job_id, pipeline_name, f"エラー情報と再実行コンテキストを {error_log_path} に記録しました。")

    def _log_event(self, level, job_id, pipeline, message):
        """コンソールにイベントを記録する"""
        log_message = f"[{datetime.now().isoformat()}] [{level}] Job:{job_id} ({pipeline}) - {message}"
        print(log_message)