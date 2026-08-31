"""
NexusOps Notification Dispatcher for Slack & PagerDuty
"""
import json
from typing import Dict, Any

class NotificationDispatcher:
    @staticmethod
    def format_slack_payload(title: str, message: str, color: str = "#EF4444") -> Dict[str, Any]:
        return {
            "attachments": [{
                "title": title,
                "text": message,
                "color": color,
                "footer": "NexusOps DevSecOps Alert Engine"
            }]
        }
