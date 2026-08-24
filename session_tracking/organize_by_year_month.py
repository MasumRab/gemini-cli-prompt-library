#!/usr/bin/env python3
"""
Organize session tracking files by year/month subdirectories based on timestamps.
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path


def extract_timestamp(data):
    """Extract timestamp from session data using known field names."""
    timestamp_fields = ["last_update", "updateTime", "createTime"]
    for field in timestamp_fields:
        if field in data and data[field]:
            return data[field]
    return None


def parse_timestamp(timestamp_str):
    """Parse timestamp string into datetime object."""
    # Try ISO format first
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        pass

    # Try common formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse timestamp: {timestamp_str}")


def organize_sessions(base_dir, dry_run=False):
    """Organize session files into year/month subdirectories."""
    base_path = Path(base_dir)
    summary_path = base_path / "SUMMARY.json"

    if not summary_path.exists():
        print(f"Error: SUMMARY.json not found in {base_dir}")
        return 1

    # Load SUMMARY.json
    try:
        with open(summary_path, "r") as f:
            summary_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in SUMMARY.json: {e}")
        return 1
    except Exception as e:
        print(f"Error reading SUMMARY.json: {e}")
        return 1

    # Assume summary_data is a dict with 'sessions' list
    if "sessions" not in summary_data:
        print("Error: SUMMARY.json missing 'sessions' key")
        return 1

    sessions = summary_data["sessions"]
    updated_count = 0
    errors = []

    for session in sessions:
        if "tracking_file" not in session:
            print(
                f"Warning: Session missing 'tracking_file' field: {session.get('session_id', 'unknown')}"
            )
            continue

        json_file_path = base_path / session["tracking_file"]
        if not json_file_path.exists():
            print(f"Warning: Session file not found: {json_file_path}")
            continue

        # Skip SUMMARY.json itself
        if json_file_path.name == "SUMMARY.json":
            continue

        # Read session data to extract timestamp
        try:
            with open(json_file_path, "r") as f:
                session_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {json_file_path}: {e}")
            errors.append((json_file_path, str(e)))
            continue
        except Exception as e:
            print(f"Warning: Could not read {json_file_path}: {e}")
            errors.append((json_file_path, str(e)))
            continue

        # Extract timestamp
        timestamp_str = extract_timestamp(session_data)
        if not timestamp_str:
            print(f"Warning: No timestamp found in {json_file_path}")
            errors.append((json_file_path, "No timestamp found"))
            continue

        # Parse timestamp
        try:
            dt = parse_timestamp(timestamp_str)
        except ValueError as e:
            print(f"Warning: Could not parse timestamp in {json_file_path}: {e}")
            errors.append((json_file_path, str(e)))
            continue

        # Determine year/month directory
        year = dt.year
        month = dt.month
        target_dir = base_path / f"{year}" / f"{month:02d}"

        # Target paths
        target_json_path = target_dir / json_file_path.name
        yaml_file_path = json_file_path.with_suffix("").with_name(
            json_file_path.stem + "_summary.yaml"
        )
        target_yaml_path = None
        if yaml_file_path.exists():
            target_yaml_path = target_dir / yaml_file_path.name

        # Show what would be done or do it
        if dry_run:
            print(f"[DRY RUN] Would move {json_file_path} -> {target_json_path}")
            if target_yaml_path:
                print(f"[DRY RUN] Would move {yaml_file_path} -> {target_yaml_path}")
            new_rel_path = str(target_json_path.relative_to(base_path))
            print(
                f"[DRY RUN] Would update SUMMARY.json: {session['tracking_file']} -> {new_rel_path}"
            )
        else:
            try:
                # Create target directory
                target_dir.mkdir(parents=True, exist_ok=True)

                # Move JSON file
                shutil.move(str(json_file_path), str(target_json_path))

                # Move YAML file if exists
                if target_yaml_path:
                    shutil.move(str(yaml_file_path), str(target_yaml_path))

                # Update session record
                new_rel_path = str(target_json_path.relative_to(base_path))
                session["tracking_file"] = new_rel_path
                updated_count += 1

                print(f"Moved {json_file_path.name} to {year}/{month:02d}/")

            except Exception as e:
                print(f"Error moving files for {json_file_path}: {e}")
                errors.append((json_file_path, str(e)))
                continue

    # Write updated SUMMARY.json if not dry run and we made changes
    if not dry_run and updated_count > 0:
        try:
            with open(summary_path, "w") as f:
                json.dump(summary_data, f, indent=2)
            print(f"Updated SUMMARY.json with {updated_count} session(s)")
        except Exception as e:
            print(f"Error writing SUMMARY.json: {e}")
            return 1
    elif dry_run:
        print(f"[DRY RUN] Would update SUMMARY.json with {updated_count} session(s)")

    # Report errors
    if errors:
        print(f"\nEncountered {len(errors)} error(s):")
        for file_path, error in errors:
            print(f"  {file_path}: {error}")

    return 0 if updated_count > 0 or not errors else 1


def main():
    parser = argparse.ArgumentParser(
        description="Organize session tracking files by year/month"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    args = parser.parse_args()

    base_dir = "/home/masum/github/remote/jules/session_tracking"
    if not os.path.isdir(base_dir):
        print(f"Error: Directory not found: {base_dir}")
        sys.exit(1)

    sys.exit(organize_sessions(base_dir, args.dry_run))


if __name__ == "__main__":
    main()
