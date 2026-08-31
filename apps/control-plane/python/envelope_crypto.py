"""
NexusOps Secrets Subsystem: AES-256-GCM Envelope Encryption Engine
"""
import base64
import os
import json
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EnvelopeCryptoService:
    """Enterprise envelope encryption with Master Key & Data Encryption Key (DEK) hierarchy."""

    def __init__(self, master_key_base64: str = None):
        if master_key_base64:
            self.master_key = base64.b64decode(master_key_base64)
        else:
            self.master_key = AESGCM.generate_key(bit_length=256)

    def encrypt_secret(self, plaintext: str, associated_data: Dict[str, Any] = None) -> Dict[str, str]:
        # 1. Generate ephemeral DEK (Data Encryption Key)
        dek = AESGCM.generate_key(bit_length=256)
        
        # 2. Encrypt plaintext with DEK
        dek_cipher = AESGCM(dek)
        nonce = os.urandom(12)
        ad_bytes = json.dumps(associated_data, sort_keys=True).encode("utf-8") if associated_data else None
        ciphertext = dek_cipher.encrypt(nonce, plaintext.encode("utf-8"), ad_bytes)

        # 3. Encrypt DEK with Master Key
        master_cipher = AESGCM(self.master_key)
        dek_nonce = os.urandom(12)
        encrypted_dek = master_cipher.encrypt(dek_nonce, dek, b"nexusops-dek-envelope")

        return {
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "encrypted_dek": base64.b64encode(encrypted_dek).decode("utf-8"),
            "dek_nonce": base64.b64encode(dek_nonce).decode("utf-8"),
            "version": "v1-aes-256-gcm"
        }

    def decrypt_secret(self, encrypted_payload: Dict[str, str], associated_data: Dict[str, Any] = None) -> str:
        # 1. Decrypt DEK using Master Key
        master_cipher = AESGCM(self.master_key)
        encrypted_dek = base64.b64decode(encrypted_payload["encrypted_dek"])
        dek_nonce = base64.b64decode(encrypted_payload["dek_nonce"])
        dek = master_cipher.decrypt(dek_nonce, encrypted_dek, b"nexusops-dek-envelope")

        # 2. Decrypt Ciphertext with recovered DEK
        dek_cipher = AESGCM(dek)
        ciphertext = base64.b64decode(encrypted_payload["ciphertext"])
        nonce = base64.b64decode(encrypted_payload["nonce"])
        ad_bytes = json.dumps(associated_data, sort_keys=True).encode("utf-8") if associated_data else None
        
        plaintext_bytes = dek_cipher.decrypt(nonce, ciphertext, ad_bytes)
        return plaintext_bytes.decode("utf-8")
