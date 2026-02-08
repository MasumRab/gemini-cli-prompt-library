import os
import tomli
import logging


def get_commands():
    commands = []
    for root, dirs, files in os.walk("commands"):
        for file in files:
            if file.endswith(".toml"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "rb") as f:
                        data = tomli.load(f)
                        prompt = data.get("prompt", "")
                        prompt_lines = prompt.strip().split("\n")
                        description = ""
                        for line in prompt_lines:
                            cleaned_line = line.strip()
                            if cleaned_line and cleaned_line.startswith("#"):
                                description = cleaned_line.strip("# ").strip()
                                if description:
                                    break
                        name = os.path.splitext(file)[0]
                        category = os.path.basename(root)
                        commands.append(
                            {
                                "name": name,
                                "category": category,
                                "description": description,
                                "examples": [],  # Placeholder for examples
                            }
                        )
                except Exception as e:
                    logging.warning(f"Error parsing {filepath}: {e}")
    return commands


if __name__ == "__main__":
    commands = get_commands()
    print(len(commands))
