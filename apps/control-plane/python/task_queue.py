"""
NexusOps Distributed Task Queue with Redis & In-Memory Fallback
"""
import time
from typing import Dict, Any, List, Optional
from collections import deque

class TaskQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, task: Dict[str, Any]):
        task["enqueued_at"] = time.time()
        self.queue.append(task)

    def dequeue(self) -> Optional[Dict[str, Any]]:
        return self.queue.popleft() if self.queue else None
