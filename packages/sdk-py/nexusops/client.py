import requests
from typing import Dict, Any, List
from .models import PipelineRun

class NexusOpsClient:
    """Synchronous Client for NexusOps API Gateway."""

    def __init__(self, endpoint: str = "http://localhost:8080", api_key: str = None):
        self.endpoint = endpoint.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}" if api_key else "",
            "Content-Type": "application/json"
        }

    def trigger_pipeline(self, pipeline_id: str, branch: str = "main", vars: Dict[str, str] = None) -> Dict[str, Any]:
        url = f"{self.endpoint}/api/v1/pipelines/{pipeline_id}/trigger"
        payload = {"branch": branch, "variables": vars or {}}
        res = requests.post(url, json=payload, headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        url = f"{self.endpoint}/api/v1/runs/{run_id}"
        res = requests.get(url, headers=self.headers)
        res.raise_for_status()
        return res.json()
