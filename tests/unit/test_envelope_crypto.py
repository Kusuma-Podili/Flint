import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from envelope_crypto import EnvelopeCryptoService


class TestEnvelopeCrypto(unittest.TestCase):

    def setUp(self):
        self.crypto = EnvelopeCryptoService()

    def test_encrypt_decrypt_secret(self):
        secret = "postgres://usr:demo_safe_mock_pwd@localhost:5432/db"
        ad = {"tenant_id": "tenant-100", "environment": "production"}
        encrypted = self.crypto.encrypt_secret(secret, ad)
        self.assertIn("ciphertext", encrypted)
        self.assertIn("encrypted_dek", encrypted)
        decrypted = self.crypto.decrypt_secret(encrypted, ad)
        self.assertEqual(secret, decrypted)

    def test_tamper_associated_data_fails(self):
        secret = "demo_api_mock_token_safe_value"
        ad = {"tenant_id": "tenant-100"}
        encrypted = self.crypto.encrypt_secret(secret, ad)
        with self.assertRaises(ValueError):
            self.crypto.decrypt_secret(encrypted, {"tenant_id": "tenant-attacker"})


if __name__ == "__main__":
    unittest.main()
