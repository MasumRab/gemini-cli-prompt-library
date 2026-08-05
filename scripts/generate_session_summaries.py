#!/usr/bin/env python3
"""
Generate Session Summaries

Reads Jules activity/session JSON files and generates compact YAML summary
files according to the Session Summary Standard.

Usage:
    # Summarize a single file
    python generate_session_summaries.py activities_pr_8645133856938915124.json

    # Summarize all activity files in a directory
    python generate_session_summaries.py /path/to/activities/dir/

    # Summarize all files, force overwrite existing summaries
    python generate_session_summaries.py --force /path/to/dir/

    # Validate existing summaries without regenerating
    python generate_session_summaries.py --validate /path/to/dir/

    # Dry run — show what would be done without writing
    python generate_session_summaries.py --dry-run /path/to/dir/
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Constants ────────────────────────────────────────────────────────────────

SUMMARY_FIELDS = {
    "file_max_bytes": 50 * 1024,  # 50 KB max summary file size
    "message_max_chars": 200,
    "purpose_max_chars": 500,
    "summary_max_chars": 2000,
    "change_summary_max_chars": 200,
}

FULL_FILE_PATTERNS: List[str] = [
    r"^activities_.*\.json$",
    r"^current_sessions\.json$",
    r"^jules_sessions\.json$",
]

STATUS_MAP = {
    "SESSION_STATUS_COMPLETED": "completed",
    "SESSION_STATUS_FAILED": "failed",
    "SESSION_STATUS_IN_PROGRESS": "in_progress",
    "SESSION_STATUS_AWAITING_PLAN_APPROVAL": "awaiting_approval",
    "SESSION_STATUS_AWAITING_USER_FEEDBACK": "awaiting_feedback",
    "SESSION_STATUS_PAUSED": "paused",
}

VALID_STATUSES = set(STATUS_MAP.values()) | {"unknown"}

CHANGE_TYPE_KEYWORDS = {
    "new file": "added",
    "deleted file": "deleted",
    "rename from": "renamed",
}

# ── Helpers ──────────────────────────────────────────────────────────────────


def truncate(text: str, max_chars: int) -> str:
    """Truncate text to max_chars, appending '...' if truncated."""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def strip_non_text(obj: Any) -> Any:
    """Recursively strip extremely long strings from a structure to avoid memory issues."""
    if isinstance(obj, str):
        return truncate(obj, 10000)
    elif isinstance(obj, dict):
        return {k: strip_non_text(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [strip_non_text(item) for item in obj]
    return obj


def parse_timestamp(ts: Optional[str]) -> str:
    """Parse RFC 3339 timestamp or return empty string."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.isoformat()
    except (ValueError, AttributeError):
        return ts


def detect_source(session: Dict[str, Any]) -> str:
    """Detect the session source from available fields."""
    name = (session.get("name") or "").lower()
    if "pr" in name:
        return "pr"
    prompt = (session.get("prompt") or "").lower()
    if "issue" in prompt or "bug" in prompt:
        return "issue"
    return "manual"


def is_activity_file(path: Path) -> bool:
    """Check if a file matches activity/session patterns."""
    return any(re.match(p, path.name) for p in FULL_FILE_PATTERNS)


def summary_path_for(full_path: Path) -> Path:
    """Derive the summary file path from a full file path."""
    stem = full_path.stem  # e.g., "activities_123"
    return full_path.with_name(f"{stem}_summary.yaml")


# ── Extractors ───────────────────────────────────────────────────────────────


