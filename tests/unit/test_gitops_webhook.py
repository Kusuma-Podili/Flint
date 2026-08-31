"""
Unit Tests for GitOps Webhook Validation
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from gitops_engine import GitWebhookHandler


class TestGitOpsWebhook(unittest.TestCase):

    def test_github_signature_verification(self):
        secret = "super_secure_webhook_secret_key"
        payload = b'{"ref": "refs/heads/main", "after": "a1b2c3d4"}'
        
        # Valid signature computation
        import hmac, hashlib
        sig = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        
        self.assertTrue(GitWebhookHandler.verify_github_signature(payload, secret, sig))
        self.assertFalse(GitWebhookHandler.verify_github_signature(payload, secret, "sha256=invalid_sig"))

    def test_parse_push_event(self):
        raw = {
            "ref": "refs/heads/feature/microservice-auth",
            "after": "9f8e7d6c5b4a",
            "repository": {"full_name": "enterprise/payments-api"},
            "pusher": {"name": "alice_devops"},
            "head_commit": {"message": "feat: add payment gateway retry logic"}
        }
        event = GitWebhookHandler.parse_event("push", raw)
        self.assertEqual(event["type"], "GIT_PUSH")
        self.assertEqual(event["branch"], "feature/microservice-auth")
        self.assertEqual(event["commit_sha"], "9f8e7d6c5b4a")
        self.assertEqual(event["author"], "alice_devops")


if __name__ == "__main__":
    unittest.main()
