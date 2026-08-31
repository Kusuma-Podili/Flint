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
    sys.path.insert(0, os.path.join(test_dir, "unit"))
    sys.path.insert(0, os.path.join(test_dir, "e2e"))

    # Import test suites directly
    import test_auth_service
    import test_envelope_crypto
    import test_hash_chain_audit
    import test_dag_topological_sort
    import test_runner_pool
    import test_iac_plan_diff
    import test_k8s_canary_routing
    import test_gitops_webhook
    import test_policy_rego
    import test_security_scanners
    import test_metrics_and_alerts
    import test_platform_full_lifecycle

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for mod in [
        test_auth_service,
        test_envelope_crypto,
        test_hash_chain_audit,
        test_dag_topological_sort,
        test_runner_pool,
        test_iac_plan_diff,
        test_k8s_canary_routing,
        test_gitops_webhook,
        test_policy_rego,
        test_security_scanners,
        test_metrics_and_alerts,
        test_platform_full_lifecycle
    ]:
        suite.addTests(loader.loadTestsFromModule(mod))

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
