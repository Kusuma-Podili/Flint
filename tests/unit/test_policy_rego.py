import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("packages/policy-engine/python"))
from policy_engine import PolicyEngine


class TestPolicyEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PolicyEngine()

    def test_s3_encryption_guardrail(self):
        self.assertTrue(self.engine.evaluate_s3_resource({"server_side_encryption": True})[0])
        self.assertFalse(self.engine.evaluate_s3_resource({"server_side_encryption": False})[0])

    def test_k8s_non_root_guardrail(self):
        self.assertTrue(self.engine.evaluate_k8s_pod_security({"securityContext": {"runAsNonRoot": True}})[0])
        self.assertFalse(self.engine.evaluate_k8s_pod_security({"securityContext": {"runAsNonRoot": False}})[0])

    def test_security_group_ssh_exposure(self):
        self.assertFalse(self.engine.evaluate_security_group([{"port": 22, "cidr_blocks": ["0.0.0.0/0"]}])[0])
        self.assertTrue(self.engine.evaluate_security_group([{"port": 22, "cidr_blocks": ["10.0.0.0/16"]}])[0])


if __name__ == "__main__":
    unittest.main()
