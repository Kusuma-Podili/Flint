"""
NexusOps Pre-commit Secret Detection Hook
"""
from security_scanner import SecretEntropyScanner

def scan_git_diff(diff_text: str) -> bool:
    findings = SecretEntropyScanner.scan_content(diff_text)
    return len(findings) == 0
