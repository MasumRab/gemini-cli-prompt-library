# Jules API Skill

Quick reference for using the Jules REST API with Python scripts.

## Requirements
- `JULES_API_KEY` - Generate at https://jules.google.com/settings#api
- Python 3.12+ with `requests` library

## Commands
```bash
python3 tools/cli/jules-manager.py list           # List sessions
python3 tools/cli/jules-manager.py session ID    # Get session details
python3 tools/cli/jules-manager.py send ID "msg" # Send message
python3 tools/cli/jules-manager.py approve ID    # Approve plan
```