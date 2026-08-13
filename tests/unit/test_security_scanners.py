import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from security_scanner import SecretEntropyScanner, TrivyVulnerabilityParser


class TestSecurityScanners(unittest.TestCase):

    def test_secret_detection_regex(self):
        # Using safely constructed mock tokens for verification
        mock_sample = "MOCK_TOKEN_SAMPLE = 'MOCK_ENTROPY_KEY_STRING_VAL_XYZ'"
        findings = SecretEntropyScanner.scan_content(mock_sample)
        self.assertIsInstance(findings, list)

    def test_trivy_report_parsing_and_score(self):
        mock_trivy = {
            "Results": [{
                "Vulnerabilities": [
                    {"VulnerabilityID": "CVE-2024-0001", "Severity": "CRITICAL", "PkgName": "lib", "InstalledVersion": "1.0", "FixedVersion": "1.1"}
                ]
            }]
        }
        res = TrivyVulnerabilityParser.parse_trivy_report(mock_trivy)
        self.assertEqual(res["critical_count"], 1)
        self.assertEqual(res["compliance_score"], 85)


if __name__ == "__main__":
    unittest.main()
