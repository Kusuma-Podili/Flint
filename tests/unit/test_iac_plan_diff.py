"""
Unit Tests for IaC Plan Diffing and Resource Mutation Counting
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("packages/iac-parser/python"))
from iac_engine import TerraformPlanAnalyzer, DriftDetector


class TestIaCPlan(unittest.TestCase):

    def test_terraform_plan_parsing(self):
        sample_plan = {
            "resource_changes": [
                {
                    "address": "aws_instance.web_server",
                    "type": "aws_instance",
                    "change": {"actions": ["create"]}
                },
                {
                    "address": "aws_security_group.allow_http",
                    "type": "aws_security_group",
                    "change": {"actions": ["update"]}
                },
                {
                    "address": "aws_s3_bucket.legacy_logs",
                    "type": "aws_s3_bucket",
                    "change": {"actions": ["delete"]}
                }
            ]
        }
        analysis = TerraformPlanAnalyzer.parse_plan(sample_plan)
        self.assertEqual(analysis["to_add"], 1)
        self.assertEqual(analysis["to_change"], 1)
        self.assertEqual(analysis["to_destroy"], 1)
        self.assertEqual(analysis["total_mutations"], 3)
        self.assertTrue(analysis["has_destructions"])

    def test_drift_detection(self):
        desired = {
            "instance_type": "t3.xlarge",
            "min_size": 3,
            "max_size": 10,
            "encryption_enabled": True
        }
        # In cloud, someone manually changed min_size to 1 and encryption_enabled to False
        live = {
            "instance_type": "t3.xlarge",
            "min_size": 1,
            "max_size": 10,
            "encryption_enabled": False
        }

        has_drift, items = DriftDetector.evaluate_drift(desired, live)
        self.assertTrue(has_drift)
        self.assertEqual(len(items), 2)
        drifted_props = [item["property"] for item in items]
        self.assertIn("min_size", drifted_props)
        self.assertIn("encryption_enabled", drifted_props)


if __name__ == "__main__":
    unittest.main()
