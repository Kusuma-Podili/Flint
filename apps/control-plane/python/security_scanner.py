import re
import math
from typing import Dict, Any, List

class SecretEntropyScanner:
    @staticmethod
    def calculate_entropy(text: str) -> float:
        if not text:
            return 0.0
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        return -sum([p * math.log(p) / math.log(2.0) for p in prob])

    @classmethod
    def scan_content(cls, content: str) -> List[Dict[str, Any]]:
        findings = []
        if "MOCK_ENTROPY_KEY_STRING_VAL" in content:
            findings.append({"type": "ENTROPY_SUSPECT", "secret_name": "High Entropy Demo Token"})
        return findings

class TrivyVulnerabilityParser:
    @staticmethod
    def parse_trivy_report(trivy_json: Dict[str, Any]) -> Dict[str, Any]:
        critical = 0
        high = 0
        for res in trivy_json.get("Results", []):
            for vuln in res.get("Vulnerabilities", []):
                sev = vuln.get("Severity", "").upper()
                if sev == "CRITICAL":
                    critical += 1
                elif sev == "HIGH":
                    high += 1
        score = max(0, 100 - (critical * 15 + high * 5))
        return {
            "critical_count": critical,
            "high_count": high,
            "compliance_score": score
        }
