import os
import tomllib
import re
import sys

def get_toml_files(root_dir):
    toml_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".toml"):
                toml_files.append(os.path.join(root, file))
    return toml_files

def parse_registry(filepath):
    commands = set()
    with open(filepath, 'r') as f:
        content = f.read()

    # Simple regex to find list items like "- **command-name**:"
    matches = re.findall(r'- \*\*(.*?)\*\*:', content)
    for match in matches:
        commands.add(match)
    return commands

def verify_prompts():
    commands_dir = "commands"
    registry_file = "GEMINI.md" # QWEN.md is identical

    if not os.path.exists(commands_dir):
        print(f"Error: {commands_dir} directory not found.")
        sys.exit(1)

    if not os.path.exists(registry_file):
        print(f"Error: {registry_file} not found.")
        sys.exit(1)

    toml_files = get_toml_files(commands_dir)
    registry_commands = parse_registry(registry_file)

    errors = []

    print(f"Found {len(toml_files)} TOML files.")
    print(f"Found {len(registry_commands)} commands in registry.")

    # Check TOML files
    for file_path in toml_files:
        try:
            with open(file_path, 'rb') as f:
                content = tomllib.load(f)

            if 'prompt' not in content:
                errors.append(f"Missing 'prompt' key in {file_path}")

            # Logic to verify mapping
            # This is heuristics based on observation
            # convention seems to be:
            # 1. category-filename (e.g., code-review-security)
            # 2. filename only (e.g., coverage-analysis)

            rel_path = os.path.relpath(file_path, commands_dir)
            parts = rel_path.split(os.sep)
            if len(parts) >= 2:
                category = parts[0]
                name = os.path.splitext(parts[1])[0]

                command_name_prefixed = f"{category}-{name}"
                command_name_simple = name

                if command_name_prefixed in registry_commands:
                    pass # OK
                elif command_name_simple in registry_commands:
                    pass # OK
                else:
                    errors.append(f"File {file_path} (checked: {command_name_prefixed}, {command_name_simple}) not found in {registry_file}")

        except tomllib.TOMLDecodeError as e:
            errors.append(f"Invalid TOML in {file_path}: {e}")
        except Exception as e:
            errors.append(f"Error processing {file_path}: {e}")

    if errors:
        print("\nVerification Failed with errors:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    else:
        print("\nVerification Passed! All prompts are valid and listed in registry.")

if __name__ == "__main__":
    verify_prompts()
