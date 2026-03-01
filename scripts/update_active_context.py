#!/usr/bin/env python3
import os
import subprocess
import requests
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

MAX_PR_PROCESS = int(os.environ.get("MAX_PR_PROCESS", "50"))


def get_repository() -> str:
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        return repo
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        url = result.stdout.strip()
        # Parse git@github.com:owner/repo.git or https://github.com/owner/repo.git safely
        match = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", url)
        if match:
            return match.group(1)
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.SubprocessError,
    ) as e:
        logger.error(f"Failed to get repository from git config: {e}", exc_info=True)
    return ""


def fetch_paginated(
    url: str, headers: Dict[str, str], timeout: int = 10
) -> List[Dict[str, Any]]:
    results = []
    while url:
        # Enforce SSL verification explicitly for security tools
        response = requests.get(url, headers=headers, timeout=timeout, verify=True)
        response.raise_for_status()
        results.extend(response.json())

        # Check for next page in Link header
        link_header = response.headers.get("Link", "")
        next_url = None
        if link_header:
            links = link_header.split(",")
            for link in links:
                parts = link.split(";")
                if len(parts) == 2 and 'rel="next"' in parts[1]:
                    next_url = parts[0].strip()[1:-1]  # Remove < and >
                    break
        url = next_url
    return results


def main():
    docs_dir = os.path.join(os.getcwd(), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    output_file = os.path.join(docs_dir, "ACTIVE_CONTEXT.md")

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        with open(output_file, "w") as f:
            f.write("*GitHub Token missing - Context unavailable*\n")
        return

    repo = get_repository()
    if not repo:
        with open(output_file, "w") as f:
            f.write("*Repository cannot be determined - Context unavailable*\n")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        prs_url = f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=100"
        prs = fetch_paginated(prs_url, headers)

        if len(prs) > MAX_PR_PROCESS:
            logger.warning(
                f"Total PRs ({len(prs)}) exceeds MAX_PR_PROCESS ({MAX_PR_PROCESS}). Only processing the first {MAX_PR_PROCESS}."
            )
            prs = prs[:MAX_PR_PROCESS]

        pr_data = []
        for pr in prs:
            pr_number = pr["number"]
            files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files?per_page=100"
            files = fetch_paginated(files_url, headers)
            file_names = [f["filename"] for f in files]

            pr_data.append(
                {
                    "number": pr_number,
                    "title": pr["title"],
                    "url": pr["html_url"],
                    "author": pr["user"]["login"],
                    "files": file_names,
                }
            )

        with open(output_file, "w") as f:
            f.write("# Active GitHub Context\n\n")
            f.write(
                "The following Pull Requests are currently open. The files listed below are **locked**.\n"
            )
            f.write(
                "Do NOT modify these files to avoid merge conflicts or duplicating work.\n\n"
            )

            if not pr_data:
                f.write("*No open Pull Requests found.*\n")
            else:
                f.write("| PR | Title | Author | Locked Files |\n")
                f.write("|---|---|---|---|\n")
                for pr in pr_data:
                    files_list = "<br>".join([f"`{file}`" for file in pr["files"]])
                    f.write(
                        f"| [#{pr['number']}]({pr['url']}) | {pr['title']} | @{pr['author']} | {files_list} |\n"
                    )

    except requests.RequestException as e:
        with open(output_file, "w") as f:
            f.write("*GitHub API request failed - Context unavailable*\n")
            f.write(f"<!-- Error: {e} -->\n")


if __name__ == "__main__":
    main()
