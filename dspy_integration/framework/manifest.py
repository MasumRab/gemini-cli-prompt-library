import json
import os


def get_commands():
    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "commands_manifest.json",
    )
    if not os.path.exists(manifest_path):
        manifest_path = "commands_manifest.json"

    if not os.path.exists(manifest_path):
        return []

    with open(manifest_path, "r") as f:
        data = json.load(f)

    return [
        {"name": k.split(":")[1], "description": v, "category": k.split(":")[0][1:]}
        for k, v in data.items()
    ]
