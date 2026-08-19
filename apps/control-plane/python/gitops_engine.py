import hmac
import hashlib
from typing import Dict, Any

class GitWebhookVerifier:
    @staticmethod
    def verify_github_signature(payload: bytes, signature_header: str, secret: str) -> bool:
        if not signature_header or not signature_header.startswith("sha256="):
            return False
        expected = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature_header, expected)

    @staticmethod
    def generate_test_signature(payload: bytes, secret: str) -> str:
        return "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    @staticmethod
    def parse_event(event_type: str, payload_json: Dict[str, Any]) -> Dict[str, Any]:
        if event_type == "push":
            return {
                "branch": payload_json.get("ref", "").replace("refs/heads/", ""),
                "commit_sha": payload_json.get("after"),
                "repo": payload_json.get("repository", {}).get("name")
            }
        return {"event": event_type}
