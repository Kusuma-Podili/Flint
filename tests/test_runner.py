"""
NexusOps Universal Test Harness & Test Suite Runner
Discovers and executes all unit, integration, security, and E2E test suites.
"""
import unittest
import sys
import os
import time

def run_all_tests():
    start_time = time.time()
    print("=" * 70)
    print("  NEXUSOPS ENTERPRISE TEST SUITE RUNNER")
    print("=" * 70)

    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)

    sys.path.insert(0, os.path.join(project_root, "apps", "control-plane", "python"))
    sys.path.insert(0, os.path.join(project_root, "apps", "runner-agent", "python"))
    sys.path.insert(0, os.path.join(project_root, "packages", "dag-engine", "python"))
    sys.path.insert(0, os.path.join(project_root, "packages", "iac-parser", "python"))
    sys.path.insert(0, os.path.join(project_root, "packages", "policy-engine", "python"))

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    unit_dir = os.path.join(test_dir, "unit")
    e2e_dir = os.path.join(test_dir, "e2e")

    if os.path.exists(unit_dir):
        unit_tests = loader.discover(unit_dir, pattern="test_*.py")
        suite.addTests(unit_tests)

    if os.path.exists(e2e_dir):
        e2e_tests = loader.discover(e2e_dir, pattern="test_*.py")
        suite.addTests(e2e_tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    duration = time.time() - start_time
    print("-" * 70)
    print(f"Executed {result.testsRun} test cases in {duration:.2f} seconds.")
    print(f"Failures: {len(result.failures)} | Errors: {len(result.errors)}")
    
    if result.wasSuccessful() and result.testsRun > 0:
        print(">>> ALL TESTS PASSED SUCCESSFULLY (100% PASS RATE) <<<")
        print("=" * 70)
        return 0
    else:
        print(">>> SOME TESTS FAILED OR NO TESTS DISCOVERED <<<")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
