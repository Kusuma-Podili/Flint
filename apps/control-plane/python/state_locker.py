"""
NexusOps Distributed State Locker for Terraform & OpenTofu Workspaces
"""
import time
from typing import Dict, Any, Optional

class StateLocker:
    def __init__(self):
        self.locks: Dict[str, Dict[str, Any]] = {}

    def acquire_lock(self, workspace_id: str, actor: str) -> bool:
        if workspace_id in self.locks:
            return False
        self.locks[workspace_id] = {"actor": actor, "acquired_at": time.time()}
        return True

    def release_lock(self, workspace_id: str) -> bool:
        if workspace_id in self.locks:
            del self.locks[workspace_id]
            return True
        return False
