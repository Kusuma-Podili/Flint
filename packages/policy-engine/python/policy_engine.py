"""
NexusOps DevSecOps OPA Rego Engine & Policy Validator
"""
import math
from typing import Dict, Any, List, Tuple


class PolicyRule:
    def __init__(self, rule_id: str, name: str, category: str, severity: str, description: str, remediation: str):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.severity = severity
        self.description = description
        self.remediation = remediation


class PolicyEngine:
    """Evaluates security guardrails on Terraform resources and K8s manifests."""

    def __init__(self):
        self.rules: List[PolicyRule] = []
        self._load_default_cis_rules()

    def _load_default_cis_rules(self):
        self.rules.append(PolicyRule(
            "CIS-AWS-S3-ENCRYPT",
            "S3 Bucket Must Enforce Server-Side Encryption",
            "STORAGE",
            "HIGH",
            "Unencrypted S3 buckets expose sensitive organizational data to exfiltration.",
            "Add server_side_encryption_configuration with AES256 or aws:kms."
        ))
        self.rules.append(PolicyRule(
            "CIS-K8S-NO-ROOT",
            "Containers Must Not Run As Root",
            "CONTAINER",
            "CRITICAL",
            "Running containers as root grants attackers privilege escalation inside the cluster.",
            "Set securityContext.runAsNonRoot = true and runAsUser >= 1000."
        ))
        self.rules.append(PolicyRule(
            "CIS-SEC-GROUP-NO-OPEN-SSH",
            "Security Groups Must Not Open Port 22 to 0.0.0.0/0",
            "NETWORK",
            "CRITICAL",
            "Exposing SSH publicly exposes compute instances to brute force attacks.",
            "Restrict ingress CIDR to corporate VPN or bastion host IP."
        ))

    def evaluate_s3_resource(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        if config.get("server_side_encryption") is True or "kms_key_id" in config:
            return True, "Passed: Server-side encryption configured."
        return False, "Failed: S3 bucket is unencrypted."

    def evaluate_k8s_pod_security(self, pod_spec: Dict[str, Any]) -> Tuple[bool, str]:
        sec_ctx = pod_spec.get("securityContext", {})
        if sec_ctx.get("runAsNonRoot") is True:
            return True, "Passed: Container configured to run as non-root."
        return False, "Failed: Container allows root execution."

    def evaluate_security_group(self, ingress_rules: List[Dict[str, Any]]) -> Tuple[bool, str]:
        for rule in ingress_rules:
            port = rule.get("port")
            cidr = rule.get("cidr_blocks", [])
            if (port == 22 or (rule.get("from_port") <= 22 <= rule.get("to_port", 0))) and "0.0.0.0/0" in cidr:
                return False, "Failed: Port 22 open to the entire internet (0.0.0.0/0)."
        return True, "Passed: SSH ingress properly restricted."
