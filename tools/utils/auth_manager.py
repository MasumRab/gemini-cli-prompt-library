#!/usr/bin/env python3
"""
Centralized Authentication Manager.
Validates and provides API keys for Jules and GitHub.
"""
import os
import re
import sys

from dotenv import load_dotenv

load_dotenv()

class AuthError(Exception):
    """Raised when authentication validation fails."""
    pass

def _validate_key(key: str, name: str) -> str:
    if not key:
        raise AuthError(f"{name} is missing.")

    # Regex guards against placeholders
    placeholders = [r"YOUR_", r"PLACEHOLDER", r"xxx", r"CHANGE_ME", r"<.*>", r"\{\{.*\}\}"]
    for pattern in placeholders:
        if re.search(pattern, key, re.IGNORECASE):
            raise AuthError(f"{name} matches placeholder pattern: {pattern}")

    if len(key) < 10:
        raise AuthError(f"{name} is too short (< 10 chars).")

    return key

def get_jules_key() -> str:
    """Get and validate Jules API Key."""
    key = os.getenv("JULES_API_KEY")
    return _validate_key(key, "JULES_API_KEY")

def get_github_token() -> str:
    """Get and validate GitHub Token."""
    token = os.getenv("GITHUB_TOKEN")
    return _validate_key(token, "GITHUB_TOKEN")

if __name__ == "__main__":
    try:
        jules = get_jules_key()
        print(f"✅ Jules Key Valid: {jules[:4]}...{jules[-4:]}")
    except AuthError as e:
        print(f"❌ Jules Error: {e}")
        sys.exit(1)

    try:
        gh = get_github_token()
        print(f"✅ GitHub Token Valid: {gh[:4]}...{gh[-4:]}")
    except AuthError as e:
        print(f"❌ GitHub Error: {e}")
        sys.exit(1)
