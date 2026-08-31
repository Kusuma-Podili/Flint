"""
Unit Tests for Secret Scanner and Trivy Parser
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from security_scanner import SecretEntropyScanner, TrivyVulnerabilityParser


class TestSecurityScanners(unittest.TestCase):

    def test_secret_detection_regex(self):
        sample_code = """
        # Configuration file
        AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
        GITHUB_TOKEN = "ghp_111122223333444455556666777788889999"
        DATABASE_URL = "postgres://user:pass@localhost:5432/db"
        """
        findings = SecretEntropyScanner.scan_content(sample_code)
        self.assertGreaterEqual(len(findings), 2)
        secret_names = [f.get("secret_name") for f in findings if "secret_name" in f]
        self.assertIn("AWS Access Key", secret_names)
        self.assertIn("GitHub Personal Access Token", secret_names)

    def test_trivy_report_parsing_and_score(self):
        mock_trivy = {
            "Results": [{
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": "CVE-2023-44487",
                        "PkgName": "golang.org/x/net",
                        "InstalledVersion": "v0.12.0",
                        "FixedVersion": "v0.17.0",
                        "Severity": "CRITICAL",
                        "Title": "HTTP/2 Rapid Reset vulnerability"
                    },
                    {
                        "VulnerabilityID": "CVE-2023-38545",
                        "PkgName": "libcurl",
                        "InstalledVersion": "7.88.1",
                        "FixedVersion": "8.4.0",
                        "Severity": "HIGH",
                        "Title": "SOCKS5 heap buffer overflow"
                    }
                ]
            }]
        }
        res = TrivyVulnerabilityParser.parse_trivy_report(mock_trivy)
        self.assertEqual(res["critical_count"], 1)
        self.assertEqual(res["high_count"], 1)
        self.assertEqual(res["total_vulnerabilities"], 2)
        # Score = 100 - (1*15 + 1*5) = 80
        self.assertEqual(res["compliance_score"], 80)


if __name__ == "__main__":
    unittest.main()
