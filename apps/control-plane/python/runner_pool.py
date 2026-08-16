import time
from typing import Dict, Any, List, Optional

class RunnerPoolManager:
    def __init__(self, heartbeat_timeout_seconds: int = 30):
        self.timeout = heartbeat_timeout_seconds
        self.runners: Dict[str, Dict[str, Any]] = {}

    def register_runner(self, runner_id: str, metadata: Dict[str, Any]):
        self.runners[runner_id] = {
            "id": runner_id,
            "name": metadata.get("name", runner_id),
            "tags": metadata.get("tags", []),
            "status": "IDLE",
            "last_heartbeat": time.time(),
            "active_job_id": None
        }

    def allocate_runner(self, required_tags: List[str] = None) -> Optional[str]:
        required = set(required_tags or [])
        for r_id, runner in self.runners.items():
            if runner["status"] == "IDLE":
                runner_tags = set(runner.get("tags", []))
                if required.issubset(runner_tags):
                    return r_id
        return None

    def assign_job(self, runner_id: str, job_info: Dict[str, Any]) -> bool:
        if runner_id in self.runners and self.runners[runner_id]["status"] == "IDLE":
            self.runners[runner_id]["status"] = "BUSY"
            self.runners[runner_id]["active_job_id"] = job_info.get("job_id")
            return True
        return False
