"""
NexusOps Istio & Envoy Traffic Shifter for Canary Rollouts
"""
from typing import Dict, Any

class TrafficShifter:
    @staticmethod
    def generate_virtual_service(service_name: str, canary_weight: int) -> Dict[str, Any]:
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "VirtualService",
            "metadata": {"name": service_name},
            "spec": {
                "hosts": [service_name],
                "http": [{
                    "route": [
                        {"destination": {"host": service_name, "subset": "stable"}, "weight": 100 - canary_weight},
                        {"destination": {"host": service_name, "subset": "canary"}, "weight": canary_weight}
                    ]
                }]
            }
        }
