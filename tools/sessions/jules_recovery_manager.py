import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

from .config import calculate_grade
from tools.api.jules_api_client import JulesAPIClient


# Session priorities (inverse of PR - 1 is highest priority)
# State names match the official Jules API v1alpha State enum:
#   STATE_UNSPECIFIED, QUEUED, PLANNING, AWAITING_PLAN_APPROVAL,
#   AWAITING_USER_FEEDBACK, IN_PROGRESS, PAUSED, FAILED, COMPLETED
SESSION_STATE_PRIORITY = {
    "FAILED": 1,                    # Needs immediate recovery
    "PAUSED": 2,                    # Needs review/input
    "AWAITING_USER_FEEDBACK": 2,    # Needs user input
    "AWAITING_PLAN_APPROVAL": 2,    # Needs plan approval
    "IN_PROGRESS": 3,               # In progress - monitor
    "QUEUED": 3,                    # Queued - monitor
    "PLANNING": 3,                  # Planning - monitor
    "COMPLETED": 4,                 # Done - audit later
    "STATE_UNSPECIFIED": 5,         # Unknown/unspecified state
    "UNKNOWN": 5,                   # Fallback for missing state field
}


class RecoveryStrategy:
    def execute(self, session_id: str, client: JulesAPIClient):
        pass


class RetryLastMessageStrategy(RecoveryStrategy):
    def execute(self, session_id: str, client: JulesAPIClient):
        print(f"Executing RetryLastMessageStrategy for {session_id}")
        client.send_message(session_id, "Please retry the last step.")


class ApprovePlanStrategy(RecoveryStrategy):
    def execute(self, session_id: str, client: JulesAPIClient):
        print(f"Executing ApprovePlanStrategy for {session_id}")
        client.approve_plan(session_id)


class JulesRecoveryManager:
    def __init__(self, client: JulesAPIClient = None):
        self.client = client or JulesAPIClient()
        self.strategies = {
            "retry": RetryLastMessageStrategy(),
            "approve": ApprovePlanStrategy()
        }

    def get_session_priority(self, state: str) -> Tuple[int, str]:
        """Get priority level and reason for a session state."""
        priority = SESSION_STATE_PRIORITY.get(state, 5)
        reasons = {
            1: "Session failed - needs recovery",
            2: "Session paused/waiting - needs input",
            3: "Session running - monitor",
            4: "Session completed - audit later",
            5: "Unknown state"
        }
        return priority, reasons.get(priority, "Unknown")

    def analyze_session_state(self, session_id: str) -> Dict[str, Any]:
        """
        Analyzes the current state of a session and forms a hypothesis for recovery if needed.
        Returns priority-aware report.
        """
        session = self.client.get_session(session_id)
        activities = list(
            self.client.list_activities(session_id, page_size=20, max_results=20)
        )

        state = session.get("state", "UNKNOWN")
        priority, priority_reason = self.get_session_priority(state)

        report = {
            "session_id": session_id,
            "state": state,
            "priority": priority,
            "priority_reason": priority_reason,
            "hypothesis": "No action needed",
            "action": None
        }

        if state == "FAILED":
            # Hypothesis: It might be due to a transient error or a stuck activity
            report["hypothesis"] = "Session failed, likely transient error"
            report["action"] = "retry"
        elif state in ["PAUSED", "AWAITING_USER_FEEDBACK", "AWAITING_PLAN_APPROVAL"]:
            report["hypothesis"] = "Session is waiting for user input or approval"
            report["action"] = "approve"  # Default suggestion if plan generated
        elif state == "COMPLETED":
            grade, score = calculate_grade({"activities": activities, "completion_rate": 1.0})
            report["hypothesis"] = f"Session completed with grade {grade}"
            report["action"] = "AUDIT"

        return report

    def trigger_recovery(self, session_id: str, action: str):
        """
        Triggers a recovery action based on the analysis or explicit request.
        """
        if action in self.strategies:
            self.strategies[action].execute(session_id, self.client)
        elif action == "AUDIT":
            print(f"Triggering safety audit for completed session {session_id}...")
            # Use subprocess.run for safe argument passing (no shell injection risk)
            subprocess.run(
                [sys.executable, "-m", "tools.pr.jules_audit_session_pr", "--session", session_id],
                check=False
            )
        else:
            print(f"No specific recovery action for {action}")

    def recover(self, session_id: str, strategy_name: str):
        """Execute a specific recovery strategy."""
        strategy = self.strategies.get(strategy_name)
        if strategy:
            strategy.execute(session_id, self.client)
        else:
            print(f"Unknown strategy: {strategy_name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m tools.sessions.jules_recovery_manager <session_id> [strategy]")
        sys.exit(1)

    session_id = sys.argv[1]
    manager = JulesRecoveryManager()
    
    if len(sys.argv) > 2:
        strategy = sys.argv[2]
        manager.recover(session_id, strategy)
    else:
        report = manager.analyze_session_state(session_id)
        print(json.dumps(report, indent=2))
        if report["action"]:
            manager.trigger_recovery(session_id, report["action"])
