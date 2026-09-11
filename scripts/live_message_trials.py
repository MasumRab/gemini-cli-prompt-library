#!/usr/bin/env python3
"""T4/T5b: Live message trials on EXISTING sessions from session_tracking records.

No session creation. Protocol (variance-tolerant):
  - 2 attempts per target, separated by 60s
  - verdict: 2xx = SUPPORTED / TRANSIENT after retries = INCONCLUSIVE / stable 4xx = DETERMINISTIC
  - every attempt logged to session_tracking/EXPERIMENTS.md (via E1 writer below)

T5b targets (FAILED sessions from records) - message acceptance proof on FAILED state:
    10865630989900669675  (ci-fix, EmailIntelligence)  -> retry text
    13005011563799472129  (ci-fix, EmailIntelligence)  -> retry text
    9164742845732374282   (ci-fix, EmailIntelligence)  -> RE-OPENING style (recovery_payloads.json)

T4 targets (oldest awaiting sessions from records) - A/B message method:
    6551222913502603426  (ci-fix, EmailIntelligence, PR #724)  -> surgical template
    16994837303056291039 (general, kaggle-notebooks-analysis)  -> generic nudge
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.api.jules_api_client import JulesAPIClient

TARGETS = [
    {
        "id": "10865630989900669675",
        "phase": "T5b-retry",
        "state": "FAILED",
        "message": "Please retry the last step.",
        "source": "RetryLastMessageStrategy (tools/sessions/jules_recovery_manager.py)",
    },
    {
        "id": "13005011563799472129",
        "phase": "T5b-retry",
        "state": "FAILED",
        "message": "Please retry the last step.",
        "source": "RetryLastMessageStrategy (tools/sessions/jules_recovery_manager.py)",
    },
    {
        "id": "9164742845732374282",
        "phase": "T5b-reopen",
        "state": "FAILED",
        "message": ("RE-OPENING: Resume your task. If you encounter a FAILED state again, "
                    "your first action must be to run 'git status' and 'pytest --collect-only' "
                    "to diagnose the environment. Document findings and wait for feedback."),
        "source": "recovery_payloads.json (recovery-directive style)",
    },
    {
        "id": "6551222913502603426",
        "phase": "T4-surgical",
        "state": "AWAITING_USER_FEEDBACK",
        "message": ("Continue fixing the failing CI checks on PR #724 (frontend npm ci failures). "
                    "Reproduce the failure locally by running the exact install/CI commands from "
                    "the failing workflow logs. Fix only the failing step, re-run those same local "
                    "checks, and push to the existing PR branch. Do NOT create a new PR."),
        "source": "surgical template (failure_runbook + response_templates build-on-existing policy)",
    },
    {
        "id": "16994837303056291039",
        "phase": "T4-generic",
        "state": "AWAITING_USER_FEEDBACK",
        "message": ("Status update? If you're encountering blockers, describe them. "
                    "Otherwise, continue with the remaining work."),
        "source": "generic nudge (response_templates IN_PROGRESS_STUCK template)",
    },
]


def record_trial(entry: dict) -> None:
    log = ROOT / "session_tracking" / "EXPERIMENTS.md"
    log.touch(exist_ok=True)
    lines = []
    if log.stat().st_size > 0:
        lines.append(log.read_text(encoding="utf-8").rstrip() + "\n")
    lines.append(f"### {entry['phase']} — {entry['id']} — {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
    lines.append(f"- session_id: `{entry['id']}` (state {entry['state']})\n")
    lines.append(f"- attempt {entry['trial']}: **{entry['kind']}** ({entry['elapsed_s']}s)\n")
    lines.append(f"  detail: {entry['detail'][:300]}\n")
    lines.append(f"  message ({entry['source']}):\n  > {entry['message'][:300]}\n")
    log.write_text("".join(lines), encoding="utf-8")


def send_trial(client: JulesAPIClient, target: dict, trial: int) -> dict:
    t0 = time.time()
    try:
        client.send_message(target["id"], target["message"])
        kind = "2xx-SUPPORTED"
        detail = "sendMessage accepted (empty 200); FAILED/AWAITING session accepts messages"
    except RuntimeError as e:
        msg = str(e)
        if "HTTP 429" in msg or ("HTTP 5" in msg and "HTTP" in msg):
            kind = "TRANSIENT"
        else:
            kind = "DETERMINISTIC-ish"
        detail = msg[:300]
    except Exception as e:  # noqa: BLE001
        kind = "TRANSIENT"
        detail = f"{type(e).__name__}: {e}"[:300]
    entry = {**target, "trial": trial, "kind": kind,
             "elapsed_s": round(time.time() - t0, 1), "detail": detail}
    record_trial(entry)
    return entry


def main() -> int:
    client = JulesAPIClient()

    # --- Static preamble: record conformance check (T5-static) ---
    print("T5-static: recording canonical shape of existing sessions (sourceContext form)\n")
    conformant = nonconformant = 0
    for p in sorted((ROOT / "session_tracking").glob("*.json")):
        if p.name == "SUMMARY.json":
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue
        sc = data.get("sourceContext")
        if sc:
            if sc.get("source", "").startswith("sources/github/") and "githubRepoContext" in sc:
                conformant += 1
            else:
                nonconformant += 1
    print(f"records with canonical sourceContext: {conformant}, non-canonical: {nonconformant}")

    print("\nExecuting live message trials against EXISTING sessions:\n")
    results = []
    for i, target in enumerate(TARGETS):
        for trial in (1, 2):
            r = send_trial(client, target, trial)
            print(f"[{r['phase']} / {r['id']} trial {trial}] {r['kind']} ({r['elapsed_s']}s)")
            results.append(r)
            if trial == 1:
                time.sleep(60)

    print("\n" + "=" * 72)
    print("VERDICT SUMMARY")
    print("=" * 72)
    for phase in ("T5b-retry", "T5b-reopen", "T4-surgical", "T4-generic"):
        rs = [r for r in results if r["phase"] == phase]
        kinds = [r["kind"] for r in rs]
        verdict = "SUPPORTED" if all(k.startswith("2xx") for k in kinds) else (
            "INCONCLUSIVE (transient)" if all(k == "TRANSIENT" for k in kinds)
            else f"mixed: {kinds}")
        print(f"  {phase:<14} -> {verdict}")
    print("\nFull attempt log: session_tracking/EXPERIMENTS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())