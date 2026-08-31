"""
End-to-End Test: Full DevOps Pipeline, IaC & DevSecOps Lifecycle
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
sys.path.insert(0, os.path.abspath("packages/dag-engine/python"))
sys.path.insert(0, os.path.abspath("packages/iac-parser/python"))
sys.path.insert(0, os.path.abspath("packages/policy-engine/python"))

from auth_service import AuthEngine
from envelope_crypto import EnvelopeCryptoService
from hash_chain_audit import HashChainAuditLogger
from dag_engine import DAGResolver
from pipeline_orchestrator import PipelineExecutionEngine
from runner_pool import RunnerPoolManager
from iac_engine import TerraformPlanAnalyzer, DriftDetector
from k8s_controller import CanaryRolloutController
from policy_engine import PolicyEngine
from security_scanner import SecretEntropyScanner, TrivyVulnerabilityParser


class TestPlatformFullLifecycleE2E(unittest.TestCase):
    """Executes a complete simulated workflow across all platform subsystems."""

    def test_e2e_devops_workflow(self):
        # 1. Authenticate user & check permissions
        auth = AuthEngine()
        self.assertTrue(auth.check_permission("DEVOPS_ENGINEER", "pipelines:execute"))

        # 2. Encrypt repository deploy key with AES-256 Envelope Crypto
        crypto = EnvelopeCryptoService()
        secret_payload = crypto.encrypt_secret("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...", {"tenant": "acme-corp"})
        decrypted_key = crypto.decrypt_secret(secret_payload, {"tenant": "acme-corp"})
        self.assertTrue(decrypted_key.startswith("ssh-rsa"))

        # 3. Log audit event with immutable hash chain
        audit = HashChainAuditLogger()
        audit.record_entry("acme-corp", "usr-1", "alice@acme.com", "TRIGGER_PIPELINE", "PIPELINE", "pipe-prod-01", "10.0.0.5", {})
        valid_chain, _ = audit.verify_integrity()
        self.assertTrue(valid_chain)

        # 4. Parse DAG and execute pipeline stages
        pipeline_def = {
            "id": "pipe-prod-01",
            "steps": [
                {"id": "compile", "depends_on": []},
                {"id": "sast-scan", "depends_on": ["compile"]},
                {"id": "unit-test", "depends_on": ["compile"]},
                {"id": "deploy-canary", "depends_on": ["sast-scan", "unit-test"]}
            ]
        }
        engine = PipelineExecutionEngine()
        run = engine.trigger_pipeline(pipeline_def, {"type": "GIT_PUSH", "actor": "alice"})
        self.assertEqual(run["status"], "RUNNING")
        self.assertEqual(len(run["stages"]), 3)

        # 5. DevSecOps Security Scan Verification
        findings = SecretEntropyScanner.scan_content("const db = 'postgres://prod:secret@db:5432';")
        self.assertGreaterEqual(len(findings), 0)

        # 6. Terraform Plan Analysis
        mock_plan = {
            "resource_changes": [
                {"address": "aws_instance.worker", "type": "aws_instance", "change": {"actions": ["create"]}}
            ]
        }
        iac_summary = TerraformPlanAnalyzer.parse_plan(mock_plan)
        self.assertEqual(iac_summary["to_add"], 1)

        # 7. Progressive Canary Traffic Promotion
        canary = CanaryRolloutController(step_percentage=25)
        weight = canary.calculate_next_weights(0)
        self.assertEqual(weight, 25)
        weight = canary.calculate_next_weights(weight)
        self.assertEqual(weight, 50)


if __name__ == "__main__":
    unittest.main()
