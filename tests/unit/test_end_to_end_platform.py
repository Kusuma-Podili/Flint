import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
sys.path.insert(0, os.path.abspath("apps/runner-agent/python"))
sys.path.insert(0, os.path.abspath("packages/dag-engine/python"))
sys.path.insert(0, os.path.abspath("packages/iac-parser/python"))
sys.path.insert(0, os.path.abspath("packages/policy-engine/python"))

from state_store import state_store


class TestFlintEndToEndPlatform(unittest.TestCase):

    def test_01_authentication_flow(self):
        # 1. Successful Login for all 4 demo users
        admin = state_store.authenticate_user("admin@gmail.com", "Admin@123")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "ADMIN")

        devops = state_store.authenticate_user("devops@gmail.com", "DevOps@123")
        self.assertIsNotNone(devops)
        self.assertEqual(devops["role"], "DEVOPS_ENGINEER")

        developer = state_store.authenticate_user("developer@gmail.com", "Developer@123")
        self.assertIsNotNone(developer)
        self.assertEqual(developer["role"], "DEVELOPER")

        viewer = state_store.authenticate_user("viewer@gmail.com", "Viewer@123")
        self.assertIsNotNone(viewer)
        self.assertEqual(viewer["role"], "VIEWER")

        # 2. Invalid password rejection
        bad_auth = state_store.authenticate_user("admin@gmail.com", "WrongPassword!99")
        self.assertIsNone(bad_auth)

        # 3. Session token lifecycle
        token = state_store.create_session(admin)
        self.assertTrue(token.startswith("flint_sess_"))
        validated = state_store.validate_session(token)
        self.assertIsNotNone(validated)
        self.assertEqual(validated["email"], "admin@gmail.com")

        # Invalidate on logout
        state_store.invalidate_session(token)
        self.assertIsNone(state_store.validate_session(token))

    def test_02_rbac_permission_matrix(self):
        # ADMIN permissions
        self.assertTrue(state_store.check_permission("ADMIN", "users:create"))
        self.assertTrue(state_store.check_permission("ADMIN", "pipelines:execute"))
        self.assertTrue(state_store.check_permission("ADMIN", "deployments:rollback"))

        # DEVOPS_ENGINEER permissions
        self.assertFalse(state_store.check_permission("DEVOPS_ENGINEER", "users:create"))
        self.assertTrue(state_store.check_permission("DEVOPS_ENGINEER", "pipelines:execute"))
        self.assertTrue(state_store.check_permission("DEVOPS_ENGINEER", "deployments:promote"))

        # DEVELOPER permissions
        self.assertFalse(state_store.check_permission("DEVELOPER", "users:create"))
        self.assertFalse(state_store.check_permission("DEVELOPER", "iac:mutate"))
        self.assertTrue(state_store.check_permission("DEVELOPER", "pipelines:execute"))
        self.assertTrue(state_store.check_permission("DEVELOPER", "logs:read"))

        # VIEWER permissions (Read-only)
        self.assertFalse(state_store.check_permission("VIEWER", "pipelines:execute"))
        self.assertFalse(state_store.check_permission("VIEWER", "deployments:create"))
        self.assertFalse(state_store.check_permission("VIEWER", "deployments:rollback"))
        self.assertTrue(state_store.check_permission("VIEWER", "dashboard:read"))

    def test_03_pipeline_dag_execution_and_security_gate(self):
        # 1. Standard Happy Path Execution
        res = state_store.run_pipeline("pipe-web-prod", "devops@gmail.com", simulation_mode="NORMAL")
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(len(res["stages"]), 7)
        self.assertIsNone(res["failure_reason"])

        # 2. Security Failure Simulation (Security gate blocks deployment)
        sec_res = state_store.run_pipeline("pipe-web-prod", "devops@gmail.com", simulation_mode="FAIL_SECURITY")
        self.assertEqual(sec_res["status"], "FAILED")
        self.assertIn("Security Gate Blocked", sec_res["failure_reason"])
        
        # Verify failed stage details
        failed_stage = next(s for s in sec_res["stages"] if s["status"] == "FAILED")
        self.assertEqual(failed_stage["id"], "security-scan")

    def test_04_deployments_canary_blue_green_and_rollback(self):
        # 1. Create Deployment
        dep = state_store.create_deployment("Payment Core", "v3.0.0", "CANARY", "admin@gmail.com")
        dep_id = dep["id"]
        self.assertEqual(dep["status"], "DEPLOYING")
        self.assertEqual(dep["canary_weight"], 25)

        # 2. Progressive Canary Promotion (25% -> 50% -> 75% -> 100%)
        p1 = state_store.promote_canary(dep_id, "admin@gmail.com")
        self.assertEqual(p1["canary_weight"], 50)
        p2 = state_store.promote_canary(dep_id, "admin@gmail.com")
        self.assertEqual(p2["canary_weight"], 75)
        p3 = state_store.promote_canary(dep_id, "admin@gmail.com")
        self.assertEqual(p3["canary_weight"], 100)
        self.assertEqual(p3["status"], "HEALTHY")

        # 3. Rollback
        rb = state_store.rollback_deployment(dep_id, "Simulated telemetry error rate > 5%", "devops@gmail.com")
        self.assertEqual(rb["status"], "ROLLED_BACK")
        self.assertEqual(rb["canary_weight"], 0)

        # 4. Blue-Green Switch
        bg_dep = state_store.create_deployment("Auth Service", "v2.0.0", "BLUE_GREEN", "admin@gmail.com")
        sw1 = state_store.switch_blue_green(bg_dep["id"], "admin@gmail.com")
        self.assertEqual(sw1["blue_green_active"], "green")

    def test_05_infrastructure_drift_detection_and_remediation(self):
        # Run drift detection
        drift_res = state_store.detect_drift("devops@gmail.com")
        self.assertTrue(drift_res["has_drift"])
        self.assertIn("k8s_deployment.web_service_replicas", drift_res["details"]["resource"])

        # Remediate drift back to desired state
        rem_res = state_store.remediate_drift("devops@gmail.com")
        self.assertEqual(rem_res["status"], "REMEDIATED")

    def test_06_audit_cryptographic_chain_integrity(self):
        # Verify that all transactions maintain valid SHA-256 hash chaining
        verify_res = state_store.verify_audit_integrity("admin@gmail.com")
        self.assertTrue(verify_res["is_valid"])
        self.assertGreater(verify_res["total_records"], 0)


if __name__ == "__main__":
    unittest.main()
