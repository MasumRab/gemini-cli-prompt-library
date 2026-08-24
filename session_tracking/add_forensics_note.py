#!/usr/bin/env python3
"""
Add forensics_analysis_note field to session tracking JSON files.

This script walks through the session_tracking directory and adds a
forensics_analysis_note field to each JSON file (excluding SUMMARY.json).
"""

import json
import os
import sys
from pathlib import Path


def add_forensics_note(file_path, dry_run=False):
    """Add forensics_analysis_note to a single JSON file."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error: Could not parse JSON in {file_path}: {e}", file=sys.stderr)
        return False
    except OSError as e:
        print(f"Error: Could not read file {file_path}: {e}", file=sys.stderr)
        return False

    # Check if the field already exists
    if "forensics_analysis_note" in data:
        return False  # No change needed

    # Add the field
    data["forensics_analysis_note"] = (
        "For aggregated forensics analysis of sessions, see the migrated_forensics_data.json file in the docs/forensics/ directory."
    )

    if dry_run:
        print(f"[DRY RUN] Would add forensics_analysis_note to {file_path}")
        return True

    # Write back the updated JSON
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated: {file_path}")
        return True
    except OSError as e:
        print(f"Error: Could not write to file {file_path}: {e}", file=sys.stderr)
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Add forensics_analysis_note to session tracking JSON files."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    args = parser.parse_args()

    # Base directory
    base_dir = Path("/home/masum/github/remote/jules/session_tracking")
    if not base_dir.is_dir():
        print(f"Error: Directory {base_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    # Walk through the directory
    updated_count = 0
    error_count = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json") and file != "SUMMARY.json":
                file_path = Path(root) / file
                if add_forensics_note(file_path, dry_run=args.dry_run):
                    updated_count += 1

    # Summary
    if args.dry_run:
        print(f"\n[DRY RUN] Would update {updated_count} file(s).")
    else:
        print(f"\nUpdated {updated_count} file(s).")
        if error_count > 0:
            print(f"Encountered {error_count} error(s).", file=sys.stderr)


if __name__ == "__main__":
    main()
