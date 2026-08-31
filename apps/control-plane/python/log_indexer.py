"""
NexusOps In-Memory Structured Log Indexer & Query Engine
"""
import time
from typing import Dict, Any, List

class LogIndexer:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def index_log(self, run_id: str, step_id: str, level: str, message: str):
        self.logs.append({
            "run_id": run_id,
            "step_id": step_id,
            "level": level,
            "message": message,
            "timestamp": time.time()
        })

    def query_logs(self, run_id: str) -> List[Dict[str, Any]]:
        return [l for l in self.logs if l["run_id"] == run_id]
