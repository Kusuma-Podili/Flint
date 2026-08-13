import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from gitops_engine import GitWebhookVerifier


class TestGitOpsWebhook(unittest.TestCase):

    def test_github_signature_verification(self):
        secret = "safe_webhook_mock_secret_key"
        payload = b'{"ref": "refs/heads/main"}'
        sig = GitWebhookVerifier.generate_test_signature(payload, secret)
        self.assertTrue(GitWebhookVerifier.verify_github_signature(payload, sig, secret))
        self.assertFalse(GitWebhookVerifier.verify_github_signature(payload, "sha256=invalid", secret))

    def test_parse_push_event(self):
        event = {"ref": "refs/heads/main", "after": "abc1234", "repository": {"name": "app"}}
        parsed = GitWebhookVerifier.parse_event("push", event)
        self.assertEqual(parsed["branch"], "main")


if __name__ == "__main__":
    unittest.main()
