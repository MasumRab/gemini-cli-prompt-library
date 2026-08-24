#!/usr/bin/env python3
"""
Script to add new forensics data to the standardized format.
Accepts a JSON file as input, validates it against the schema, and merges it
with the existing migrated_forensics_data.json file.
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any
from jsonschema import validate, ValidationError


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and return JSON data from a file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def save_json_file(data: Dict[str, Any], filepath: str) -> None:
    """Save JSON data to a file with proper formatting."""
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving file {filepath}: {e}")
        sys.exit(1)


def validate_against_schema(data: Dict[str, Any], schema_path: str) -> bool:
    """Validate data against the JSON schema.
    For input data, we allow missing top-level sections (sessions, pull_requests, interventions)
    but validate whatever is present.
    """
    try:
        with open(schema_path, "r") as f:
            full_schema = json.load(f)

        # Create a copy of the schema and make all top-level properties optional
        # This allows input files to contain only some sections
        input_schema = full_schema.copy()
        input_schema["required"] = []  # No top-level properties are required

        validate(instance=data, schema=input_schema)
        return True
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file: {e}")
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: Validation failed: {e.message}")
        return False
    except Exception as e:
        print(f"Error: Unexpected error during validation: {e}")
        sys.exit(1)


def merge_data(
    existing_data: Dict[str, Any], new_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge new data into existing data structure.
    Appends arrays and updates metadata counters.
    """
    # Create a deep copy of existing data to avoid modifying original
    merged = json.loads(json.dumps(existing_data))

    # Merge sessions if present in new data
    if "sessions" in new_data and isinstance(new_data["sessions"], list):
        merged["sessions"].extend(new_data["sessions"])

    # Merge pull_requests if present in new data
    if "pull_requests" in new_data and isinstance(new_data["pull_requests"], list):
        merged["pull_requests"].extend(new_data["pull_requests"])

    # Merge interventions if present in new data
    if "interventions" in new_data and isinstance(new_data["interventions"], list):
        merged["interventions"].extend(new_data["interventions"])

    # Update metadata counters
    if "metadata" in merged:
        merged["metadata"]["total_sessions"] = len(merged["sessions"])
        merged["metadata"]["total_prs"] = len(merged["pull_requests"])
        merged["metadata"]["total_interventions"] = len(merged["interventions"])
        merged["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()

        # If analysis_thread is not set in existing data, try to get it from new data
        if not merged["metadata"].get("analysis_thread") and "metadata" in new_data:
            merged["metadata"]["analysis_thread"] = new_data["metadata"].get(
                "analysis_thread", ""
            )

    return merged


def main():
    parser = argparse.ArgumentParser(
        description="Add new forensics data to the standardized format."
    )
    parser.add_argument(
        "input_file", help="JSON file containing new forensics data to add"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without saving",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Just validate the input without modifying anything",
    )

    args = parser.parse_args()

    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Paths to required files
    schema_path = os.path.join(script_dir, "forensics_data_schema.json")
    existing_data_path = os.path.join(script_dir, "migrated_forensics_data.json")

    # Load the input data
    print(f"Loading input data from {args.input_file}...")
    new_data = load_json_file(args.input_file)

    # Validate the input data against the schema
    print("Validating input data against schema...")
    if not validate_against_schema(new_data, schema_path):
        print("Input data validation failed. Exiting.")
        sys.exit(1)

    print("✓ Input data is valid!")

    # If validate-only, exit here
    if args.validate_only:
        print("Validation only mode - exiting without changes.")
        sys.exit(0)

    # Load existing data
    print(f"Loading existing data from {existing_data_path}...")
    existing_data = load_json_file(existing_data_path)

    # Merge the data
    print("Merging data...")
    merged_data = merge_data(existing_data, new_data)

    # Show what would be changed in dry-run mode
    if args.dry_run:
        print("\nDRY RUN MODE - No changes will be saved")
        print(f"Existing sessions: {len(existing_data.get('sessions', []))}")
        print(f"New sessions to add: {len(new_data.get('sessions', []))}")
        print(f"Total sessions after merge: {len(merged_data.get('sessions', []))}")

        print(f"Existing pull_requests: {len(existing_data.get('pull_requests', []))}")
        print(f"New pull_requests to add: {len(new_data.get('pull_requests', []))}")
        print(
            f"Total pull_requests after merge: {len(merged_data.get('pull_requests', []))}"
        )

        print(f"Existing interventions: {len(existing_data.get('interventions', []))}")
        print(f"New interventions to add: {len(new_data.get('interventions', []))}")
        print(
            f"Total interventions after merge: {len(merged_data.get('interventions', []))}"
        )

        print(f"\nMetadata would be updated:")
        print(f"  last_updated: {merged_data['metadata']['last_updated']}")
        print(f"  total_sessions: {merged_data['metadata']['total_sessions']}")
        print(f"  total_prs: {merged_data['metadata']['total_prs']}")
        print(
            f"  total_interventions: {merged_data['metadata']['total_interventions']}"
        )

        # Validate merged data against schema
        print("\nValidating merged data against schema...")
        if validate_against_schema(merged_data, schema_path):
            print("✓ Merged data is valid!")
        else:
            print("✗ Merged data validation failed!")
            sys.exit(1)

        print("\nDry run complete - no files were modified.")
        sys.exit(0)

    # Validate merged data against schema before saving
    print("Validating merged data against schema...")
    if not validate_against_schema(merged_data, schema_path):
        print("Merged data validation failed. Exiting without saving.")
        sys.exit(1)

    # Save the merged data
    print(f"Saving merged data to {existing_data_path}...")
    save_json_file(merged_data, existing_data_path)

    print("✓ Data successfully added and saved!")
    print(f"  Total sessions: {merged_data['metadata']['total_sessions']}")
    print(f"  Total pull requests: {merged_data['metadata']['total_prs']}")
    print(f"  Total interventions: {merged_data['metadata']['total_interventions']}")


if __name__ == "__main__":
    main()
