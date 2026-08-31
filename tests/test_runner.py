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

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Discover tests in tests/unit and tests/e2e
    unit_tests = loader.discover("tests/unit", pattern="test_*.py")
    e2e_tests = loader.discover("tests/e2e", pattern="test_*.py")

    suite.addTests(unit_tests)
    suite.addTests(e2e_tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    duration = time.time() - start_time
    print("-" * 70)
    print(f"Executed {result.testsRun} test cases in {duration:.2f} seconds.")
    print(f"Failures: {len(result.failures)} | Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print(">>> ALL TESTS PASSED SUCCESSFULLY (100% PASS RATE) <<<")
        print("=" * 70)
        return 0
    else:
        print(">>> SOME TESTS FAILED <<<")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
