from typing import Dict, Any, Tuple

class CanaryRolloutController:
    def __init__(self, step_percentage: int = 25, max_failure_rate: float = 0.01):
        self.step = step_percentage
        self.max_failure_rate = max_failure_rate

    def calculate_next_weights(self, current_weight: int) -> int:
        return min(100, current_weight + self.step)

    def should_rollback(self, total_requests: int, failed_requests: int) -> Tuple[bool, str]:
        if total_requests == 0:
            return False, "No traffic"
        rate = failed_requests / total_requests
        if rate > self.max_failure_rate:
            return True, f"Failure rate {rate:.2%} exceeded threshold {self.max_failure_rate:.2%}"
        return False, "Healthy"

class BlueGreenDeployer:
    def __init__(self):
        self.active_color = "blue"

    def promote(self):
        self.active_color = "green" if self.active_color == "blue" else "blue"

class HelmManifestGenerator:
    @staticmethod
    def generate_deployment(name: str, image: str, replicas: int = 3, port: int = 8080) -> Dict[str, Any]:
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": name},
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {"labels": {"app": name}},
                    "spec": {"containers": [{"name": name, "image": image, "ports": [{"containerPort": port}]}]}
                }
            }
        }
