"""
NexusOps Immutable Compliance Audit Subsystem with Cryptographic Hash Chaining
"""
import hashlib
import json
import time
from typing import Dict, Any, List, Optional


class HashChainAuditLogger:
    """Cryptographically tamper-evident append-only audit trail."""

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def record_entry(
        self,
        tenant_id: str,
        user_id: str,
        user_email: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        seq_num = len(self.audit_log) + 1
        prev_hash = self.audit_log[-1]["current_hash"] if self.audit_log else self.GENESIS_HASH
        timestamp = time.time()

        entry_payload = {
            "sequence_number": seq_num,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": ip_address,
            "details": details,
            "timestamp": timestamp,
            "previous_hash": prev_hash
        }

        serialized = json.dumps(entry_payload, sort_keys=True).encode("utf-8")
        current_hash = hashlib.sha256(serialized).hexdigest()

        entry = {
            **entry_payload,
            "current_hash": current_hash
        }
        self.audit_log.append(entry)
        return entry

    def verify_integrity(self) -> Tuple[bool, Optional[str]]:
        for i, entry in enumerate(self.audit_log):
            expected_prev_hash = self.audit_log[i - 1]["current_hash"] if i > 0 else self.GENESIS_HASH
            if entry["previous_hash"] != expected_prev_hash:
                return False, f"Broken chain link at sequence {entry['sequence_number']}: previous_hash mismatch"

            # Re-compute hash
            recalc_payload = {k: v for k, v in entry.items() if k != "current_hash"}
            serialized = json.dumps(recalc_payload, sort_keys=True).encode("utf-8")
            expected_current_hash = hashlib.sha256(serialized).hexdigest()
            if entry["current_hash"] != expected_current_hash:
                return False, f"Tampered entry detected at sequence {entry['sequence_number']}: current_hash mismatch"

        return True, None
