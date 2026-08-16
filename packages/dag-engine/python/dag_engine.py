import re
from typing import Dict, List, Set, Any, Tuple

class DAGResolver:
    def __init__(self, steps: List[Dict[str, Any]]):
        self.steps = {s["id"]: s for s in steps}
        self.graph: Dict[str, List[str]] = {s["id"]: s.get("depends_on", []) for s in steps}

    def detect_cycles(self) -> Tuple[bool, List[str]]:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycle_path: List[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for dep in self.graph.get(node, []):
                if dep not in self.steps:
                    continue
                if dep not in visited:
                    if dfs(dep):
                        cycle_path.append(node)
                        return True
                elif dep in rec_stack:
                    cycle_path.append(dep)
                    cycle_path.append(node)
                    return True
            rec_stack.remove(node)
            return False

        for step_id in self.steps:
            if step_id not in visited:
                if dfs(step_id):
                    return True, list(reversed(cycle_path))
        return False, []

    def get_execution_stages(self) -> List[List[str]]:
        has_cycle, path = self.detect_cycles()
        if has_cycle:
            raise ValueError(f"Cyclic dependency detected: {' -> '.join(path)}")

        in_degree: Dict[str, int] = {node: 0 for node in self.steps}
        dependents: Dict[str, List[str]] = {node: [] for node in self.steps}

        for node, deps in self.graph.items():
            for dep in deps:
                if dep in self.steps:
                    in_degree[node] += 1
                    dependents[dep].append(node)

        stages: List[List[str]] = []
        current_wave = [node for node, deg in in_degree.items() if deg == 0]

        while current_wave:
            stages.append(sorted(current_wave))
            next_wave = []
            for node in current_wave:
                for dependent in dependents[node]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_wave.append(dependent)
            current_wave = next_wave

        return stages

class VariableInterpolator:
    PATTERN = re.compile(r"\$\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")

    @classmethod
    def interpolate(cls, template: str, context: Dict[str, Any]) -> str:
        def replacer(match):
            path = match.group(1).split(".")
            curr = context
            for p in path:
                if isinstance(curr, dict) and p in curr:
                    curr = curr[p]
                else:
                    return match.group(0)
            return str(curr)
        return cls.PATTERN.sub(replacer, template)
