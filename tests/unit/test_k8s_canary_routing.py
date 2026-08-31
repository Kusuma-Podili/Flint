"""
Unit Tests for Kubernetes Canary Traffic Routing & Blue-Green Cutover
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from k8s_controller import CanaryRolloutController, BlueGreenDeployer, HelmManifestGenerator


class TestK8sControllers(unittest.TestCase):

    def test_canary_step_progression(self):
        canary = CanaryRolloutController(step_percentage=20)
        
        weight = 0
        weight = canary.calculate_next_weights(weight)
        self.assertEqual(weight, 20)

        weight = canary.calculate_next_weights(weight)
        self.assertEqual(weight, 40)

        # Skip to 90
        weight = canary.calculate_next_weights(90)
        self.assertEqual(weight, 100)

    def test_canary_health_check_and_rollback(self):
        canary = CanaryRolloutController(max_failure_rate=0.01) # max 1% error rate
        
        # 1000 requests, 5 errors = 0.5% (healthy)
        rollback, reason = canary.should_rollback(total_requests=1000, failed_requests=5)
        self.assertFalse(rollback)

        # 1000 requests, 30 errors = 3.0% (unhealthy -> trigger rollback)
        rollback, reason = canary.should_rollback(total_requests=1000, failed_requests=30)
        self.assertTrue(rollback)
        self.assertIn("exceeded threshold", reason)

    def test_blue_green_promotion(self):
        bg = BlueGreenDeployer()
        self.assertEqual(bg.active_color, "blue")
        new_active = bg.promote_idle_environment()
        self.assertEqual(new_active, "green")
        self.assertEqual(bg.idle_color, "blue")

    def test_manifest_generation(self):
        manifest = HelmManifestGenerator.generate_deployment_manifest(
            app_name="order-service",
            namespace="production",
            image="registry.nexusops.io/order-svc:v2.1.0",
            replicas=5
        )
        self.assertEqual(manifest["metadata"]["name"], "order-service")
        self.assertEqual(manifest["spec"]["replicas"], 5)
        self.assertEqual(manifest["spec"]["template"]["spec"]["containers"][0]["image"], "registry.nexusops.io/order-svc:v2.1.0")


if __name__ == "__main__":
    unittest.main()
