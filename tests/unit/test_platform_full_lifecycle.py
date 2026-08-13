import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
sys.path.insert(0, os.path.abspath("packages/dag-engine/python"))
from auth_service import AuthEngine
from envelope_crypto import EnvelopeCryptoService
from hash_chain_audit import HashChainAuditLogger
from dag_engine import DAGResolver
from k8s_controller import CanaryRolloutController


class TestPlatformFullLifecycleE2E(unittest.TestCase):

    def test_e2e_devops_workflow(self):
        # 1. Auth
        auth = AuthEngine()
        key, _, hashed = auth.generate_api_key("ci-system")
        self.assertTrue(auth.validate_api_key(key, hashed))

        # 2. Crypto
        crypto = EnvelopeCryptoService()
        enc = crypto.encrypt_secret("safe_mock_db_uri", {"env": "prod"})
        self.assertEqual(crypto.decrypt_secret(enc, {"env": "prod"}), "safe_mock_db_uri")

        # 3. Audit
        audit = HashChainAuditLogger()
        audit.record_entry("org-1", "usr-1", "user@org.io", "DEPLOY", "K8S", "svc", "127.0.0.1", {})
        self.assertTrue(audit.verify_integrity()[0])

        # 4. DAG
        stages = DAGResolver([{"id": "b", "depends_on": []}, {"id": "d", "depends_on": ["b"]}]).get_execution_stages()
        self.assertEqual(stages, [["b"], ["d"]])

        # 5. Canary
        canary = CanaryRolloutController()
        w = canary.calculate_next_weights(0)
        self.assertEqual(w, 25)


if __name__ == "__main__":
    unittest.main()
