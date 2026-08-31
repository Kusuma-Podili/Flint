"""
NexusOps Security Scanner: Trivy Vulnerability Parser & Secret Entropy Detector
"""
import math
import re
from typing import Dict, Any, List


class SecretEntropyScanner:
    """Scans code, configurations, and git diffs for leaked secrets and high-entropy credentials."""

    COMMON_PATTERNS = [
        ("AWS Access Key", r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
        ("Generic Private Key", r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        ("GitHub Personal Access Token", r"ghp_[a-zA-Z0-9]{36}"),
        ("Slack Bot Token", r"xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}"),
        ("Stripe API Key", r"sk_live_[0-9a-zA-Z]{24}")
    ]

    @staticmethod
    def calculate_shannon_entropy(data: str) -> float:
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        freq = {}
        for char in data:
            freq[char] = freq.get(char, 0) + 1
        for count in freq.values():
            p = count / length
            entropy -= p * math.log2(p)
        return entropy

    @classmethod
    def scan_content(cls, content: str) -> List[Dict[str, Any]]:
        findings = []

        # 1. Regex Matchers
        for name, pattern in cls.COMMON_PATTERNS:
            matches = re.finditer(pattern, content)
            for m in matches:
                findings.append({
                    "type": "KNOWN_SECRET_PATTERN",
                    "secret_name": name,
                    "matched_snippet": m.group(0)[:8] + "...",
                    "start_pos": m.start()
                })

        # 2. High Entropy String Detection (tokens with entropy > 4.5 and length > 20)
        tokens = re.findall(r"[A-Za-z0-9+/=_-]{24,}", content)
        for token in tokens:
            entropy = cls.calculate_shannon_entropy(token)
            if entropy > 4.5:
                findings.append({
                    "type": "HIGH_ENTROPY_STRING",
                    "entropy": round(entropy, 2),
                    "token_snippet": token[:6] + "..."
                })

        return findings


class TrivyVulnerabilityParser:
    """Parses Trivy vulnerability reports and computes security posture."""

    @staticmethod
    def parse_trivy_report(trivy_json: Dict[str, Any]) -> Dict[str, Any]:
        critical = 0
        high = 0
        medium = 0
        low = 0
        vulnerabilities = []

        results = trivy_json.get("Results", [])
        for res in results:
            for vuln in res.get("Vulnerabilities", []):
                sev = vuln.get("Severity", "UNKNOWN").upper()
                if sev == "CRITICAL":
                    critical += 1
                elif sev == "HIGH":
                    high += 1
                elif sev == "MEDIUM":
                    medium += 1
                elif sev == "LOW":
                    low += 1

                vulnerabilities.append({
                    "cve_id": vuln.get("VulnerabilityID"),
                    "pkg_name": vuln.get("PkgName"),
                    "installed_version": vuln.get("InstalledVersion"),
                    "fixed_version": vuln.get("FixedVersion"),
                    "severity": sev,
                    "title": vuln.get("Title", "No title")
                })

        score = max(0, 100 - (critical * 15 + high * 5 + medium * 1))

        return {
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "total_vulnerabilities": len(vulnerabilities),
            "compliance_score": score,
            "vulnerabilities": vulnerabilities
        }
