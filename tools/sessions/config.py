import os

# JULES SESSION-STATE CONFIG
# Single source of truth for shared session-state constants across tools.
# Known non-action states — every other state (including unknown/future API
# states) is surfaced as "pending" so edge cases stay visible.
NO_ACTION_STATES = frozenset({"COMPLETED", "QUEUED", "PLANNING", "STATE_UNSPECIFIED"})


def likely_pending(state: str) -> bool:
    """Return True if a state likely needs user attention.

    Only known no-action states return False. Every other state (including
    unknown or future API states) returns True so the session is surfaced.
    """
    return state.upper() not in NO_ACTION_STATES


def normalize_state(state) -> str:
    """Uppercase a session state string, defaulting to "UNKNOWN"."""
    if not state:
        return "UNKNOWN"
    upper = str(state).upper()
    return upper if upper else "UNKNOWN"


# JULES API CONFIG
JULES_API_KEY = os.environ.get("JULES_API_KEY", "")
JULES_API_BASE_URL = "https://jules.googleapis.com/v1alpha"  # Correct endpoint

# A+ SCORING LOGIC
# Weights for different session attributes
WEIGHTS = {
    "completion_rate": 0.4,
    "activity_count": 0.2,
    "error_rate": -0.3,
    "feedback_quality": 0.2,
    "time_efficiency": 0.2
}

def calculate_grade(session_data):
    """
    Calculates a numeric grade and an A+ grade for a session.
    session_data: dict containing keys like 'completion_rate', 'activities', 'errors', etc.
    """
    score = 0
    score += (session_data.get("completion_rate", 0) * WEIGHTS["completion_rate"])
    score += (min(len(session_data.get("activities", [])), 10) / 10.0 * WEIGHTS["activity_count"])
    # Cap error_count at 3 to match error_rate weight (-0.3): 3 * -0.3 = -0.9
    # With perfect scores (1.0 - 0.9 = 0.1) this still allows passing grades
    # but prevents A+ with >3 errors, which is the intended behavior.
    error_count = min(session_data.get("error_count") or 0, 3)
    score += (error_count * WEIGHTS["error_rate"])
    score += (session_data.get("feedback_score", 0) * WEIGHTS["feedback_quality"])
    score += (session_data.get("time_efficiency", 1.0) * WEIGHTS["time_efficiency"])

    # Normalize to 0-100
    final_score = max(0, min(100, score * 100))

    if final_score >= 95:
        return "A+", final_score
    elif final_score >= 90:
        return "A", final_score
    elif final_score >= 80:
        return "B", final_score
    else:
        return "C", final_score

def validate_config():
    if not JULES_API_KEY:
        return False
    return True

# DAEMON CONFIG
MONITOR_INTERVAL = 60  # seconds
PID_FILE = "/tmp/jules_monitor.pid"

if __name__ == "__main__":
    if validate_config():
        print("Config is valid.")
    else:
        print("Error: JULES_API_KEY is not set in environment variables.")
