import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("packages/dag-engine/python"))
from dag_engine import DAGResolver, VariableInterpolator


class TestDAGResolver(unittest.TestCase):

    def test_linear_pipeline_stages(self):
        steps = [
            {"id": "build", "depends_on": []},
            {"id": "test", "depends_on": ["build"]},
            {"id": "deploy", "depends_on": ["test"]}
        ]
        resolver = DAGResolver(steps)
        stages = resolver.get_execution_stages()
        self.assertEqual(stages, [["build"], ["test"], ["deploy"]])

    def test_diamond_parallel_pipeline(self):
        steps = [
            {"id": "checkout", "depends_on": []},
            {"id": "lint", "depends_on": ["checkout"]},
            {"id": "unit_test", "depends_on": ["checkout"]},
            {"id": "package", "depends_on": ["lint", "unit_test"]}
        ]
        resolver = DAGResolver(steps)
        stages = resolver.get_execution_stages()
        self.assertEqual(stages[0], ["checkout"])
        self.assertEqual(set(stages[1]), {"lint", "unit_test"})
        self.assertEqual(stages[2], ["package"])

    def test_cycle_detection_exception(self):
        steps = [
            {"id": "stepA", "depends_on": ["stepB"]},
            {"id": "stepB", "depends_on": ["stepA"]}
        ]
        resolver = DAGResolver(steps)
        has_cycle, _ = resolver.detect_cycles()
        self.assertTrue(has_cycle)
        with self.assertRaises(ValueError):
            resolver.get_execution_stages()

    def test_variable_interpolation(self):
        template = "Deploy ${{ vars.image }}:${{ vars.tag }}"
        ctx = {"vars": {"image": "app", "tag": "v1.0"}}
        self.assertEqual(VariableInterpolator.interpolate(template, ctx), "Deploy app:v1.0")


if __name__ == "__main__":
    unittest.main()
