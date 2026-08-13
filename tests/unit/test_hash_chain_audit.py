import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from hash_chain_audit import HashChainAuditLogger


class TestHashChainAudit(unittest.TestCase):

    def setUp(self):
        self.logger = HashChainAuditLogger()

    def test_audit_logging_and_integrity_verification(self):
        e1 = self.logger.record_entry("org-1", "usr-1", "user@test.org", "CREATE", "PIPELINE", "pipe-1", "127.0.0.1", {})
        e2 = self.logger.record_entry("org-1", "usr-1", "user@test.org", "RUN", "PIPELINE", "pipe-1", "127.0.0.1", {})
        self.assertEqual(e1["sequence_number"], 1)
        self.assertEqual(e2["sequence_number"], 2)
        valid, msg = self.logger.verify_integrity()
        self.assertTrue(valid)

    def test_tampering_detection(self):
        self.logger.record_entry("org-1", "usr-1", "user@test.org", "CREATE", "PIPELINE", "pipe-1", "127.0.0.1", {})
        self.logger.chain[0]["action"] = "UNAUTHORIZED_EDIT"
        valid, msg = self.logger.verify_integrity()
        self.assertFalse(valid)
        self.assertIn("Tampering detected", msg)


if __name__ == "__main__":
    unittest.main()
