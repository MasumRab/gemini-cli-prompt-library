#!/usr/bin/env python3
"""Unified Jules CLI — all operations via JulesAPIClient (REST API).

Usage:
    uv run python3 -m tools.cli.jules-manager list [page_size]
    uv run python3 -m tools.cli.jules-manager session <session_id>
    uv run python3 -m tools.cli.jules-manager send <session_id> <message>
    uv run python3 -m tools.cli.jules-manager approve <session_id>
    uv run python3 -m tools.cli.jules-manager create <owner/repo> <prompt>
    uv run python3 -m tools.cli.jules-manager ask <session_id> <question>
    uv run python3 -m tools.cli.jules-manager wait <session_id> <state>
    uv run python3 -m tools.cli.jules-manager archive <session_id>
    uv run python3 -m tools.cli.jules-manager delete <session_id>
"""

import argparse
import json
import sys

from tools.api.jules_api_client import JulesAPIClient


def cmd_list(args):
    client = JulesAPIClient()
    sessions = list(client.list_sessions(page_size=min(max(args.page_size, 1), 50)))
    for s in sessions:
        pr = ""
        for o in s.get("outputs", []):
            if "pullRequest" in o:
                pr = f"  PR: {o['pullRequest'].get('url', '')}"
        print(f"{s.get('name', '?')}: {s.get('state', '?')}{pr}")


def cmd_session(args):
    client = JulesAPIClient()
    data = client.get_session(args.session_id)
    print(json.dumps(data, indent=2))


def cmd_send(args):
    client = JulesAPIClient()
    client.send_message(args.session_id, args.message)
    print("Message sent.")


def cmd_approve(args):
    client = JulesAPIClient()
    client.approve_plan(args.session_id)
    print("Plan approved.")


def cmd_create(args):
    client = JulesAPIClient()
    source = f"sources/github/{args.repo}"
    result = client.create_session(
        prompt=args.prompt,
        source=source,
        starting_branch=args.branch,
        title=args.title,
    )
    print(json.dumps(result, indent=2))


def cmd_ask(args):
    client = JulesAPIClient()
    try:
        reply = client.ask(args.session_id, args.question)
        print(json.dumps(reply, indent=2))
    except TimeoutError as e:
        print(f"Timeout: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_wait(args):
    client = JulesAPIClient()
    try:
        result = client.wait_for_state(args.session_id, args.state)
        print(json.dumps(result, indent=2))
    except TimeoutError as e:
        print(f"Timeout: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_archive(args):
    client = JulesAPIClient()
    client.archive_session(args.session_id)
    print("Session archived.")


def cmd_delete(args):
    client = JulesAPIClient()
    client.delete_session(args.session_id)
    print("Session deleted.")


def main():
    parser = argparse.ArgumentParser(description="Unified Jules CLI")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="List sessions")
    p_list.add_argument("page_size", nargs="?", type=int, default=20)

    p_session = sub.add_parser("session", help="Get session details")
    p_session.add_argument("session_id")

    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("session_id")
    p_send.add_argument("message")

    p_approve = sub.add_parser("approve", help="Approve plan")
    p_approve.add_argument("session_id")

    p_create = sub.add_parser("create", help="Create a new Jules session")
    p_create.add_argument("repo", help="owner/repo")
    p_create.add_argument("prompt")
    p_create.add_argument("--branch", default="main")
    p_create.add_argument("--title")

    p_ask = sub.add_parser("ask", help="Send a message and wait for agent reply")
    p_ask.add_argument("session_id")
    p_ask.add_argument("question")

    p_wait = sub.add_parser("wait", help="Poll until session reaches a state")
    p_wait.add_argument("session_id")
    p_wait.add_argument("state")

    p_archive = sub.add_parser("archive", help="Archive a session")
    p_archive.add_argument("session_id")

    p_delete = sub.add_parser("delete", help="Delete a session")
    p_delete.add_argument("session_id")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "list": cmd_list,
        "session": cmd_session,
        "send": cmd_send,
        "approve": cmd_approve,
        "create": cmd_create,
        "ask": cmd_ask,
        "wait": cmd_wait,
        "archive": cmd_archive,
        "delete": cmd_delete,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
