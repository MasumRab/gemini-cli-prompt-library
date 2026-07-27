import json

with open("commands_manifest.json") as f:
    manifest = json.load(f)

print(list(manifest.keys()))
