#!/usr/bin/env python3
"""
Archive old session tracking files.

This script scans the session_tracking directory for JSON session files,
identifies files older than a specified threshold (default 90 days), and
moves them to an archive directory organized by year/month.
"""

import os
import json
import shutil
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys


def get_file_timestamp(filepath):
    """
    Extract timestamp from a JSON session file.
    Tries to find 'last_update', 'updateTime', or 'createTime' fields.
    Returns a timezone-aware datetime object in UTC or None if not found.
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        # Try different timestamp fields
        timestamp_fields = ["last_update", "updateTime", "createTime"]
        for field in timestamp_fields:
            if field in data and data[field]:
                # Assuming timestamp is in ISO format string or Unix timestamp
                ts = data[field]
                if isinstance(ts, (int, float)):
                    # Unix timestamp
                    return datetime.fromtimestamp(ts, tz=timezone.utc)
                elif isinstance(ts, str):
                    # Try to parse ISO format
                    try:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        # If naive, assume UTC
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return dt
                    except ValueError:
                        # Try other common formats (assume UTC if no timezone)
                        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
                            try:
                                dt = datetime.strptime(ts, fmt)
                                # Assume UTC for naive times
                                dt = dt.replace(tzinfo=timezone.utc)
                                return dt
                            except ValueError:
                                pass
        return None
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Archive old session tracking files.")
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Threshold in days for archiving (default: 90)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be archived without making changes",
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Restore files from archive (requires --archive-date)",
    )
    parser.add_argument(
        "--archive-date",
        type=str,
        help="Specify archive date for restore (YYYY/MM format)",
    )
    args = parser.parse_args()

    # Base directory
    base_dir = Path("/home/masum/github/remote/jules/session_tracking")
    if not base_dir.exists():
        print(f"Error: Base directory {base_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.restore:
        if not args.archive_date:
            print("Error: --restore requires --archive-date (YYYY/MM)", file=sys.stderr)
            sys.exit(1)
        # Implement restore logic (bonus)
        print("Restore functionality is not implemented in this version.")
        # For now, just show what would be done
        archive_dir = base_dir / "archive" / args.archive_date
        if archive_dir.exists():
            print(f"Would restore files from {archive_dir} to {base_dir}")
        else:
            print(f"Archive directory {archive_dir} does not exist.")
        return

    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=args.days)

    # Find all JSON files in session_tracking (including subdirectories)
    json_files = list(base_dir.rglob("*.json"))
    # Exclude the archive directory itself to avoid processing archived files
    json_files = [f for f in json_files if "archive" not in f.parts]

    files_to_archive = []
    for filepath in json_files:
        timestamp = get_file_timestamp(filepath)
        if timestamp is None:
            # If we can't determine timestamp, skip or use file mtime?
            # According to requirements, we should check the timestamp in the JSON.
            # If not available, we might skip or use file system time? Let's skip for safety.
            print(
                f"Warning: Could not determine timestamp for {filepath}, skipping.",
                file=sys.stderr,
            )
            continue
        if timestamp < cutoff_date:
            files_to_archive.append((filepath, timestamp))

    if not files_to_archive:
        print("No files to archive.")
        return

    if args.dry_run:
        print(
            f"Dry run: Would archive {len(files_to_archive)} files older than {args.days} days:"
        )
        for filepath, timestamp in files_to_archive:
            print(f"  {filepath} (last updated: {timestamp})")
        return

    # Archive the files
    archived_count = 0
    for filepath, timestamp in files_to_archive:
        # Determine archive path: session_tracking/archive/YYYY/MM/
        archive_dir = (
            base_dir / "archive" / str(timestamp.year) / f"{timestamp.month:02d}"
        )
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Create README in archive directory if it doesn't exist
        readme_path = archive_dir / "README.md"
        if not readme_path.exists():
            readme_content = f"""# Archived Session Tracking Files

This directory contains session tracking files archived on {datetime.now().strftime("%Y-%m-%d")}.

## Archival Policy
- Files are archived when older than {args.days} days (based on last_update, updateTime, or createTime timestamps).
- Archive structure: archive/YYYY/MM/
- Archived files retain their original names and JSON structure.

## Accessing Archived Data
Archived session files can be accessed directly in this directory.
The SUMMARY.json file (if present) provides an index of archived sessions.
"""
            readme_path.write_text(readme_content)

        # Move the file
        dest_path = archive_dir / filepath.name
        try:
            shutil.move(str(filepath), str(dest_path))
            print(f"Archived: {filepath} -> {dest_path}")
            archived_count += 1
        except Exception as e:
            print(f"Error archiving {filepath}: {e}", file=sys.stderr)

    print(f"Archived {archived_count} files.")

    # Update SUMMARY.json (if exists) - remove entries for archived files
    summary_path = base_dir / "SUMMARY.json"
    if summary_path.exists():
        try:
            with open(summary_path, "r") as f:
                summary_data = json.load(f)

            # Assuming summary_data is a list of session entries or a dict with sessions
            # We'll remove entries where the file is now archived.
            # This is implementation-specific; we'll do a simple approach:
            # If summary_data is a list of objects with a 'file' field matching the basename.
            if isinstance(summary_data, list):
                original_count = len(summary_data)
                summary_data = [
                    entry
                    for entry in summary_data
                    if not (
                        isinstance(entry, dict)
                        and entry.get("file") in [f.name for f, _ in files_to_archive]
                    )
                ]
                removed_count = original_count - len(summary_data)
                if removed_count > 0:
                    with open(summary_path, "w") as f:
                        json.dump(summary_data, f, indent=2)
                    print(
                        f"Updated SUMMARY.json: removed {removed_count} entries for archived files."
                    )
            # If it's a dict, we might need to adjust; but we'll leave as is for now.
        except Exception as e:
            print(f"Error updating SUMMARY.json: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
