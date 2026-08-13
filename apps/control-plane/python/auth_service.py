import hashlib
import os
import secrets
from typing import Dict, List, Optional, Tuple

class AuthEngine:
    ROLE_PERMISSIONS: Dict[str, List[str]] = {
        "ADMIN": ["*"],
        "DEVOPS_ENGINEER": ["pipelines:*", "iac:*", "deployments:*", "runners:*"],
        "DEVELOPER": ["pipelines:read", "pipelines:execute", "logs:read"],
        "VIEWER": ["pipelines:read", "logs:read", "metrics:read"]
    }

    def hash_password(self, password: str, salt: bytes = None) -> Tuple[str, str]:
        if not salt:
            salt = secrets.token_bytes(16)
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hashed.hex(), salt.hex()

    def verify_password(self, password: str, hashed_hex: str, salt_hex: str) -> bool:
        salt = bytes.fromhex(salt_hex)
        check_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000).hex()
        return secrets.compare_digest(hashed_hex, check_hash)

    def generate_api_key(self, name: str) -> Tuple[str, str, str]:
        prefix = f"nx_{secrets.token_hex(4)}"
        secret_part = secrets.token_urlsafe(32)
        full_key = f"{prefix}_{secret_part}"
        hashed_key = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
        return full_key, prefix, hashed_key

    def validate_api_key(self, raw_key: str, stored_hash: str) -> bool:
        computed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return secrets.compare_digest(computed, stored_hash)

    def check_permission(self, role: str, required_permission: str) -> bool:
        allowed = self.ROLE_PERMISSIONS.get(role, [])
        if "*" in allowed:
            return True
        for perm in allowed:
            if perm.endswith(":*") and required_permission.startswith(perm[:-2]):
                return True
            if perm == required_permission:
                return True
        return False
