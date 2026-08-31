"""
Unit Tests for Policy Engine Guardrails
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("packages/policy-engine/python"))
from policy_engine import PolicyEngine


class TestPolicyEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PolicyEngine()

    def test_s3_encryption_guardrail(self):
        # Valid encrypted S3 bucket
        valid_s3 = {"name": "prod-data-lake", "server_side_encryption": True}
        passed, msg = self.engine.evaluate_s3_resource(valid_s3)
        self.assertTrue(passed)

        # Unencrypted S3 bucket
        invalid_s3 = {"name": "public-unencrypted-bucket", "server_side_encryption": False}
        passed, msg = self.engine.evaluate_s3_resource(invalid_s3)
        self.assertFalse(passed)
        self.assertIn("Failed", msg)

    def test_k8s_non_root_guardrail(self):
        # Valid non-root pod
        valid_pod = {"securityContext": {"runAsNonRoot": True, "runAsUser": 1001}}
        passed, msg = self.engine.evaluate_k8s_pod_security(valid_pod)
        self.assertTrue(passed)

        # Root pod
        root_pod = {"securityContext": {"runAsNonRoot": False}}
        passed, msg = self.engine.evaluate_k8s_pod_security(root_pod)
        self.assertFalse(passed)

    def test_security_group_ssh_exposure(self):
        # Disallow 0.0.0.0/0 on port 22
        bad_sg = [{"port": 22, "cidr_blocks": ["0.0.0.0/0"]}]
        passed, msg = self.engine.evaluate_security_group(bad_sg)
        self.assertFalse(passed)

        # Allow corporate VPN CIDR
        good_sg = [{"port": 22, "cidr_blocks": ["10.50.0.0/16"]}]
        passed, msg = self.engine.evaluate_security_group(good_sg)
        self.assertTrue(passed)


if __name__ == "__main__":
    unittest.main()
