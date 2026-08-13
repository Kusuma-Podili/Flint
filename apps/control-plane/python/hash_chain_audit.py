import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple

class HashChainAuditLogger:
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        self.chain: List[Dict[str, Any]] = []

    def record_entry(self, tenant_id: str, user_id: str, user_email: str, action: str, resource_type: str, resource_id: str, ip_address: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        prev_hash = self.chain[-1]["current_hash"] if self.chain else self.GENESIS_HASH
        seq_num = len(self.chain) + 1
        ts = time.time()
        entry_data = {
            "sequence_number": seq_num,
            "timestamp": ts,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "user_email": user_email,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "ip_address": ip_address,
            "payload": payload,
            "previous_hash": prev_hash
        }
        current_hash = hashlib.sha256(json.dumps(entry_data, sort_keys=True).encode("utf-8")).hexdigest()
        entry_data["current_hash"] = current_hash
        self.chain.append(entry_data)
        return entry_data

    def verify_integrity(self) -> Tuple[bool, Optional[str]]:
        for i, entry in enumerate(self.chain):
            expected_prev = self.chain[i - 1]["current_hash"] if i > 0 else self.GENESIS_HASH
            if entry["previous_hash"] != expected_prev:
                return False, f"Broken chain link at index {i}"
            check_data = {k: v for k, v in entry.items() if k != "current_hash"}
            computed = hashlib.sha256(json.dumps(check_data, sort_keys=True).encode("utf-8")).hexdigest()
            if computed != entry["current_hash"]:
                return False, f"Tampering detected at index {i}"
        return True, None
