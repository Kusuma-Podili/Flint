"""
NexusOps Observability Engine: Prometheus Metrics & Alert Escalation
"""
import time
from typing import Dict, Any, List, Optional


class MetricsAggregator:
    """Collects and exposes Prometheus-compatible metric gauges and counters."""

    def __init__(self):
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}

    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        key = self._format_key(name, labels)
        self.counters[key] = self.counters.get(key, 0.0) + value

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        key = self._format_key(name, labels)
        self.gauges[key] = value

    def _format_key(self, name: str, labels: Dict[str, str] = None) -> str:
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def export_prometheus_format(self) -> str:
        lines = []
        for key, val in self.counters.items():
            lines.append(f"# TYPE {key.split('{')[0]} counter")
            lines.append(f"{key} {val}")
        for key, val in self.gauges.items():
            lines.append(f"# TYPE {key.split('{')[0]} gauge")
            lines.append(f"{key} {val}")
        return "\n".join(lines)


class AlertManager:
    """Evaluates threshold alert conditions and routes notifications to Slack/PagerDuty."""

    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self.active_alerts: List[Dict[str, Any]] = []

    def add_alert_rule(self, name: str, metric_name: str, threshold: float, condition: str, severity: str):
        self.rules.append({
            "name": name,
            "metric_name": metric_name,
            "threshold": threshold,
            "condition": condition,
            "severity": severity
        })

    def evaluate(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        triggered = []
        for rule in self.rules:
            val = current_metrics.get(rule["metric_name"])
            if val is not None:
                is_fired = False
                if rule["condition"] == "GT" and val > rule["threshold"]:
                    is_fired = True
                elif rule["condition"] == "LT" and val < rule["threshold"]:
                    is_fired = True

                if is_fired:
                    alert_event = {
                        "rule_name": rule["name"],
                        "severity": rule["severity"],
                        "current_value": val,
                        "threshold": rule["threshold"],
                        "triggered_at": time.time()
                    }
                    triggered.append(alert_event)
        self.active_alerts = triggered
        return triggered
