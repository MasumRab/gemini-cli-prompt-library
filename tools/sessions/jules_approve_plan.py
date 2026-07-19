import argparse
import sys

from tools.api.jules_api_client import JulesAPIClient


def approve_plan(session_id: str):
    client = JulesAPIClient()
    return client.approve_plan(session_id)

def main():
    parser = argparse.ArgumentParser(description="Approve the plan for a Jules session")
    parser.add_argument("session_id", help="Session ID")
    args = parser.parse_args()

    try:
        approve_plan(args.session_id)
        print("Plan approved successfully.")
    except Exception as e:
        print(f"Error approving plan: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
