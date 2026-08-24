# Forensics Schema Migrations

This directory contains migration scripts for the Jules forensics data schema.

## Purpose

Migration scripts are used to update existing forensics data files from older schema versions to newer ones. Each migration script should be designed to:

1. Read data in an older schema version
2. Transform it to conform to a newer schema version
3. Save the migrated data, optionally overwriting the original or creating a new file

## Migration Script Naming Convention

Migration scripts should be named using the format:
`migrate_vX_Y_Z.py` where X_Y_Z represents the target schema version.

For example, `migrate_v1_1_0.py` would migrate data to schema version 1.1.0.

## Running Migrations

To run a specific migration script:
```bash
python3 migrate_vX_Y_Z.py [options]
```

See individual migration scripts for specific usage instructions.

## Adding New Migrations

When adding a new migration:
1. Create a new migration script in this directory
2. Update the `migrations` array in `forensics_data_schema.json` to document the migration
3. Ensure the migration script updates the schema version in migrated data appropriately