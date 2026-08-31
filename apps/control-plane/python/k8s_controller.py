"""
NexusOps Kubernetes Multi-Cluster Controller: Canary & Blue-Green Deployments
"""
import math
from typing import Dict, Any, List, Tuple


class CanaryRolloutController:
    """Controls progressive canary traffic shifting and metric health evaluation."""

    def __init__(self, step_percentage: int = 10, max_failure_rate: float = 0.02):
        self.step_percentage = step_percentage
        self.max_failure_rate = max_failure_rate

    def calculate_next_weights(self, current_canary_weight: int) -> int:
        next_weight = min(100, current_canary_weight + self.step_percentage)
        return next_weight

    def should_rollback(self, total_requests: int, failed_requests: int) -> Tuple[bool, str]:
        if total_requests == 0:
            return False, "No traffic"
        failure_rate = failed_requests / total_requests
        if failure_rate > self.max_failure_rate:
            return True, f"Error rate {failure_rate*100:.2f}% exceeded threshold {self.max_failure_rate*100:.2f}%"
        return False, "Healthy"


class BlueGreenDeployer:
    """Coordinates zero-downtime blue/green environment cutovers."""

    def __init__(self):
        self.active_color = "blue"
        self.idle_color = "green"

    def promote_idle_environment(self) -> str:
        self.active_color, self.idle_color = self.idle_color, self.active_color
        return self.active_color


class HelmManifestGenerator:
    """Generates standard Kubernetes manifests for deployments."""

    @staticmethod
    def generate_deployment_manifest(
        app_name: str,
        namespace: str,
        image: str,
        replicas: int = 3,
        port: int = 8080
    ) -> Dict[str, Any]:
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": app_name,
                "namespace": namespace,
                "labels": {"app.kubernetes.io/name": app_name}
            },
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": app_name}},
                "template": {
                    "metadata": {"labels": {"app": app_name}},
                    "spec": {
                        "containers": [{
                            "name": app_name,
                            "image": image,
                            "ports": [{"containerPort": port}],
                            "resources": {
                                "limits": {"cpu": "1000m", "memory": "1Gi"},
                                "requests": {"cpu": "200m", "memory": "256Mi"}
                            }
                        }]
                    }
                }
            }
        }
