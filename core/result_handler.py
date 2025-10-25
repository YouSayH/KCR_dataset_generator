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