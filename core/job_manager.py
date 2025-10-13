import threading
import uuid
from typing import Optional, Dict, Any, List


class JobManager:
    """
    データ生成ジョブを管理するクラス。
    複数のワーカーからの同時アクセスに対応するため、スレッドセーフな設計とする。
    """

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.pending_job_ids: List[str] = []
        self._lock = threading.Lock()
        self.worker_assignments: Dict[str, str] = {}  # {job_id: worker_id}

    def add_job(self, job_data: Dict[str, Any]) -> str:
        """
        新しいジョブをリストに追加する。

        Args:
            job_data: ジョブの詳細データ（例: {'pipeline': 'rag_source', 'url': '...'}）

        Returns:
            生成された一意のジョb ID。
        """
        with self._lock:
            job_id = str(uuid.uuid4())
            self.jobs[job_id] = {
                "data": job_data,
                "status": "pending",  # pending, processing, completed, failed
                "history": [],
            }
            self.pending_job_ids.append(job_id)
            print(f"[JobManager] ジョブ追加: {job_id} (残り: {len(self.pending_job_ids)}件)")
            return job_id

    def get_job(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        未処理のジョブを一つ取り出し、ワーカーに割り当てる。

        Args:
            worker_id: ジョブを取得しようとしているワーカーの一意のID。

        Returns:
            割り当てるジョブ。未処理ジョブがない場合はNoneを返す。
        """
        with self._lock:
            if not self.pending_job_ids:
                return None

            job_id = self.pending_job_ids.pop(0)
            job = self.jobs[job_id]
            job["status"] = "processing"
            job["history"].append(f"Assigned to {worker_id}")

            self.worker_assignments[job_id] = worker_id

            print(f"[JobManager] ジョブ割当: {job_id} -> {worker_id} (残り: {len(self.pending_job_ids)}件)")
            return {"job_id": job_id, **job["data"]}

    def update_job_status(self, job_id: str, status: str, message: str = ""):
        """
        ジョブの状態を更新する。

        Args:
            job_id: 対象のジョブID。
            status: 新しいステータス ('completed', 'failed')。
            message: エラーメッセージなど、記録したい情報。
        """
        with self._lock:
            if job_id not in self.jobs:
                print(f"[JobManager] 警告: 存在しないジョブID {job_id} の更新が試みられました。")
                return

            job = self.jobs[job_id]
            job["status"] = status
            history_entry = f"Status updated to {status}"
            if message:
                history_entry += f" - {message}"
            job["history"].append(history_entry)

            if job_id in self.worker_assignments:
                del self.worker_assignments[job_id]

            print(f"[JobManager] ジョブ状態更新: {job_id} -> {status}")

    def get_stats(self) -> Dict[str, int]:
        """
        現在のジョブ全体の統計情報を返す。
        """
        with self._lock:
            stats = {
                "total": len(self.jobs),
                "pending": len(self.pending_job_ids),
                "processing": len(self.worker_assignments),
                "completed": 0,
                "failed": 0,
            }

            completed_or_failed_ids = set(self.jobs.keys()) - set(self.pending_job_ids) - set(self.worker_assignments.keys())
            for job_id in completed_or_failed_ids:
                status = self.jobs[job_id]["status"]
                if status == "completed":
                    stats["completed"] += 1
                elif status == "failed":
                    stats["failed"] += 1
            return stats
