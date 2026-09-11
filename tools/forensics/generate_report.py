#!/usr/bin/env python3
"""
Generate a data-driven forensics report for a Jules session.

Unlike the previous template-only generator, this version pulls live
session data via JulesAPIClient and embeds it in the report.

Usage:
    # Failure analysis report for a specific session
    uv run python -m tools.forensics.generate_report \
        --repo EmailIntelligence \
        --type failure_analysis \
        --session-id 596003508416904399 \
        --output workspaces/EmailIntelligence/analysis/forensics/

    # Pattern analysis report for a repo (no session ID needed)
    uv run python -m tools.forensics.generate_report \
        --repo EmailIntelligence \
        --type pattern_analysis \
        --output workspaces/EmailIntelligence/analysis/forensics/
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from tools.api.jules_api_client import JulesAPIClient
from tools.forensics.analyze_failures import analyze_session_failure
from tools.forensics.analyze_patterns import analyze_session_reuse

REPORT_TYPES = [
    "failure_analysis",
    "intervention_outcome",
    "pattern_analysis",
    "audit",
    "investigation",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_frontmatter(
    session_id: str,
    title: str,
    repo: str,
    report_type: str,
    confidence: str = "probable",
) -> Dict[str, Any]:
    """Generate frontmatter dict matching WORKSPACE_INTEGRATION.md spec."""
    return {
        "session": {
            "id": str(session_id),
            "title": title,
            "repository": repo,
            "created": utc_now(),
            "updated": utc_now(),
            "status": "completed",
            "source": "forensics",
        },
        "forensics": {
            "type": report_type,
            "confidence": confidence,
            "api_boundary": "https://jules.googleapis.com/v1alpha",
            "retrieval_timestamp": utc_now(),
        },
    }


def frontmatter_to_yaml(fm: Dict[str, Any]) -> str:
    """Render frontmatter dict as YAML without requiring PyYAML.

    Kept dependency-free: the frontmatter shape is flat two-level
    scalars, which we can emit deterministically.
    """
    lines = ["---"]
    for top_key, section in fm.items():
        lines.append(f"{top_key}:")
        for key, value in section.items():
            lines.append(f"  {key}: \"{value}\"")
    lines.append("---")
    return "\n".join(lines)


def fetch_session_data(
    client: JulesAPIClient, session_id: Optional[str], repo: Optional[str]
) -> Dict[str, Any]:
    """Fetch session data from the live API.

    Returns a dict with the session, its activities, and (for
    pattern_analysis) repo-wide session listings.
    """
    data: Dict[str, Any] = {"session": None, "activities": [], "sessions": []}

    if session_id:
        data["session"] = client.get_session(session_id)
        data["activities"] = list(client.list_activities(session_id, page_size=100))

    if repo:
        # list_sessions yields all sessions; filter client-side by repo
        all_sessions = list(client.list_sessions(page_size=50))
        data["sessions"] = [
            s for s in all_sessions
            if repo.lower() in str(s.get("repository", "")).lower()
            or repo.lower() in str(s.get("name", "")).lower()
        ]

    return data


def render_failure_analysis(
    session_id: str, analysis: Dict[str, Any], repo: str
) -> str:
    """Render failure analysis sections from analyze_failures output."""
    errors = analysis.get("errors", [])
    lines = [
        "## Summary",
        "",
        f"Session `{session_id}` "
        f"({'FAILED' if analysis.get('state') == 'FAILED' else analysis.get('state', 'unknown state')}) "
        f"recorded {len(errors)} error-bearing activit"
        f"{'y' if len(errors) == 1 else 'ies'} out of "
        f"{analysis.get('total_activities', 0)} total activities.",
        "",
    ]

    if not errors:
        lines += [
            "No activities explicitly flagged as errors were found. "
            "The failure may be recorded in the session-level error field "
            "or require manual inspection of the final activities.",
            "",
        ]

    lines += ["## Errors", ""]
    for i, err in enumerate(errors, 1):
        ts = err.get("createTime", err.get("timestamp", "unknown time"))
        text = str(err.get("text", err.get("message", "")))[:500]
        lines.append(f"### Error {i} — {ts}")
        lines.append("")
        lines.append(f"> {text}")
        lines.append("")

    return "\n".join(lines)


def render_pattern_analysis(analysis: Dict[str, Any]) -> str:
    """Render pattern analysis sections from analyze_patterns output."""
    duplicates = analysis.get("duplicates", {})
    total = analysis.get("total_sessions", 0)
    lines = [
        "## Summary",
        "",
        f"Analyzed {total} sessions. "
        f"Found {len(duplicates)} session group(s) sharing the same "
        "PR + head SHA (potential reuse or redundant runs).",
        "",
    ]

    if duplicates:
        lines += ["## Duplicate Groups", ""]
        for key, sessions in duplicates.items():
            lines.append(f"### `{key}`")
            lines.append("")
            for s in sessions:
                sid = s.get("name", "").replace("sessions/", "")
                state = s.get("state", "UNKNOWN")
                lines.append(f"- `{sid}` — {state}")
            lines.append("")

    return "\n".join(lines)


def render_session_section(session: Optional[Dict[str, Any]]) -> str:
    """Render the session metadata section."""
    if not session:
        return ""
    sid = session.get("name", "").replace("sessions/", "")
    lines = [
        "## Session",
        "",
        f"- **ID:** `{sid}`",
        f"- **State:** {session.get('state', 'N/A')}",
        f"- **Title:** {session.get('title', 'N/A')}",
        f"- **Repository:** {session.get('repository', 'N/A')}",
        f"- **Branch:** {session.get('headBranch', 'N/A')}",
        "",
    ]
    pr = session.get("pullRequest") or {}
    if pr.get("url"):
        lines.append(f"- **PR:** {pr['url']}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate a data-driven forensics report")
    parser.add_argument("--repo", required=True, help="Target repository name")
    parser.add_argument("--type", required=True, choices=REPORT_TYPES,
                        help="Report type")
    parser.add_argument("--session-id", help="Jules session ID (required for failure_analysis)")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--title", help="Report title (default: derived from type)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print report to stdout instead of writing a file")
    args = parser.parse_args()

    if args.type == "failure_analysis" and not args.session_id:
        parser.error("--session-id is required for failure_analysis reports")

    client = JulesAPIClient()
    data = fetch_session_data(client, args.session_id, args.repo)

    title = args.title or f"{args.type.replace('_', ' ').title()} Report"
    fm = generate_frontmatter(args.session_id or "N/A", title, args.repo, args.type)

    # Build report body
    body = [f"# {title}", ""]
    body.append(f"**Generated:** {utc_now()}")
    body.append(f"**Repository:** {args.repo}")
    body.append(f"**Type:** {args.type}")
    body.append(f"**Session:** {args.session_id or 'N/A'}")
    body.append("")

    if args.session_id:
        body.append(render_session_section(data["session"]))

    if args.type == "failure_analysis" and args.session_id:
        analysis = analyze_session_failure(args.session_id, client=client)
        body.append(render_failure_analysis(args.session_id, analysis, args.repo))

    elif args.type == "pattern_analysis":
        analysis = analyze_session_reuse(args.repo, sessions=data["sessions"])
        body.append(render_pattern_analysis(analysis))

    else:
        body.append("## Summary")
        body.append("")
        body.append("[TODO: manual analysis required for this report type]")
        body.append("")

    report = frontmatter_to_yaml(fm) + "\n\n" + "\n".join(body)

    if args.dry_run:
        print(report)
        return

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{args.type}_{date_str}.md"
    os.makedirs(args.output, exist_ok=True)
    output_path = os.path.join(args.output, filename)

    with open(output_path, "w") as f:
        f.write(report)

    print(f"Generated: {output_path}")

    index_path = os.path.join(args.output, "INDEX.yaml")
    if os.path.exists(index_path):
        print(f"NOTE: Update {index_path} to include the new report")


if __name__ == "__main__":
    main()
