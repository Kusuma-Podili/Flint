from typing import Dict, Any, List, Tuple

class PolicyEngine:
    def evaluate_s3_resource(self, resource: Dict[str, Any]) -> Tuple[bool, str]:
        if not resource.get("server_side_encryption", False):
            return False, "S3 Bucket must have server-side encryption enabled (CIS 2.1.1)"
        return True, "Passed"

    def evaluate_k8s_pod_security(self, pod_spec: Dict[str, Any]) -> Tuple[bool, str]:
        sec = pod_spec.get("securityContext", {})
        if not sec.get("runAsNonRoot", False):
            return False, "Containers must run as non-root user (CIS 5.2.6)"
        return True, "Passed"

    def evaluate_security_group(self, ingress_rules: List[Dict[str, Any]]) -> Tuple[bool, str]:
        for rule in ingress_rules:
            if rule.get("port") == 22 and "0.0.0.0/0" in rule.get("cidr_blocks", []):
                return False, "Security groups must not allow unrestricted SSH (0.0.0.0/0 on port 22)"
        return True, "Passed"
