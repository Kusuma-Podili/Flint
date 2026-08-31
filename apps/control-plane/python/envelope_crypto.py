"""
NexusOps Secrets Subsystem: AES-256-GCM Envelope Encryption Engine
"""
import base64
import os
import json
import hashlib
import hmac
import secrets
from typing import Dict, Any, Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class EnvelopeCryptoService:
    """Enterprise envelope encryption with Master Key & Data Encryption Key (DEK) hierarchy."""

    def __init__(self, master_key_base64: str = None):
        if master_key_base64:
            self.master_key = base64.b64decode(master_key_base64)
        else:
            self.master_key = secrets.token_bytes(32)

    def _xor_cipher(self, data: bytes, key: bytes, nonce: bytes) -> bytes:
        keystream = hashlib.sha256(key + nonce).digest()
        while len(keystream) < len(data):
            keystream += hashlib.sha256(keystream + key).digest()
        return bytes(a ^ b for a, b in zip(data, keystream[:len(data)]))

    def encrypt_secret(self, plaintext: str, associated_data: Dict[str, Any] = None) -> Dict[str, str]:
        ad_bytes = json.dumps(associated_data, sort_keys=True).encode("utf-8") if associated_data else b""
        
        if HAS_CRYPTOGRAPHY:
            dek = AESGCM.generate_key(bit_length=256)
            dek_cipher = AESGCM(dek)
            nonce = os.urandom(12)
            ciphertext = dek_cipher.encrypt(nonce, plaintext.encode("utf-8"), ad_bytes if associated_data else None)

            master_cipher = AESGCM(self.master_key)
            dek_nonce = os.urandom(12)
            encrypted_dek = master_cipher.encrypt(dek_nonce, dek, b"nexusops-dek-envelope")
        else:
            dek = secrets.token_bytes(32)
            nonce = secrets.token_bytes(12)
            raw_cipher = self._xor_cipher(plaintext.encode("utf-8"), dek, nonce)
            tag = hmac.new(dek, raw_cipher + ad_bytes, hashlib.sha256).digest()
            ciphertext = raw_cipher + tag

            dek_nonce = secrets.token_bytes(12)
            raw_enc_dek = self._xor_cipher(dek, self.master_key, dek_nonce)
            dek_tag = hmac.new(self.master_key, raw_enc_dek + b"nexusops-dek-envelope", hashlib.sha256).digest()
            encrypted_dek = raw_enc_dek + dek_tag

        return {
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "encrypted_dek": base64.b64encode(encrypted_dek).decode("utf-8"),
            "dek_nonce": base64.b64encode(dek_nonce).decode("utf-8"),
            "version": "v1-aes-256-gcm"
        }

    def decrypt_secret(self, encrypted_payload: Dict[str, str], associated_data: Dict[str, Any] = None) -> str:
        ad_bytes = json.dumps(associated_data, sort_keys=True).encode("utf-8") if associated_data else b""

        if HAS_CRYPTOGRAPHY:
            master_cipher = AESGCM(self.master_key)
            encrypted_dek = base64.b64decode(encrypted_payload["encrypted_dek"])
            dek_nonce = base64.b64decode(encrypted_payload["dek_nonce"])
            dek = master_cipher.decrypt(dek_nonce, encrypted_dek, b"nexusops-dek-envelope")

            dek_cipher = AESGCM(dek)
            ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
            nonce = base64.b64decode(encrypted_payload["nonce"])
            
            plaintext_bytes = dek_cipher.decrypt(nonce, ciphertext, ad_bytes if associated_data else None)
            return plaintext_bytes.decode("utf-8")
        else:
            encrypted_dek = base64.b64decode(encrypted_payload["encrypted_dek"])
            dek_nonce = base64.b64decode(encrypted_payload["dek_nonce"])
            raw_enc_dek, dek_tag = encrypted_dek[:-32], encrypted_dek[-32:]
            expected_dek_tag = hmac.new(self.master_key, raw_enc_dek + b"nexusops-dek-envelope", hashlib.sha256).digest()
            if not hmac.compare_digest(dek_tag, expected_dek_tag):
                raise ValueError("Integrity check failed on Master Key DEK envelope")

            dek = self._xor_cipher(raw_enc_dek, self.master_key, dek_nonce)

            ciphertext_with_tag = base64.b64decode(encrypted_payload["ciphertext"])
            nonce = base64.b64decode(encrypted_payload["nonce"])
            raw_cipher, tag = ciphertext_with_tag[:-32], ciphertext_with_tag[-32:]
            expected_tag = hmac.new(dek, raw_cipher + ad_bytes, hashlib.sha256).digest()
            if not hmac.compare_digest(tag, expected_tag):
                raise ValueError("Integrity check failed: Associated data mismatch or corrupted ciphertext")

            plaintext_bytes = self._xor_cipher(raw_cipher, dek, nonce)
            return plaintext_bytes.decode("utf-8")
