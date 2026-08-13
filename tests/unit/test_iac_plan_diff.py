import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("packages/iac-parser/python"))
from iac_engine import TerraformPlanAnalyzer, DriftDetector


class TestIaCPlan(unittest.TestCase):

    def test_terraform_plan_parsing(self):
        plan = {
            "resource_changes": [
                {"address": "aws_s3_bucket.data", "type": "aws_s3_bucket", "change": {"actions": ["create"]}},
                {"address": "aws_iam_role.admin", "type": "aws_iam_role", "change": {"actions": ["delete"]}}
            ]
        }
        res = TerraformPlanAnalyzer.parse_plan(plan)
        self.assertEqual(res["to_add"], 1)
        self.assertEqual(res["to_destroy"], 1)
        self.assertTrue(res["has_destructions"])

    def test_drift_detection(self):
        actual = {"replicas": 5}
        expected = {"replicas": 3}
        drift = DriftDetector.detect_drift(actual, expected)
        self.assertTrue(drift["has_drift"])


if __name__ == "__main__":
    unittest.main()
