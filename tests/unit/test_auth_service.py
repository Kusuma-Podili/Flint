"""
Unit Tests for NexusOps Auth & RBAC Engine
"""
import unittest
import sys
import os

# Add control-plane python path
sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from auth_service import AuthEngine


class TestAuthService(unittest.TestCase):

    def setUp(self):
        self.auth = AuthEngine()

    def test_password_hashing_and_verification(self):
        password = "SuperSecretSecurePassword123!"
        hashed = self.auth.hash_password(password)
        self.assertIn(":", hashed)
        self.assertTrue(self.auth.verify_password(password, hashed))
        self.assertFalse(self.auth.verify_password("WrongPassword123!", hashed))

    def test_api_key_generation_and_validation(self):
        full_key, prefix, hashed_secret = self.auth.generate_api_key("ci-token")
        self.assertTrue(full_key.startswith("nx_"))
        self.assertTrue(self.auth.verify_api_key(full_key, hashed_secret))
        self.assertFalse(self.auth.verify_api_key("nx_invalid_key_value", hashed_secret))

    def test_rbac_permission_matrix(self):
        # Super Admin has all perms
        self.assertTrue(self.auth.check_permission("SUPER_ADMIN", "pipelines:delete"))
        self.assertTrue(self.auth.check_permission("SUPER_ADMIN", "anything:wildcard"))

        # DevOps Engineer permissions
        self.assertTrue(self.auth.check_permission("DEVOPS_ENGINEER", "pipelines:create"))
        self.assertTrue(self.auth.check_permission("DEVOPS_ENGINEER", "iac:apply"))
        self.assertFalse(self.auth.check_permission("DEVOPS_ENGINEER", "tenant:settings"))

        # Developer permissions
        self.assertTrue(self.auth.check_permission("DEVELOPER", "pipelines:read"))
        self.assertFalse(self.auth.check_permission("DEVELOPER", "secrets:delete"))

        # Viewer permissions
        self.assertTrue(self.auth.check_permission("VIEWER", "pipelines:read"))
        self.assertFalse(self.auth.check_permission("VIEWER", "pipelines:create"))


if __name__ == "__main__":
    unittest.main()
