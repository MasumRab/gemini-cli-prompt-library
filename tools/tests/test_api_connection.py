import itertools
import sys

from tools.api.jules_api_client import JulesAPIClient


def test_connection():
    """Test the Jules API connection by fetching one session.

    Uses itertools.islice to avoid exhausting pagination.
    """
    print("Testing Jules API connection...")
    try:
        client = JulesAPIClient()
        sessions = list(itertools.islice(client.list_sessions(page_size=1), 1))
        count = len(sessions)
        print(f"Connection successful. Got {count} session(s).")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
