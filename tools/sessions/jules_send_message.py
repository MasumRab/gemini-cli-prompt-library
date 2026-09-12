import argparse
import json
import sys

from tools.api.jules_api_client import JulesAPIClient
from tools.sdk.bridge import JulesSDKBridge


def send_message(session_id: str, text: str, await_reply: bool = False):
    """Send a message to a Jules session.
    
    Args:
        session_id: The Jules session ID
        text: The message text to send
        await_reply: If True, use SDK ask() which waits for agent reply.
                     If False, use REST send_message() (fire-and-forget).
    
    Returns:
        If await_reply=True: dict with the agent's reply activity
        If await_reply=False: dict with send_message response
    """
    if await_reply:
        bridge = JulesSDKBridge()
        return bridge.ask(session_id, text)
    
    client = JulesAPIClient()
    return client.send_message(session_id, text)

def main():
    parser = argparse.ArgumentParser(description="Send a message to a Jules session")
    parser.add_argument("session_id", help="Session ID")
    parser.add_argument("text", help="Message text")
    parser.add_argument("--await-reply", action="store_true", 
                        help="Wait for agent reply using SDK ask()")
    args = parser.parse_args()

    try:
        result = send_message(args.session_id, args.text, await_reply=args.await_reply)
        if args.await_reply:
            # SDK ask() returns the reply activity as JSON
            print(json.dumps(result, indent=2))
        else:
            print("Message sent successfully.")
    except Exception as e:
        print(f"Error sending message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
