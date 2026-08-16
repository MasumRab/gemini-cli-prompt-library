# Standardized Forensics Data Format

## Purpose

This standardized forensics data format provides a consistent structure for storing and analyzing software development forensics data. By establishing a common schema, we enable:

- Cross-repository analysis of development patterns
- Consistent intervention tracking and outcome measurement
- Reliable migration of legacy forensic data
- Improved collaboration between analysis teams
- Long-term preservation of forensic insights

## Schema Description

The standardized format consists of four main sections:

### Sessions
Contains data about development sessions, including:
- Session identifiers and timestamps
- Participant information
- Context and objectives
- Related pull requests and interventions

### Pull Requests
Tracks pull request data associated with sessions:
- PR identifiers, URLs, and metadata
- Review and discussion metrics
- Code change statistics
- Status and resolution information

### Interventions
Records intentional actions taken during development:
- Intervention type and description
- Timing and duration
- Actor responsible
- Expected and actual outcomes
- Effectiveness metrics

### Metadata
Provides contextual information about the dataset:
- Collection methodology and timeframe
- Schema version and validation info
- Data quality indicators
- Transformation history

## Using the migrated_forensics_data.json File

The `migrated_forensics_data.json` file contains all legacy forensics data converted to the standardized format. To use this file:

1. **Direct consumption**: Load the JSON file in your analysis tools using standard JSON parsing libraries
2. **Schema validation**: Validate against `forensics_data_schema.json` to ensure data integrity
3. **Querying**: Use JSON query tools (jq, JQ, or programming language libraries) to extract specific insights
4. **Integration**: Incorporate into existing analysis pipelines by mapping standardized fields to your metrics

Example usage with jq:
```bash
# Count total sessions
jq '.sessions | length' migrated_forensics_data.json

# List all intervention types
jq '.interventions[].type | unique' migrated_forensics_data.json

# Find sessions with specific PR counts
jq '.sessions[] | select(.pull_requests | length > 5)' migrated_forensics_data.json
```

## Contributing New Forensics Data

To contribute new forensics data to the standardized format:

### Policies for Storing New Data

1. **Format compliance**: All new data must conform to the current schema version in `forensics_data_schema.json`
2. **Data quality**: Ensure complete, accurate, and verifiable data entries
3. **Privacy considerations**: Remove or anonymize sensitive personal information according to organizational policies
4. **Temporal consistency**: Use ISO 8601 format for all timestamps (YYYY-MM-DDTHH:MM:SSZ)
5. **Identifier standards**: Use established naming conventions for sessions, PRs, and interventions
6. **Validation**: Run data through the migration script to verify compatibility before submission

### Submission Process

1. Prepare your data in JSON format following the schema
2. Validate using: `python migrate_forensics.py --validate your_data.json`
3. Submit validated data through the designated contribution channel
4. Include documentation about data collection methodology and scope

## Reference to Schema File

The definitive schema definition is maintained in [`forensics_data_schema.json`](forensics_data_schema.json). This file specifies:

- Required and optional fields for each section
- Data types and format constraints
- Enumerated values where applicable
- Relationships between entities
- Versioning information

Always refer to the latest schema version when creating or validating forensics data.

## Note About the Migration Script

The [`migrate_forensics.py`](migrate_forensics.py) script provides tools for:

- **Conversion**: Transforming legacy forensics data formats to the current standardized schema
- **Validation**: Checking compliance with the schema definition
- **Transformation**: Applying schema updates to existing standardized data
- **Quality assurance**: Identifying data inconsistencies or completeness issues

To use the migration script:
```bash
# Validate data against schema
python migrate_forensics.py --validate input_data.json

# Convert legacy format to standardized format
python migrate_forensics.py --convert legacy_data.json output_data.json

# Check schema version and migration history
python migrate_forensics.py --info
```

The script maintains backward compatibility and logs all transformations for auditability.