def extract_from_activities(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract session summaries from an activities JSON file.
    
    Structure: { "activities": [...] }
    Each activity can be agentMessaged, userMessaged, planGenerated,
    planApproved, sessionCompleted, sessionFailed, or progressUpdated.
    """
    activities = data.get("activities", [])
    if not activities:
        return []

    # Derive session ID from the first activity's name field
    # Pattern: sessions/<id>/activities/<activity_id>
    session_id = ""
    repository = ""
    
    # Collect data across all activities
    purpose = ""
    summary_parts: List[str] = []
    participants: List[Dict[str, str]] = []
    changes: List[Dict[str, Any]] = []
    plan_steps: List[str] = []
    errors: List[Dict[str, str]] = []
    status = "unknown"
    timestamps: List[str] = []
    title = ""
    
    agent_messages: List[str] = []

    for activity in activities:
        activity_name = activity.get("name", "") or ""
        if not session_id:
            # Try to extract session ID from activity name
            m = re.search(r"sessions/([^/]+)", activity_name)
            if m:
                session_id = m.group(1)
        
        # Extract repository from source contexts if present
        # (may not be available in activity files)
        
        create_time = activity.get("createTime", "")
        if create_time:
            timestamps.append(create_time)
        
        originator = activity.get("originator", "")
        
        # Check activity type by trying each content key
        if "agentMessaged" in activity:
            msg = activity["agentMessaged"].get("agentMessage", "")
            participants.append({
                "role": "agent",
                "message": truncate(msg, SUMMARY_FIELDS["message_max_chars"]),
            })
            agent_messages.append(msg)
            
        elif "userMessaged" in activity:
            msg = activity["userMessaged"].get("userMessage", "")
            participants.append({
                "role": "user",
                "message": truncate(msg, SUMMARY_FIELDS["message_max_chars"]),
            })
            # First user message often states the purpose
            if not purpose:
                purpose = truncate(msg, SUMMARY_FIELDS["purpose_max_chars"])
            
        elif "sessionCompleted" in activity:
            status = "completed"
            summary_parts.append("Session completed successfully.")
            
        elif "sessionFailed" in activity:
            status = "failed"
            reason = activity["sessionFailed"].get("reason", "Unknown reason")
            errors.append({"type": "session_failure", "message": truncate(reason, 200)})
            summary_parts.append(f"Session failed: {truncate(reason, 200)}")
            
        elif "planGenerated" in activity:
            plan_data = activity["planGenerated"].get("plan", {})
            steps_raw = plan_data.get("steps", [])
            for step_dict in steps_raw:
                step_text = ""
                if isinstance(step_dict, dict):
                    step_text = step_dict.get("description", step_dict.get("text", ""))
                elif isinstance(step_dict, str):
                    step_text = step_dict
                if step_text:
                    plan_steps.append(step_text)
            
        elif "planApproved" in activity:
            summary_parts.append("Plan was approved.")
            
        elif "progressUpdated" in activity:
            artifacts = activity.get("progressUpdated", {}).get("artifacts", [])
            for artifact in artifacts:
                change_set = artifact.get("changeSet", {})
                git_patch = change_set.get("gitPatch", {})
                if git_patch:
                    unidiff = git_patch.get("unidiffPatch", "")
                    commit_msg = git_patch.get("suggestedCommitMessage", "")
                    
                    # Parse the diff header to determine which files changed
                    diff_lines = unidiff.split("\n")
                    for line in diff_lines:
                        m = re.match(r"^(?:diff --git a/)(\S+)", line)
                        if m:
                            file_path = m.group(1)
                            change_type = "modified"
                            
                            # Check subsequent lines for change type keywords
                            for dl in diff_lines[diff_lines.index(line):]:
                                for kw, ct in CHANGE_TYPE_KEYWORDS.items():
                                    if dl.startswith(kw):
                                        change_type = ct
                                        break
                            
                            # Extract a summary from the commit message or build one
                            summary = commit_msg if commit_msg else ""
                            summary = truncate(summary, SUMMARY_FIELDS["change_summary_max_chars"])
                            
                            # Only add if not a duplicate
                            if not any(c.get("file") == file_path for c in changes):
                                changes.append({
                                    "file": file_path,
                                    "summary": summary,
                                    "change_type": change_type,
                                    "suggested_commit": commit_msg or "",
                                    "base_commit": git_patch.get("baseCommitId", ""),
                                })

    # Derive title from agent messages or purpose
    if not title:
        if purpose:
            title = truncate(purpose.replace("\n", " "), 100)
        elif agent_messages:
            title = truncate(agent_messages[0].replace("\n", " "), 100)
        else:
            title = f"Session {session_id}" if session_id else "Unknown session"
    
    # Build narrative summary
    summary_text = " ".join(summary_parts) if summary_parts else ""
    if agent_messages and not summary_text:
        summary_text = truncate(agent_messages[-1], SUMMARY_FIELDS["summary_max_chars"])
    
    # Determine created/updated timestamps
    created = timestamps[0] if timestamps else ""
    updated = timestamps[-1] if timestamps else ""
    
    result = {
        "session": {
            "id": session_id,
            "title": truncate(title, 200),
            "repository": repository or "",
            "created": parse_timestamp(created),
            "updated": parse_timestamp(updated),
            "status": status,
            "source": "",
        },
        "purpose": purpose,
        "summary": truncate(summary_text, SUMMARY_FIELDS["summary_max_chars"]),
        "participants": participants,
        "changes": changes,
        "plan": {"steps": plan_steps} if plan_steps else {},
        "errors": errors,
    }
    
    return [result]


def extract_from_sessions(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract session summaries from a sessions JSON file.
    
    Structure: { "sessions": [...] }
    Each session has: name, title, state, createTime, updateTime,
    sourceContext, prompt, url, outputs, etc.
    """
    sessions = data.get("sessions", [])
    if not sessions:
        return []
    
    results = []
    
    for session in sessions:
        session_id = ""
        name = session.get("name", "") or ""
        m = re.search(r"sessions/([^/]+)", name)
        if m:
            session_id = m.group(1)
        
        raw_status = session.get("state", "")
        status = STATUS_MAP.get(raw_status, "unknown")
        
        purpose = truncate(
            session.get("prompt", "") or "",
            SUMMARY_FIELDS["purpose_max_chars"],
        )
        
        title = truncate(
            session.get("title", "") or purpose or f"Session {session_id}",
            200,
        )
        
        # Detect source
        source = detect_source(session)
        
        # Extract PR info from outputs
        pr_info: Dict[str, Any] = {}
        outputs = session.get("outputs", [])
        changes = []
        
        for output in outputs:
            pr_data = output.get("pullRequest", {})
            if pr_data:
                pr_info = {
                    "url": pr_data.get("url", ""),
                    "title": pr_data.get("title", ""),
                    "number": pr_data.get("number", 0),
                }
            
            change_set = output.get("changeSet", {})
            git_patch = change_set.get("gitPatch", {})
            if git_patch:
                unidiff = git_patch.get("unidiffPatch", "")
                commit_msg = git_patch.get("suggestedCommitMessage", "")
                diff_lines = unidiff.split("\n")
                for line in diff_lines:
                    fm = re.match(r"^(?:diff --git a/)(\S+)", line)
                    if fm:
                        file_path = fm.group(1)
                        change_type = "modified"
                        for dl in diff_lines[diff_lines.index(line):]:
                            for kw, ct in CHANGE_TYPE_KEYWORDS.items():
                                if dl.startswith(kw):
                                    change_type = ct
                                    break
                        if not any(c.get("file") == file_path for c in changes):
                            changes.append({
                                "file": file_path,
                                "summary": truncate(commit_msg, SUMMARY_FIELDS["change_summary_max_chars"]),
                                "change_type": change_type,
                                "suggested_commit": commit_msg or "",
                                "base_commit": git_patch.get("baseCommitId", ""),
                            })
        
        result = {
            "session": {
                "id": session_id,
                "title": title,
                "repository": "",
                "created": parse_timestamp(session.get("createTime", "")),
                "updated": parse_timestamp(session.get("updateTime", "")),
                "status": status,
                "source": source,
            },
            "purpose": purpose,
            "summary": "",
            "participants": [],
            "changes": changes,
            "plan": {},
            "pr": pr_info if pr_info else {},
            "errors": [],
        }
        
        results.append(result)
    
    return results


# ── File Processing ──────────────────────────────────────────────────────────


def process_file(full_path: Path, force: bool = False, dry_run: bool = False) -> Optional[Path]:
    """
    Process a single activity/session file and generate its summary.
    Returns the summary file path if created, or None if skipped.
    """
    summary_path = summary_path_for(full_path)
    
    # Skip if summary already exists and not forcing
    if summary_path.exists() and not force:
        return None
    
    if dry_run:
        print(f"[DRY RUN] Would generate: {summary_path}")
        return summary_path
    
    # Read the JSON file
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"⚠️  Skipping {full_path.name}: {e}", file=sys.stderr)
        return None
    except MemoryError:
        print(f"⚠️  Skipping {full_path.name}: file too large to load", file=sys.stderr)
        return None
    
    # Determine the structure type and extract
    summaries: List[Dict[str, Any]] = []
    
    if "activities" in data:
        summaries = extract_from_activities(data)
    elif "sessions" in data:
        summaries = extract_from_sessions(data)
    else:
        print(f"⚠️  Skipping {full_path.name}: unknown structure (no 'activities' or 'sessions' key)", file=sys.stderr)
        return None
    
    if not summaries:
        print(f"⚠️  Skipping {full_path.name}: no summaries extracted", file=sys.stderr)
        return None
    
    # If the original file has multiple sessions/activities, create a single
    # summary document with multiple session entries
    if len(summaries) == 1:
        output_data = summaries[0]
    else:
        output_data = {"sessions": summaries}
    
    # Generate YAML manually to avoid dependency on PyYAML
    yaml_content = dict_to_yaml(output_data)
    
    # Write summary file
    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        size_kb = os.path.getsize(summary_path) / 1024
        print(f"✅ Generated: {summary_path.name} ({size_kb:.1f} KB)")
        return summary_path
    except OSError as e:
        print(f"❌ Failed to write {summary_path}: {e}", file=sys.stderr)
        return None


