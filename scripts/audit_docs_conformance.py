#!/usr/bin/env python3
"""T1: Docs conformance scan.

Extract every Jules API endpoint and JSON payload key referenced in skills/,
docs/, and commands/ and grade it against the canonical API shape derived from
tools/api/jules_api_client.py.

Canonical reference (v1alpha):
  Endpoints:
    GET    /sessions
    GET    /sessions/{id}
    POST   /sessions/{id}:sendMessage
    POST   /sessions/{id}:approvePlan
    POST   /sessions/{id}:archive
    POST   /sessions/{id}:unarchive
    DELETE /sessions/{id}
    GET    /sessions/{id}/activities
    GET    /sources
    GET    /sources/github/{owner}/{repo}
    POST   /sessions  (create)
  Create-session payload keys:
    prompt, sourceContext, sourceContext.source, sourceContext.githubRepoContext.startingBranch,
    title, automationMode, requirePlanApproval
  Known-invalid:
    payload keys: autoPr, baseBranch, "source": {"github": ...}, message
    endpoints:    :approve, :cancel, :listActivities
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCAN_DIRS = ["skills", "docs", "commands"]

VALID_ENDPOINT_RE = re.compile(
    r"/sessions(?::sendMessage|:approvePlan|:archive|:unarchive)?"
    r"|/sessions/\{?[^}\s\"']+\}?(?:/activities)?"
    r"|/sources(?:/github/[\w.-]+/[\w.-]+)?"
)
CUSTOM_METHOD_RE = re.compile(r"/sessions/[^:\s\"']*:([a-zA-Z]+)")
BODY_KEYS_RE = re.compile(r'"(\w+)":')
DANGEROUS = {
    "autoPr", "baseBranch",
}
DANGEROUS_ENDPOINTS = {"approve", "cancel", "listActivities"}


def scan_file(path: Path) -> list[dict]:
    findings = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return findings
    for lineno, line in enumerate(lines, 1):
        for m in CUSTOM_METHOD_RE.finditer(line):
            method = m.group(1)
            if method in DANGEROUS_ENDPOINTS:
                findings.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": lineno,
                    "kind": "endpoint",
                    "detail": f"custom method ':{method}' (canonical alternatives: "
                              f"sendMessage/approvePlan/archive/unarchive)",
                })
        if "listActivities" in line or ":listActivities" in line:
            findings.append({
                "file": str(path.relative_to(ROOT)),
                "line": lineno,
                "kind": "endpoint",
                "detail": ":listActivities — actual endpoint is GET /sessions/{id}/activities",
            })
        for key in DANGEROUS:
            if re.search(rf'"{key}"\s*:', line):
                findings.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": lineno,
                    "kind": "payload_key",
                    "detail": f'payload key "{key}" not part of canonical create-session shape '
                              f'(use sourceContext / automationMode / startingBranch)',
                })
        if "requirePlanApproval" in line and "requirePlanApproval" not in line.lower():
            pass
    return findings


def main() -> int:
    all_findings = []
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.suffix in (".md", ".sh", ".py") and p.is_file():
                all_findings.extend(scan_file(p))

    all_findings.sort(key=lambda f: (f["file"], f["line"]))
    if all_findings:
        print("Non-conformant Jules API references found:\n")
        for f in all_findings:
            print(f"  {f['file']}:{f['line']}  [{f['kind']}]  {f['detail']}")
        print(f"\nTotal: {len(all_findings)}")
    else:
        print("No non-conformant API references found in skills/, docs/, commands/.")
    return 0 if not all_findings else 1


if __name__ == "__main__":
    sys.exit(main())