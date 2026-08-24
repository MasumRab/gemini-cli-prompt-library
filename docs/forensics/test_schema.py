import json
import os

schema_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "forensics_data_schema.json"
)
with open(schema_path, "r") as f:
    schema = json.load(f)

print("Schema loaded successfully")
print("Keys in schema:", list(schema.keys()))

if "definitions" in schema:
    print("Definitions keys:", list(schema["definitions"].keys()))
    if "Metadata" in schema["definitions"]:
        metadata = schema["definitions"]["Metadata"]
        print("Metadata keys:", list(metadata.keys()))
        if "properties" in metadata:
            print("Metadata properties keys:", list(metadata["properties"].keys()))
            if "migrations" in metadata["properties"]:
                print(
                    "Migrations property found:", metadata["properties"]["migrations"]
                )
            else:
                print("Migrations property NOT found in metadata properties")
        else:
            print("No properties in Metadata")
    else:
        print("Metadata not found in definitions")
else:
    print("No definitions in schema")

# Also check if migrations is directly in Metadata (not in properties)
if "Metadata" in schema["definitions"]:
    metadata = schema["definitions"]["Metadata"]
    if "migrations" in metadata:
        print("Migrations found directly in Metadata:", metadata["migrations"])
    else:
        print("Migrations NOT found directly in Metadata")
