import json
import os
import tomllib


def generate_manifest():
    """
    Generates a manifest of all commands in the commands/ directory and updates the improve.toml prompt.
    """
    print("Starting manifest generation...")
    manifest = {}
    commands_dir = "commands"
    if not os.path.isdir(commands_dir):
        print(f"Error: '{commands_dir}' directory not found.")
        return

    print(f"Scanning directory: {commands_dir}")
    for category in os.listdir(commands_dir):
        category_dir = os.path.join(commands_dir, category)
        if os.path.isdir(category_dir):
            print(f"  Scanning category: {category}")
            for filename in os.listdir(category_dir):
                if filename.endswith(".toml"):
                    command_name = f"/{category}:{filename[:-5]}"
                    filepath = os.path.join(category_dir, filename)
                    print(f"    Processing {filepath}")
                    with open(filepath, "rb") as f:
                        try:
                            data = tomllib.load(f)
                            prompt_lines = data.get("prompt", "").strip().split("\n")
                            description = "No description available."
                            for line in prompt_lines:
                                stripped_line = line.strip()
                                if stripped_line.startswith("#"):
                                    description = stripped_line[1:].strip()
                                    break
                            manifest[command_name] = description
                        except tomllib.TOMLDecodeError as e:
                            print(f"Error decoding {filepath}: {e}")

    if not manifest:
        print("Warning: No commands found. Manifest will be empty.")

    # Write the manifest to a JSON file
    output_filename = "commands_manifest.json"
    print(f"Writing manifest to {output_filename}")
    with open(output_filename, "w") as f:
        json.dump(manifest, f, indent=2)
    print("Manifest file generation complete.")

    # Update the improve.toml prompt
    template_path = "commands/prompts/improve.toml.template"
    output_path = "commands/prompts/improve.toml"
    print(f"Updating {output_path} from {template_path}")
    with open(template_path, "r") as f:
        template_content = f.read()

    manifest_json = json.dumps(manifest, indent=2)
    new_content = template_content.replace("{{COMMAND_MANIFEST}}", manifest_json)

    with open(output_path, "w") as f:
        f.write(new_content)
    print(f"{output_path} updated successfully.")


if __name__ == "__main__":
    generate_manifest()
