from typing import Dict, Any, List

class MetricsAggregator:
    def __init__(self):
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}

    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        key = name
        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
            key = f"{name}{{{label_str}}}"
        self.counters[key] = self.counters.get(key, 0.0) + value

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        key = name
        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
            key = f"{name}{{{label_str}}}"
        self.gauges[key] = value

    def export_prometheus_format(self) -> str:
        lines = []
        for k, v in self.counters.items():
            lines.append(f"# TYPE {k.split('{')[0]} counter")
            lines.append(f"{k} {v}")
        for k, v in self.gauges.items():
            lines.append(f"# TYPE {k.split('{')[0]} gauge")
            lines.append(f"{k} {v}")
        return "\n".join(lines)

class AlertManager:
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []

    def add_alert_rule(self, name: str, metric_name: str, threshold: float, condition: str, severity: str):
        self.rules.append({"name": name, "metric_name": metric_name, "threshold": threshold, "condition": condition, "severity": severity})

    def evaluate(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        fired = []
        for r in self.rules:
            val = metrics.get(r["metric_name"])
            if val is not None and ((r["condition"] == "GT" and val > r["threshold"]) or (r["condition"] == "LT" and val < r["threshold"])):
                fired.append({"rule_name": r["name"], "severity": r["severity"], "current_value": val})
        return fired
