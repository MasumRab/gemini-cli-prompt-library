import subprocess
from fnmatch import fnmatch
from pathlib import Path


def git(args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def conflict_type(status):
    return {
        "UU": "both_modified",
        "UD": "deleted_by_theirs",
        "DU": "deleted_by_us",
        "AA": "both_added",
        "DD": "both_deleted",
    }.get(status.strip(), "unmerged")


def marker_files(paths):
    found = []
    for item in paths:
        p = Path(item["path"] if isinstance(item, dict) else item)
        if not p.exists() or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "<<<<<<<" in text and ">>>>>>>" in text:
            found.append(str(p))
    return found


def generated_matches(paths, patterns):
    out = []
    for path in paths:
        if any(fnmatch(path, pat) for pat in patterns):
            out.append(
                {
                    "path": path,
                    "reason": "configured generated-file pattern",
                    "recommendation": "regenerate after replay rather than manually resolve",
                }
            )
    return out


def recent_commit_risks(config, limit=30):
    file_threshold = int(
        config.get("replay", {}).get("large_commit_file_threshold", 20)
    )
    line_threshold = int(
        config.get("replay", {}).get("large_commit_line_threshold", 800)
    )
    log = git(["log", f"-{limit}", "--pretty=%H%x1f%s"]).stdout.splitlines()
    risks = []
    for line in log:
        if "\x1f" not in line:
            continue
        sha, subject = line.split("\x1f", 1)
        stat = git(["show", "--shortstat", "--format=", sha]).stdout.strip()
        files = insertions = deletions = 0
        for part in [x.strip() for x in stat.split(",")]:
            bits = part.split()
            if len(bits) >= 2 and bits[1].startswith("file"):
                files = int(bits[0])
            elif len(bits) >= 2 and bits[1].startswith("insertion"):
                insertions = int(bits[0])
            elif len(bits) >= 2 and bits[1].startswith("deletion"):
                deletions = int(bits[0])
        if files >= file_threshold or insertions + deletions >= line_threshold:
            risks.append(
                {
                    "commit": sha[:12],
                    "subject": subject,
                    "risk": "large_mixed_commit",
                    "files_changed": files,
                    "lines_changed": insertions + deletions,
                    "recommendation": "consider decomposition before replay",
                }
            )
    return risks


def assess_replay(config, inventory, run_id):
    state = inventory.get("state", {})
    conflicted = [
        {
            "path": x["path"],
            "status": x["status"],
            "conflict_type": conflict_type(x["status"]),
        }
        for x in state.get("conflicted_files", [])
    ]
    conflict_paths = [x["path"] for x in conflicted]
    changed_paths = [
        line[3:]
        for line in git(["status", "--porcelain"]).stdout.splitlines()
        if len(line) > 3
    ]
    generated = generated_matches(
        sorted(set(conflict_paths + changed_paths)),
        config.get("generated_files", {}).get("patterns", []),
    )
    markers = marker_files(conflicted)
    commit_risks = recent_commit_risks(config)
    blockers = []
    if state.get("active_rebase"):
        blockers.append("active rebase/conflict state detected")
    if state.get("active_merge"):
        blockers.append("active merge state detected")
    if state.get("active_cherry_pick"):
        blockers.append("active cherry-pick state detected")
    if conflicted:
        blockers.append("conflicted files detected")
    if markers:
        blockers.append("conflict markers detected")
    if any(
        x["conflict_type"] in {"both_modified", "deleted_by_theirs", "deleted_by_us"}
        for x in conflicted
    ):
        blockers.append("blocking unmerged conflict types detected")
    overall = "high" if blockers else ("medium" if commit_risks or generated else "low")
    recs = []
    if blockers:
        recs.extend(
            [
                "Abort or finish the active replay before Graphite restack.",
                "Resolve conflicted files manually.",
                "Run hunk decomposition before command plan generation.",
            ]
        )
    elif commit_risks:
        recs.append("Review large mixed commits before restacking.")
    else:
        recs.append("No immediate replay blockers detected by the V7.4 skeleton.")
    return {
        "run_id": run_id,
        "summary": {
            "overall_risk": overall,
            "execution_allowed": overall == "low",
            "primary_reason": (
                blockers[0]
                if blockers
                else (
                    "large/generated change risk detected"
                    if overall == "medium"
                    else "no replay blockers detected"
                )
            ),
        },
        "repository_state": {
            "active_rebase": bool(state.get("active_rebase")),
            "active_merge": bool(state.get("active_merge")),
            "active_cherry_pick": bool(state.get("active_cherry_pick")),
            "dirty_worktree": bool(inventory.get("repo", {}).get("is_dirty")),
        },
        "conflicts": {
            "conflicted_files": conflicted,
            "conflict_markers_detected": markers,
        },
        "commit_risks": commit_risks,
        "generated_file_risks": generated,
        "recommendations": recs,
    }


def assess_fixture(status_text, run_id="fixture"):
    conflicted = []
    active_rebase = False
    for line in status_text.splitlines():
        if (
            "rebase in progress" in line.lower()
            or "interactive rebase in progress" in line.lower()
        ):
            active_rebase = True
        if len(line) > 3 and line[:2].strip() in {"UU", "UD", "DU", "AA", "DD"}:
            conflicted.append({"path": line[3:].strip(), "status": line[:2].strip()})
    inv = {
        "state": {
            "active_rebase": active_rebase,
            "active_merge": False,
            "active_cherry_pick": False,
            "conflicted_files": conflicted,
        },
        "repo": {"is_dirty": bool(conflicted)},
    }
    return assess_replay(
        {
            "generated_files": {"patterns": ["*.lock", "commands_manifest.json"]},
            "replay": {
                "large_commit_file_threshold": 20,
                "large_commit_line_threshold": 800,
            },
        },
        inv,
        run_id,
    )
