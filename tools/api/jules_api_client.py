import json
import os
import sys
from typing import Optional, Dict, Any, Generator, Iterable
import requests


def get_jules_api_key() -> str:
    """Retrieve the Jules API key from the environment.

    Supports JULES_API_KEY (primary).
    """
    key = os.environ.get("JULES_API_KEY")
    if not key:
        print(
            "ERROR: Jules API key not found. Please set JULES_API_KEY.", file=sys.stderr
        )
        sys.exit(1)
    return key


def _validate_not_placeholder(name: str, value: str) -> None:
    """Reject placeholder/dummy values before they reach the API.

    Catches common patterns a naive agent or user might copy from docs:
    YOUR_API_KEY, <insert key here>, dummy, xxx, test-key, etc.
    """
    value = value.strip().lower()
    import re as _re

    placeholders = [
        _re.compile(r)
        for r in (
            r"^YOUR_",
            r"CHANGE_ME",
            r"^<.*>$",
            r"^\{\{.*\}\}$",
            r"^test[_-]key$",
            r"^your[_-]key",
            r"placeholder",
            r"^xxx+$",
            r"^dummy$",
        )
    ]
    for pattern in placeholders:
        if pattern.search(value):
            print(
                f'ERROR: {name} value looks like a placeholder '
                f"(matched: {pattern.pattern}). Set the real API key via env var.",
                file=sys.stderr,
            )
            sys.exit(1)


def jules_request(
    endpoint: str,
    method: str = "GET",
    body: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    base_url: str = "https://api.jules.ai/v1",
    max_retries: int = 3,
) -> Dict[str, Any]:
    """Make a raw request to the Jules API."""
    if not api_key:
        api_key = get_jules_api_key()

    _validate_not_placeholder("JULES_API_KEY", api_key)

    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    import time

    for attempt in range(max_retries):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=body, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
                    continue
                else:
                    response.raise_for_status()

            if response.status_code >= 500:
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
                    continue

            response.raise_for_status()

            if not response.content:
                return {}

            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
                continue
            print(f"ERROR: Request to {url} failed: {e}", file=sys.stderr)
            raise

    return {}


