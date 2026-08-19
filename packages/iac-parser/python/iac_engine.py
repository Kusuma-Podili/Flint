from typing import Dict, Any, List

class TerraformPlanAnalyzer:
    @staticmethod
    def parse_plan(plan_json: Dict[str, Any]) -> Dict[str, Any]:
        add_count = 0
        change_count = 0
        destroy_count = 0
        for change in plan_json.get("resource_changes", []):
            actions = change.get("change", {}).get("actions", [])
            if "create" in actions:
                add_count += 1
            if "update" in actions:
                change_count += 1
            if "delete" in actions:
                destroy_count += 1
        return {
            "to_add": add_count,
            "to_change": change_count,
            "to_destroy": destroy_count,
            "has_destructions": destroy_count > 0
        }

class DriftDetector:
    @staticmethod
    def detect_drift(actual_state: Dict[str, Any], desired_state: Dict[str, Any]) -> Dict[str, Any]:
        drifted_keys = []
        for k, v in desired_state.items():
            if k not in actual_state or actual_state[k] != v:
                drifted_keys.append(k)
        return {
            "has_drift": len(drifted_keys) > 0,
            "drifted_attributes": drifted_keys
        }
