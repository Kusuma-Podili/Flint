"""
NexusOps Scheduled Infrastructure Drift Scanner
"""
import time
from typing import Dict, Any, List

class DriftScheduler:
    def __init__(self, interval_seconds: int = 3600):
        self.interval = interval_seconds
        self.last_scans: Dict[str, float] = {}

    def is_due(self, workspace_id: str) -> bool:
        last = self.last_scans.get(workspace_id, 0)
        return (time.time() - last) > self.interval
