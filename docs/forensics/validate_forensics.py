#!/usr/bin/env python3
"""
Validation script for Jules forensics JSON files.
Validates all JSON files in the docs/forensics/ directory against the schema.
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

    # Find all JSON files in the directory (excluding the schema and this script)
    json_files = []
    excluded_files = {"forensics_data_schema.json", "validate_forensics.py"}

    for filename in os.listdir(script_dir):
        if (
            filename.endswith(".json")
            and filename not in excluded_files
            and os.path.isfile(os.path.join(script_dir, filename))
        ):
            json_files.append(filename)

    # If no JSON files to validate, exit successfully
    if not json_files:
        print("No JSON files to validate (excluding schema and script).")
        sys.exit(0)

    # Validate each JSON file
    validation_errors = []

    for filename in json_files:
        file_path = os.path.join(script_dir, filename)
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            validate(instance=data, schema=schema)
            print(f"✓ {filename} is valid")

        except FileNotFoundError:
            validation_errors.append(f"Error: File not found: {filename}")
        except json.JSONDecodeError as e:
            validation_errors.append(f"Error: Invalid JSON in {filename}: {e}")
        except ValidationError as e:
            validation_errors.append(
                f"Error: Validation failed for {filename}: {e.message}"
            )
        except Exception as e:
            validation_errors.append(
                f"Error: Unexpected error validating {filename}: {e}"
            )

    # Print any validation errors
    if validation_errors:
        print("\nValidation errors:")
        for error in validation_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"\nAll {len(json_files)} JSON files are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