class JulesAPIClient:
    """A minimal client for interacting with Jules sessions."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_jules_api_key()
        self.base_url = "https://api.jules.ai/v1"

    def request(
        self, endpoint: str, method: str = "GET", body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to the API."""
        return jules_request(
            endpoint,
            method=method,
            body=body,
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def list_sessions(
        self,
        page_size: int = 50,
        max_results: Optional[int] = None,
        page_token: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Yield sessions, handling pagination automatically."""
        yielded_count = 0
        current_token = page_token

        while True:
            remaining = (
                max_results - yielded_count if max_results is not None else None
            )
            if remaining is not None and remaining <= 0:
                break

            effective_page = (
                min(page_size, remaining) if remaining is not None else page_size
            )
            params = f"?pageSize={effective_page}"
            if current_token:
                params += f"&pageToken={current_token}"

            try:
                response = self.request(f"/sessions{params}")
                sessions = response.get("sessions", [])

                for session in sessions:
                    if state and session.get("state") != state:
                        continue
                    yield session
                    yielded_count += 1
                    if max_results is not None and yielded_count >= max_results:
                        return

                current_token = response.get("nextPageToken")
                if not current_token:
                    break
            except requests.exceptions.RequestException:
                break

    def list_activities(
        self,
        session_id: str,
        page_size: int = 100,
        max_results: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Yield activities for a session, handling pagination automatically.
        Activities are returned chronologically (oldest first).
        """
        # The API currently returns activities oldest-first via list
        # But we'll collect pages and yield as requested.

        yielded_count = 0
        current_token = page_token
        sid = session_id.replace("sessions/", "")

        while True:
            remaining = (
                max_results - yielded_count if max_results is not None else None
            )
            if remaining is not None and remaining <= 0:
                break

            effective_page = (
                min(page_size, remaining) if remaining is not None else page_size
            )
            params = f"?pageSize={effective_page}"
            if current_token:
                params += f"&pageToken={current_token}"

            try:
                response = self.request(f"/sessions/{sid}/activities{params}")
                activities = response.get("activities", [])

                # The API typically returns oldest first per page.
                # If we want true oldest first, we should really traverse
                # next page tokens.

                for activity in activities:
                    yield activity
                    yielded_count += 1
                    if max_results is not None and yielded_count >= max_results:
                        return

                current_token = response.get("nextPageToken")
                if not current_token:
                    break
            except requests.exceptions.RequestException:
                break

    def get_latest_activities(
        self, session_id: str, max_results: int = 10
    ) -> Iterable[Dict[str, Any]]:
        """A convenience method to get the most recent activities for a session."""
        # The API doesn't currently support reverse-order pagination natively.
        # We fetch up to 500, then slice the end.
        all_activities = list(
            self.list_activities(session_id, page_size=100, max_results=500)
        )
        return all_activities[-max_results:]

    def wait_for_session_state(
        self,
        session_id: str,
        target_states: Iterable[str] = ("COMPLETED", "FAILED"),
        timeout: float = 300,
        poll_interval: float = 5.0,
    ) -> Dict[str, Any]:
        """Poll a session until it enters one of the target states or times out."""
        sid = session_id.replace("sessions/", "")
        import time as _time

        deadline = _time.monotonic() + timeout

        while _time.monotonic() < deadline:
            try:
                session = self.request(f"/sessions/{sid}")
                if session.get("state") in target_states:
                    return session
            except requests.exceptions.RequestException:
                pass
            _time.sleep(poll_interval)

        raise TimeoutError(f"Session {sid} did not reach {target_states} in {timeout}s")

    def ask(
        self, session_id: str, question: str, timeout: float = 120
    ) -> Dict[str, Any]:
        """Send a message and wait for the agent's reply.

        This handles the state transition sequence:
        AWAITING_USER_FEEDBACK -> IN_PROGRESS -> AWAITING_USER_FEEDBACK
        """
        sid = session_id.replace("sessions/", "")
        self.request(
            f"/sessions/{sid}:message", method="POST", body={"message": question}
        )

        import time as _time

        before = _time.monotonic()

        while _time.monotonic() - before < timeout:
            try:
                session = self.request(f"/sessions/{sid}")
                if session.get("state") == "AWAITING_USER_FEEDBACK":
                    # Get the latest message
                    activities = self.get_latest_activities(sid, 10)
                    for act in reversed(activities):
                        if "agentMessaged" in act:
                            return act
                elif session.get("state") in ("COMPLETED", "FAILED"):
                    raise RuntimeError(f"Session ended unexpectedly: {session}")
            except requests.exceptions.RequestException:
                pass
            _time.sleep(2)
        raise TimeoutError(f"Agent did not reply to {session_id} within {timeout}s")

    def sync_session_to_store(
        self, session_id: str, store: "JulesSessionStore"
    ) -> bool:
        """Fetch a session and its activities, saving them to the store."""
        sid = session_id.replace("sessions/", "")
        try:
            session = self.request(f"/sessions/{sid}")
            store.upsert_session(session)
        except requests.exceptions.RequestException:
            return False

        activities = list(
            self.list_activities(session_id, page_size=100, max_results=500)
        )
        return store.upsert_activities(sid, activities)

    def list_sources(
        self, page_size: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """Yield all connected sources, handling pagination automatically."""
        yielded_count = 0
        current_token = None

        while True:
            params = f"?pageSize={page_size}"
            if current_token:
                params += f"&pageToken={current_token}"

            try:
                response = self.request(f"/sources{params}")
                sources = response.get("sources", [])

                for source in sources:
                    yield source
                    yielded_count += 1

                current_token = response.get("nextPageToken")
                if not current_token:
                    break
            except requests.exceptions.RequestException:
                break


def find_github_source_id(owner_repo: str) -> Optional[str]:
    """Find the source_id for a given GitHub owner/repo if connected to Jules.

    Args:
        owner_repo: e.g. "masumrab/gemini-cli"

    Returns:
        The source ID if found, otherwise None.
    """
    client = JulesAPIClient()

    if "/" not in owner_repo:
        raise ValueError(f"Invalid repo format '{owner_repo}'. Use 'owner/repo'.")
    owner, repo = owner_repo.split("/", 1)
    owner = owner.lower()
    repo = repo.lower()

    for source in client.list_sources():
        git_config = source.get("githubConfig", {})
        # Note: API format varies slightly depending on if it's app installation or personal
        # We check both repositoryName and the repo list.
        if "repositoryName" in git_config:
            # Single repo config
            if git_config["repositoryName"].lower() == owner_repo:
                return source["name"]
        elif "repositories" in git_config:
            # Multi repo config
            for r in git_config["repositories"]:
                if r.lower() == owner_repo:
                    return source["name"]

        # General check for github.com/owner/repo in uri
        uri = git_config.get("uri", "").lower()
        if owner in uri and repo in uri:
            return source["name"]

    return None

