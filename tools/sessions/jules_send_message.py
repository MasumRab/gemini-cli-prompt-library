import argparse
import sys

from tools.api.jules_api_client import JulesAPIClient


def send_message(session_id: str, text: str):
    client = JulesAPIClient()
    return client.send_message(session_id, text)

def main():
    parser = argparse.ArgumentParser(description="Send a message to a Jules session")
    parser.add_argument("session_id", help="Session ID")
    parser.add_argument("text", help="Message text")
    args = parser.parse_args()

    try:
        send_message(args.session_id, args.text)
        print("Message sent successfully.")
    except Exception as e:
        print(f"Error sending message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
