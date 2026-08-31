"""
NexusOps Multi-Cloud IaC Engine, Plan Analyzer & Drift Detector
"""
import json
import time
from typing import Dict, Any, List, Tuple


class TerraformPlanAnalyzer:
    """Parses terraform plan json output and analyzes additions, modifications, and deletions."""

    @staticmethod
    def parse_plan(plan_data: Dict[str, Any]) -> Dict[str, Any]:
        to_add = 0
        to_change = 0
        to_destroy = 0
        changes_list = []

        resource_changes = plan_data.get("resource_changes", [])
        for rc in resource_changes:
            address = rc.get("address", "unknown")
            rtype = rc.get("type", "unknown")
            actions = rc.get("change", {}).get("actions", [])

            action_type = "no-op"
            if "create" in actions and "delete" in actions:
                action_type = "replace"
                to_change += 1
            elif "create" in actions:
                action_type = "create"
                to_add += 1
            elif "delete" in actions:
                action_type = "delete"
                to_destroy += 1
            elif "update" in actions:
                action_type = "update"
                to_change += 1

            changes_list.append({
                "address": address,
                "type": rtype,
                "action": action_type
            })

        return {
            "to_add": to_add,
            "to_change": to_change,
            "to_destroy": to_destroy,
            "total_mutations": to_add + to_change + to_destroy,
            "has_destructions": to_destroy > 0,
            "resources": changes_list
        }


class DriftDetector:
    """Detects configuration drift between desired state in Git and actual cloud infrastructure."""

    @staticmethod
    def evaluate_drift(desired_state: Dict[str, Any], live_state: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        drifted_items = []
        for key, desired_val in desired_state.items():
            live_val = live_state.get(key)
            if live_val is None:
                drifted_items.append({
                    "property": key,
                    "type": "MISSING_IN_CLOUD",
                    "desired": desired_val,
                    "actual": None
                })
            elif live_val != desired_val:
                drifted_items.append({
                    "property": key,
                    "type": "VALUE_MISMATCH",
                    "desired": desired_val,
                    "actual": live_val
                })

        for key, live_val in live_state.items():
            if key not in desired_state:
                drifted_items.append({
                    "property": key,
                    "type": "UNMANAGED_CLOUD_RESOURCE",
                    "desired": None,
                    "actual": live_val
                })

        has_drift = len(drifted_items) > 0
        return has_drift, drifted_items
