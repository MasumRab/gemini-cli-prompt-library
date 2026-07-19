# Jules Auth Setup Runbook

## Overview

The Jules REST API uses API key authentication via the `X-Goog-Api-Key` header (not OAuth2 bearer tokens).

## API Key

1. Obtain a Jules API key from the Google Cloud console or your Jules workspace settings
2. Set it in your environment:

```bash
export JULES_API_KEY="your-api-key-here"
```

Or add to `~/.env`:
```
JULES_API_KEY=your-api-key-here
```

## GitHub Token (for PR tools)

Some tools (`session_pr_triage.py`, `jules_pr_triage.py`) need a GitHub token:

```bash
export GITHUB_TOKEN="ghp_..."
```

## Validation

Run the auth check to verify credentials:

```bash
uv run python3 -m tools.utils.auth_manager
```

This validates:
- Key is non-empty
- Key doesn't match placeholder patterns (`YOUR_`, `CHANGE_ME`, `<placeholder>`)
- Key is at least 10 characters

## How Keys Are Used

- `JulesAPIClient` reads `JULES_API_KEY` from environment in `get_api_key()`
- PR tools read `GITHUB_TOKEN` from environment via `auth_manager.get_github_token()`
- The `load_dotenv()` call in `auth_manager.py` auto-loads from `.env` files

## API Endpoint

Base URL: `https://jules.googleapis.com/v1alpha`
Auth header: `X-Goog-Api-Key: <your-key>`
