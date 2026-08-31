"""
NexusOps Distributed Runner Pool & WebSocket Dispatcher
"""
import time
from typing import Dict, Any, List, Optional


class RunnerPoolManager:
    """Coordinates self-hosted and cloud runner agents."""

    def __init__(self, heartbeat_timeout_seconds: int = 30):
        self.runners: Dict[str, Dict[str, Any]] = {}
        self.heartbeat_timeout = heartbeat_timeout_seconds
        self.job_queue: List[Dict[str, Any]] = []

    def register_runner(self, runner_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        info = {
            "runner_id": runner_id,
            "name": metadata.get("name", f"runner-{runner_id}"),
            "tags": metadata.get("tags", ["default"]),
            "status": "ONLINE",
            "os": metadata.get("os", "linux"),
            "arch": metadata.get("arch", "x86_64"),
            "current_job": None,
            "last_heartbeat": time.time()
        }
        self.runners[runner_id] = info
        return info

    def record_heartbeat(self, runner_id: str) -> bool:
        if runner_id in self.runners:
            self.runners[runner_id]["last_heartbeat"] = time.time()
            if self.runners[runner_id]["status"] == "OFFLINE":
                self.runners[runner_id]["status"] = "ONLINE"
            return True
        return False

    def allocate_runner(self, required_tags: List[str] = None) -> Optional[str]:
        now = time.time()
        for runner_id, runner in self.runners.items():
            # Check timeout
            if now - runner["last_heartbeat"] > self.heartbeat_timeout:
                runner["status"] = "OFFLINE"
                continue

            if runner["status"] == "ONLINE" and runner["current_job"] is None:
                if required_tags:
                    if all(tag in runner["tags"] for tag in required_tags):
                        return runner_id
                else:
                    return runner_id
        return None

    def assign_job(self, runner_id: str, job: Dict[str, Any]) -> bool:
        if runner_id in self.runners and self.runners[runner_id]["status"] == "ONLINE":
            self.runners[runner_id]["status"] = "BUSY"
            self.runners[runner_id]["current_job"] = job["job_id"]
            return True
        return False

    def release_runner(self, runner_id: str) -> None:
        if runner_id in self.runners:
            self.runners[runner_id]["status"] = "ONLINE"
            self.runners[runner_id]["current_job"] = None
