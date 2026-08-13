import unittest
import sys
import os

def run_all_tests():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)
    sys.path.insert(0, os.path.join(project_root, "apps", "control-plane", "python"))
    sys.path.insert(0, os.path.join(project_root, "apps", "runner-agent", "python"))
    sys.path.insert(0, os.path.join(project_root, "packages", "dag-engine", "python"))
    sys.path.insert(0, os.path.join(project_root, "packages", "iac-parser", "python"))
    sys.path.insert(0, os.path.join(project_root, "packages", "policy-engine", "python"))
    sys.path.insert(0, os.path.join(test_dir, "unit"))

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(test_dir, "unit"), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 70)
    print("  FLINT ENTERPRISE AUTOMATED TEST RUNNER")
    print("=" * 70)
    print(f"Executed {result.testsRun} test cases.")
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
