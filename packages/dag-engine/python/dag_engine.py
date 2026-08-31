"""
NexusOps Python DAG Topological Sorter & Graph Engine
"""
from typing import Dict, List, Set, Any, Tuple
from collections import defaultdict, deque


class DAGResolver:
    """Production topological sort and cycle detector for distributed pipeline steps."""

    def __init__(self, steps: List[Dict[str, Any]]):
        self.steps = {s["id"]: s for s in steps}
        self.adj: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = {s["id"]: 0 for s in steps}
        self._build_graph(steps)

    def _build_graph(self, steps: List[Dict[str, Any]]):
        for step in steps:
            step_id = step["id"]
            deps = step.get("depends_on", [])
            for dep in deps:
                if dep not in self.steps:
                    raise ValueError(f"Step '{step_id}' depends on unknown step '{dep}'")
                self.adj[dep].append(step_id)
                self.in_degree[step_id] += 1

    def detect_cycles(self) -> Tuple[bool, List[str]]:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycle_path: List[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            cycle_path.append(node)

            for neighbor in self.adj[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    cycle_path.append(neighbor)
                    return True

            rec_stack.remove(node)
            cycle_path.pop()
            return False

        for node_id in self.steps:
            if node_id not in visited:
                if dfs(node_id):
                    return True, cycle_path

        return False, []

    def get_execution_stages(self) -> List[List[str]]:
        has_cycle, path = self.detect_cycles()
        if has_cycle:
            raise ValueError(f"Cycle detected in pipeline graph: {' -> '.join(path)}")

        in_deg = dict(self.in_degree)
        current_wave = [node for node, deg in in_deg.items() if deg == 0]
        stages: List[List[str]] = []

        while current_wave:
            stages.append(list(current_wave))
            next_wave = []
            for node in current_wave:
                for dependent in self.adj[node]:
                    in_deg[dependent] -= 1
                    if in_deg[dependent] == 0:
                        next_wave.append(dependent)
            current_wave = next_wave

        return stages


class VariableInterpolator:
    """Dynamic expression and variable interpolator for pipelines."""

    @staticmethod
    def interpolate(text: str, context: Dict[str, Any]) -> str:
        import re
        pattern = r"\$\{\{\s*([\w\.\-]+)\s*\}\}"

        def replace_match(match):
            key = match.group(1).strip()
            parts = key.split(".")
            val = context
            for p in parts:
                if isinstance(val, dict) and p in val:
                    val = val[p]
                else:
                    return match.group(0)
            return str(val)

        return re.sub(pattern, replace_match, text)
