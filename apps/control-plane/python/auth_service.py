"""
NexusOps Core Python Auth, RBAC & Token Verification Engine
"""
import hashlib
import hmac
import os
import secrets
import time
from typing import Dict, List, Optional, Tuple

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "SUPER_ADMIN": ["*"],
    "ORG_ADMIN": [
        "pipelines:create", "pipelines:read", "pipelines:update", "pipelines:delete", "pipelines:execute",
        "runners:register", "runners:read", "runners:manage",
        "iac:plan", "iac:apply", "iac:drift", "iac:manage",
        "k8s:deploy", "k8s:rollback", "k8s:manage",
        "secrets:create", "secrets:read", "secrets:update", "secrets:delete",
        "security:audit", "security:manage_policy",
        "users:manage", "apikeys:manage", "tenant:settings"
    ],
    "DEVOPS_ENGINEER": [
        "pipelines:create", "pipelines:read", "pipelines:update", "pipelines:execute",
        "runners:read",
        "iac:plan", "iac:apply", "iac:drift",
        "k8s:deploy", "k8s:rollback",
        "secrets:create", "secrets:read",
        "security:audit"
    ],
    "DEVELOPER": [
        "pipelines:read", "pipelines:execute",
        "runners:read",
        "iac:plan",
        "k8s:read",
        "security:read"
    ],
    "SECURITY_AUDITOR": [
        "pipelines:read",
        "iac:read",
        "k8s:read",
        "security:audit", "security:manage_policy",
        "audit:read"
    ],
    "VIEWER": [
        "pipelines:read",
        "runners:read",
        "iac:read",
        "k8s:read",
        "security:read"
    ]
}


class AuthEngine:
    """Production-grade authentication & RBAC validator."""

    def __init__(self, jwt_secret: str = "nexusops-dev-secret-super-secure-key-32b"):
        self.jwt_secret = jwt_secret.encode("utf-8")

    def hash_password(self, password: str) -> str:
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
        return f"{salt}:{pwd_hash.hex()}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            salt, orig_hash = stored_hash.split(":", 1)
            pwd_hash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
            return hmac.compare_digest(pwd_hash.hex(), orig_hash)
        except Exception:
            return False

    def generate_api_key(self, name: str) -> Tuple[str, str, str]:
        prefix = f"nx_{secrets.token_hex(4)}"
        secret_part = secrets.token_hex(32)
        full_key = f"{prefix}_{secret_part}"
        hashed_secret = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
        return full_key, prefix, hashed_secret

    def verify_api_key(self, provided_key: str, stored_hashed_secret: str) -> bool:
        computed_hash = hashlib.sha256(provided_key.encode("utf-8")).hexdigest()
        return hmac.compare_digest(computed_hash, stored_hashed_secret)

    def check_permission(self, role: str, required_permission: str) -> bool:
        perms = ROLE_PERMISSIONS.get(role, [])
        if "*" in perms:
            return True
        if required_permission in perms:
            return True
        scope = required_permission.split(":", 1)[0]
        if f"{scope}:*" in perms:
            return True
        return False
