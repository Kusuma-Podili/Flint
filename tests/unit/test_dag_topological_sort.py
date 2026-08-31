"""
Unit Tests for DAG Topological Sort & Staging
"""
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
        self.assertEqual(len(stages), 3)
        self.assertEqual(stages[0], ["build"])
        self.assertEqual(stages[1], ["test"])
        self.assertEqual(stages[2], ["deploy"])

    def test_diamond_parallel_pipeline(self):
        # build -> (unit-test, lint, sast) -> package -> deploy
        steps = [
            {"id": "build", "depends_on": []},
            {"id": "unit-test", "depends_on": ["build"]},
            {"id": "lint", "depends_on": ["build"]},
            {"id": "sast", "depends_on": ["build"]},
            {"id": "package", "depends_on": ["unit-test", "lint", "sast"]},
            {"id": "deploy", "depends_on": ["package"]}
        ]
        resolver = DAGResolver(steps)
        stages = resolver.get_execution_stages()
        self.assertEqual(len(stages), 4)
        self.assertEqual(stages[0], ["build"])
        self.assertEqual(set(stages[1]), {"unit-test", "lint", "sast"})
        self.assertEqual(stages[2], ["package"])
        self.assertEqual(stages[3], ["deploy"])

    def test_cycle_detection_exception(self):
        # A -> B -> C -> A (cycle)
        cyclic_steps = [
            {"id": "stepA", "depends_on": ["stepC"]},
            {"id": "stepB", "depends_on": ["stepA"]},
            {"id": "stepC", "depends_on": ["stepB"]}
        ]
        resolver = DAGResolver(cyclic_steps)
        has_cycle, path = resolver.detect_cycles()
        self.assertTrue(has_cycle)

        with self.assertRaises(ValueError):
            resolver.get_execution_stages()

    def test_variable_interpolation(self):
        template = "Deploying image ${{ vars.image_name }}:${{ vars.tag }} to ${{ env.cluster }}"
        context = {
            "vars": {"image_name": "nexusops/control-plane", "tag": "v1.4.2"},
            "env": {"cluster": "production-us-east"}
        }
        interpolated = VariableInterpolator.interpolate(template, context)
        self.assertEqual(interpolated, "Deploying image nexusops/control-plane:v1.4.2 to production-us-east")


if __name__ == "__main__":
    unittest.main()