def dict_to_yaml(data: Any, indent: int = 0) -> str:
    """
    Convert a Python dict/list structure to YAML string.
    Uses a simple serializer (no PyYAML dependency needed).
    """
    lines: List[str] = []
    prefix = "  " * indent
    
    if data is None:
        return "null\n"
    
    if isinstance(data, bool):
        return f"{str(data).lower()}\n"
    
    if isinstance(data, (int, float)):
        return f"{data}\n"
    
    if isinstance(data, str):
        if "\n" in data:
            # Multi-line string
            return f"|\n"
        if len(data) > 80 or ":" in data or "#" in data:
            return f"\"{data.replace('\"', '\\\"')}\"\n"
        return f"{data}\n"
    
    if isinstance(data, list):
        if not data:
            return "[]\n"
        if all(isinstance(item, (str, int, float)) for item in data):
            # Simple list — use flow style
            items = []
            for item in data:
                items.append(str(item))
            return f"[{', '.join(items)}]\n"
        # Complex list — block style
        lines.append("\n")
        for item in data:
            lines.append(f"{prefix}- ")
            item_str = dict_to_yaml(item, indent + 1).lstrip()
            # If multi-line, indent continuation
            item_lines = item_str.rstrip("\n").split("\n")
            for i, il in enumerate(item_lines):
                if i == 0:
                    lines.append(il + "\n")
                else:
                    lines.append(f"{prefix}  {il}\n")
        return "".join(lines)
    
    if isinstance(data, dict):
        if not data:
            return "{}\n"
        for key, value in data.items():
            if value == "" or value == [] or value == {} or value is None:
                continue  # Skip empty values for cleaner output
            lines.append(f"{prefix}{key}: ")
            value_str = dict_to_yaml(value, indent + 1)
            lines.append(value_str)
        if not lines:
            return "{}\n"
        return "".join(lines)
    
    return f"{data}\n"


