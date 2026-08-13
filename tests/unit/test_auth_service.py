import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from auth_service import AuthEngine


class TestAuthService(unittest.TestCase):

    def setUp(self):
        self.auth = AuthEngine()

    def test_password_hashing_and_verification(self):
        pwd = "EnterpriseSafeTestPassword_999!"
        hashed, salt = self.auth.hash_password(pwd)
        self.assertTrue(self.auth.verify_password(pwd, hashed, salt))
        self.assertFalse(self.auth.verify_password("wrong_password", hashed, salt))

    def test_api_key_generation_and_validation(self):
        key, prefix, hashed = self.auth.generate_api_key("ci-runner")
        self.assertTrue(key.startswith("nx_"))
        self.assertTrue(self.auth.validate_api_key(key, hashed))

    def test_rbac_permission_matrix(self):
        self.assertTrue(self.auth.check_permission("ADMIN", "pipelines:delete"))
        self.assertTrue(self.auth.check_permission("DEVELOPER", "pipelines:execute"))
        self.assertFalse(self.auth.check_permission("VIEWER", "pipelines:delete"))


if __name__ == "__main__":
    unittest.main()
