"""
Unit Tests for AES-256-GCM Envelope Encryption
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from envelope_crypto import EnvelopeCryptoService


class TestEnvelopeCrypto(unittest.TestCase):

    def setUp(self):
        self.crypto = EnvelopeCryptoService()

    def test_encrypt_decrypt_secret(self):
        secret_value = "postgres://admin:topsecret123@db.prod.nexusops.io:5432/nexus_db"
        metadata = {"tenantId": "tenant-001", "environment": "production"}

        encrypted_payload = self.crypto.encrypt_secret(secret_value, associated_data=metadata)
        self.assertIn("ciphertext", encrypted_payload)
        self.assertIn("encrypted_dek", encrypted_payload)
        self.assertIn("nonce", encrypted_payload)

        # Decrypt successfully
        decrypted = self.crypto.decrypt_secret(encrypted_payload, associated_data=metadata)
        self.assertEqual(decrypted, secret_value)

    def test_tamper_associated_data_fails(self):
        secret_value = "aws_secret_access_key_xyz987654321"
        metadata = {"tenantId": "tenant-001", "environment": "production"}

        encrypted_payload = self.crypto.encrypt_secret(secret_value, associated_data=metadata)

        # Tampered associated data should fail GCM authentication tag
        tampered_metadata = {"tenantId": "tenant-002", "environment": "production"}
        with self.assertRaises(Exception):
            self.crypto.decrypt_secret(encrypted_payload, associated_data=tampered_metadata)


if __name__ == "__main__":
    unittest.main()
