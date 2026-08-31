"""
NexusOps GitOps Engine: Webhook Verification & Manifest Reconciliation
"""
import hmac
import hashlib
import json
from typing import Dict, Any, Tuple


class GitWebhookHandler:
    """Verifies GitHub, GitLab, and Bitbucket webhook payloads."""

    @staticmethod
    def verify_github_signature(payload_bytes: bytes, secret: str, header_signature: str) -> bool:
        if not header_signature or not header_signature.startswith("sha256="):
            return False
        expected_sig = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, header_signature)

    @staticmethod
    def parse_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if event_type == "push":
            return {
                "type": "GIT_PUSH",
                "repository": payload.get("repository", {}).get("full_name"),
                "branch": payload.get("ref", "").replace("refs/heads/", ""),
                "commit_sha": payload.get("after"),
                "author": payload.get("pusher", {}).get("name"),
                "commit_message": payload.get("head_commit", {}).get("message")
            }
        elif event_type == "pull_request":
            return {
                "type": "GIT_PR",
                "action": payload.get("action"),
                "pr_number": payload.get("number"),
                "repository": payload.get("repository", {}).get("full_name"),
                "source_branch": payload.get("pull_request", {}).get("head", {}).get("ref"),
                "target_branch": payload.get("pull_request", {}).get("base", {}).get("ref"),
                "commit_sha": payload.get("pull_request", {}).get("head", {}).get("sha")
            }
        return {"type": "UNKNOWN", "raw": payload}
