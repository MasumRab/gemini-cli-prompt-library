#!/usr/bin/env python3
"""
Validation script for Jules forensics JSON files.
Recursively finds every JSON file under docs/forensics/ (including scratch/),
excluding the schema itself, and validates the forensics data files against
forensics_data_schema.json. Files that do not carry the forensics top-level
keys (metadata, sessions, pull_requests, interventions) are reported as
skipped instead of failing validation.
"""

import json
import os
import sys
from jsonschema import validate, ValidationError


def main():
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the schema file
    schema_path = os.path.join(script_dir, "forensics_data_schema.json")

    # Load the schema
    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file: {e}")
        sys.exit(1)

    # Recursively find all JSON files (excluding the schema and this script)
    json_files = []
    excluded_files = {"forensics_data_schema.json", "validate_forensics.py"}

    for dirpath, _dirnames, filenames in os.walk(script_dir):
        for filename in sorted(filenames):
            if not filename.endswith(".json") or filename in excluded_files:
                continue
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                json_files.append(os.path.relpath(file_path, script_dir))

    json_files.sort()

    # If no JSON files to validate, exit successfully
    if not json_files:
        print("No JSON files to validate (excluding schema and script).")
        sys.exit(0)

    # Validate each JSON file that carries the forensics top-level keys
    required_keys = {"metadata", "sessions", "pull_requests", "interventions"}
    validation_errors = []
    validated_count = 0
    skipped_count = 0

    for relpath in json_files:
        file_path = os.path.join(script_dir, relpath)
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            if not isinstance(data, dict) or not required_keys.issubset(data.keys()):
                print(f"SKIP {relpath} (not a forensics data file)")
                skipped_count += 1
                continue

            validate(instance=data, schema=schema)
            validated_count += 1
            print(f"✓ {relpath} is valid")

        except FileNotFoundError:
            validation_errors.append(f"Error: File not found: {relpath}")
        except json.JSONDecodeError as e:
            validation_errors.append(f"Error: Invalid JSON in {relpath}: {e}")
        except ValidationError as e:
            validation_errors.append(
                f"Error: Validation failed for {relpath}: {e.message}"
            )
        except Exception as e:
            validation_errors.append(
                f"Error: Unexpected error validating {relpath}: {e}"
            )

    # Print any validation errors
    if validation_errors:
        print("\nValidation errors:")
        for error in validation_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(
            f"\nAll {validated_count} forensics JSON files are valid! "
            f"({skipped_count} skipped, {len(json_files)} discovered)"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
