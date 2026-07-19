"""Validate that all files use official Jules API state names.

Scans all .py, .sh, and .md files in the repo for state references
and flags any invalid state names.
"""
import re
from pathlib import Path

import pytest

OFFICIAL_STATES = {
    "QUEUED",
    "PLANNING",
    "AWAITING_PLAN_APPROVAL",
    "AWAITING_USER_FEEDBACK",
    "IN_PROGRESS",
    "PAUSED",
    "COMPLETED",
    "FAILED",
    "STATE_UNSPECIFIED",
}

INVALID_STATES = {
    "RUNNING": "IN_PROGRESS",
    "PENDING": "QUEUED",
    "WAITING_FOR_USER": "AWAITING_USER_FEEDBACK",
    "RUNNING_STUCK": "IN_PROGRESS",
}

REPO_ROOT = Path(__file__).parent.parent.parent
SCAN_EXTENSIONS = {".py", ".sh", ".md"}


def find_files_to_scan():
    """Find all files to scan, excluding .git, __pycache__, node_modules."""
    skip_dirs = {".git", "__pycache__", "node_modules", ".omp", ".letta", "dist", ".venv"}
    skip_prefixes = {"tools/tests", "skills", "CHECKLIST.md"}
    files = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in filenames:
            fp = Path(root) / f
            rel = fp.relative_to(REPO_ROOT).as_posix()
            if any(rel.startswith(p) for p in skip_prefixes):
                continue
            if fp.suffix in SCAN_EXTENSIONS:
                files.append(fp)
    return files


import os


def test_no_invalid_state_names():
    """No file should contain invalid state names."""
    files = find_files_to_scan()
    violations = []

    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for invalid_state, correct_state in INVALID_STATES.items():
            # Match whole word, case-sensitive
            pattern = r"\b" + re.escape(invalid_state) + r"\b"
            matches = list(re.finditer(pattern, content))
            if matches:
                for match in matches:
                    line_num = content[:match.start()].count("\n") + 1
                    violations.append(
                        f"{filepath.relative_to(REPO_ROOT)}:{line_num} "
                        f"found '{invalid_state}' (should be '{correct_state}')"
                    )

    assert not violations, (
        f"Found {len(violations)} invalid state name(s):\n"
        + "\n".join(violations[:20])
    )


def test_official_states_present():
    """At least some official state names should appear in the codebase."""
    files = find_files_to_scan()
    all_content = ""
    for f in files:
        try:
            all_content += f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

    found_states = set()
    for state in OFFICIAL_STATES:
        if re.search(r"\b" + re.escape(state) + r"\b", all_content):
            found_states.add(state)

    # At least 5 of the 9 official states should be referenced
    assert len(found_states) >= 5, (
        f"Only found {len(found_states)} official states: {found_states}. "
        f"Expected at least 5."
    )
