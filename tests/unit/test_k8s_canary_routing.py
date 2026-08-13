import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from k8s_controller import CanaryRolloutController, BlueGreenDeployer, HelmManifestGenerator


class TestK8sControllers(unittest.TestCase):

    def test_canary_step_progression(self):
        ctrl = CanaryRolloutController(step_percentage=25)
        self.assertEqual(ctrl.calculate_next_weights(0), 25)
        self.assertEqual(ctrl.calculate_next_weights(25), 50)
        self.assertEqual(ctrl.calculate_next_weights(100), 100)

    def test_canary_health_check_and_rollback(self):
        ctrl = CanaryRolloutController(max_failure_rate=0.01)
        rollback, _ = ctrl.should_rollback(total_requests=1000, failed_requests=50) # 5% error
        self.assertTrue(rollback)

    def test_blue_green_promotion(self):
        bg = BlueGreenDeployer()
        self.assertEqual(bg.active_color, "blue")
        bg.promote()
        self.assertEqual(bg.active_color, "green")

    def test_manifest_generation(self):
        manifest = HelmManifestGenerator.generate_deployment("app", "nginx:alpine", 3, 8080)
        self.assertEqual(manifest["metadata"]["name"], "app")


if __name__ == "__main__":
    unittest.main()
