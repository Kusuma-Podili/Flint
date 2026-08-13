import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("apps/control-plane/python"))
from observability_engine import MetricsAggregator, AlertManager


class TestObservability(unittest.TestCase):

    def test_prometheus_metrics_export(self):
        agg = MetricsAggregator()
        agg.increment_counter("runs_total", 5, {"status": "success"})
        prom = agg.export_prometheus_format()
        self.assertIn("runs_total", prom)

    def test_alert_threshold_trigger(self):
        mgr = AlertManager()
        mgr.add_alert_rule("High CPU", "cpu", 80.0, "GT", "CRITICAL")
        alerts = mgr.evaluate({"cpu": 95.0})
        self.assertEqual(len(alerts), 1)


if __name__ == "__main__":
    unittest.main()
