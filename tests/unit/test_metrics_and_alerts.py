"""
Unit Tests for Observability & Alert Manager
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from observability_engine import MetricsAggregator, AlertManager


class TestObservability(unittest.TestCase):

    def test_prometheus_metrics_export(self):
        agg = MetricsAggregator()
        agg.increment_counter("nexus_pipeline_runs_total", 5, {"status": "success"})
        agg.set_gauge("nexus_active_runners", 12, {"cluster": "us-east-1"})

        prom_text = agg.export_prometheus_format()
        self.assertIn("nexus_pipeline_runs_total", prom_text)
        self.assertIn("nexus_active_runners", prom_text)
        self.assertIn('status="success"', prom_text)

    def test_alert_threshold_trigger(self):
        mgr = AlertManager()
        mgr.add_alert_rule(
            name="High CPU Utilization",
            metric_name="cluster_cpu_usage",
            threshold=85.0,
            condition="GT",
            severity="CRITICAL"
        )

        # Normal condition -> no alerts
        normal_metrics = {"cluster_cpu_usage": 45.2}
        alerts = mgr.evaluate(normal_metrics)
        self.assertEqual(len(alerts), 0)

        # Spike condition -> alert triggered
        spike_metrics = {"cluster_cpu_usage": 92.4}
        alerts = mgr.evaluate(spike_metrics)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["rule_name"], "High CPU Utilization")
        self.assertEqual(alerts[0]["severity"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
