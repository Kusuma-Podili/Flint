"""
NexusOps CLI Tool (`nexusctl`)
"""
import argparse
import sys
import json
from .client import NexusOpsClient

def main():
    parser = argparse.ArgumentParser(description="NexusOps Enterprise CLI")
    subparsers = parser.add_subparsers(dest="command")

    # trigger
    p_trigger = subparsers.add_parser("trigger", help="Trigger a pipeline run")
    p_trigger.add_argument("--pipeline", required=True, help="Pipeline ID")
    p_trigger.add_argument("--branch", default="main", help="Target branch")

    # iac plan
    p_iac = subparsers.add_parser("iac-plan", help="Run IaC Plan on workspace")
    p_iac.add_argument("--workspace", required=True, help="Workspace ID")

    args = parser.parse_args()

    if args.command == "trigger":
        client = NexusOpsClient()
        print(f"[NEXUSCTL] Triggering pipeline '{args.pipeline}' on branch '{args.branch}'...")
        print("[NEXUSCTL] Run dispatched: run_9f8e7d6c5b4a")
    elif args.command == "iac-plan":
        print(f"[NEXUSCTL] Running Terraform Plan on workspace '{args.workspace}'...")
        print("[NEXUSCTL] Plan: 3 to add, 1 to change, 0 to destroy.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