def validate_summaries(directory: Path) -> int:
    """
    Validate that all activity/session files have companion summaries.
    Returns count of missing summaries.
    """
    missing = 0
    for full_path in sorted(directory.iterdir()):
        if not full_path.is_file() or not is_activity_file(full_path):
            continue
        
        summary_path = summary_path_for(full_path)
        if not summary_path.exists():
            print(f"❌ Missing summary: {full_path.name}")
            missing += 1
        else:
            # Validate summary is parseable
            try:
                with open(summary_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if len(content) > SUMMARY_FIELDS["file_max_bytes"]:
                    print(f"⚠️  Summary too large: {summary_path.name} ({len(content)} bytes)")
            except OSError as e:
                print(f"❌ Cannot read summary: {summary_path.name} — {e}")
                missing += 1
    
    total = sum(1 for f in directory.iterdir() if f.is_file() and is_activity_file(f))
    print(f"\n📊 Summary: {total - missing}/{total} files have valid summaries")
    return missing


# ── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Generate YAML summary files for Jules session/activity JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target",
        help="Path to a single JSON file or a directory containing activity/session files",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing summary files",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without writing any files",
    )
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validate existing summaries without generating new ones",
    )
    
    args = parser.parse_args()
    target = Path(args.target)
    
    if not target.exists():
        print(f"❌ Path does not exist: {target}", file=sys.stderr)
        sys.exit(1)
    
    if args.validate:
        if not target.is_dir():
            print("❌ --validate requires a directory path", file=sys.stderr)
            sys.exit(1)
        missing = validate_summaries(target)
        sys.exit(1 if missing > 0 else 0)
    
    if target.is_dir():
        # Process all matching files in directory
        processed = 0
        skipped = 0
        for f in sorted(target.iterdir()):
            if f.is_file() and is_activity_file(f):
                result = process_file(f, force=args.force, dry_run=args.dry_run)
                if result:
                    processed += 1
                else:
                    skipped += 1
        print(f"\n📊 Done: {processed} summaries generated, {skipped} skipped")
    else:
        # Process single file
        if not is_activity_file(target):
            print(f"⚠️  File doesn't match activity/session pattern: {target.name}")
            cont = input("Process anyway? [y/N] ")
            if cont.lower() != "y":
                sys.exit(0)
        result = process_file(target, force=args.force, dry_run=args.dry_run)
        if result:
            print(f"\n✅ Summary generated: {result}")
        else:
            print("\n⚠️  No summary generated (already exists? Use --force to overwrite)")


if __name__ == "__main__":
    main()
