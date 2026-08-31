"""
Unit Tests for Cryptographic Hash Chaining Audit Log
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from hash_chain_audit import HashChainAuditLogger


class TestHashChainAudit(unittest.TestCase):

    def setUp(self):
        self.logger = HashChainAuditLogger()

    def test_audit_logging_and_integrity_verification(self):
        self.logger.record_entry(
            tenant_id="tenant-1",
            user_id="user-1",
            user_email="admin@nexusops.dev",
            action="PIPELINE_CREATE",
            resource_type="PIPELINE",
            resource_id="pipe-101",
            ip_address="192.168.1.1",
            details={"pipeline_name": "Production Deploy"}
        )

        self.logger.record_entry(
            tenant_id="tenant-1",
            user_id="user-1",
            user_email="admin@nexusops.dev",
            action="IAC_APPLY",
            resource_type="IAC_WORKSPACE",
            resource_id="ws-aws-prod",
            ip_address="192.168.1.1",
            details={"resources_changed": 5}
        )

        valid, error = self.logger.verify_integrity()
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_tampering_detection(self):
        self.logger.record_entry("tenant-1", "user-1", "admin@nexusops.dev", "DELETE_SECRET", "SECRET", "sec-1", "10.0.0.1", {})
        self.logger.record_entry("tenant-1", "user-1", "admin@nexusops.dev", "DELETE_CLUSTER", "CLUSTER", "k8s-1", "10.0.0.1", {})

        # Malicious attacker modifies log history
        self.logger.audit_log[0]["action"] = "READ_SECRET"

        valid, error = self.logger.verify_integrity()
        self.assertFalse(valid)
        self.assertIn("Tampered entry detected", error)


if __name__ == "__main__":
    unittest.main()
