import subprocess
from pathlib import Path


def git(args, check=False):
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def lines(result):
    return [x for x in result.stdout.splitlines() if x.strip()]


def git_root():
    out = git(["rev-parse", "--show-toplevel"])
    return out.stdout.strip() if out.returncode == 0 else str(Path.cwd())


def active_state(root):
    gd = git(["rev-parse", "--git-dir"])
    git_dir = Path(gd.stdout.strip()) if gd.returncode == 0 else Path(root) / ".git"
    if not git_dir.is_absolute():
        git_dir = Path(root) / git_dir
    conflicted = []
    for line in lines(git(["status", "--porcelain"])):
        status = line[:2]
        path = line[3:]
        if "U" in status or status in {"AA", "DD"}:
            conflicted.append({"path": path, "status": status})
    return {
        "active_rebase": (git_dir / "rebase-merge").exists()
        or (git_dir / "rebase-apply").exists(),
        "active_merge": (git_dir / "MERGE_HEAD").exists(),
        "active_cherry_pick": (git_dir / "CHERRY_PICK_HEAD").exists(),
        "conflicted_files": conflicted,
    }


def branch_list(kind):
    args = [
        "for-each-ref",
        "--format=%(refname:short)|%(objectname)|%(committerdate:iso8601)|%(subject)",
    ]
    args.append("refs/heads" if kind == "local" else "refs/remotes")
    out = []
    for line in lines(git(args)):
        name, sha, date, subject = (line.split("|", 3) + ["", "", "", ""])[:4]
        if kind == "remote" and name.endswith("/HEAD"):
            continue
        out.append(
            {"name": name, "head_sha": sha, "committer_date": date, "subject": subject}
        )
    return out


def origin_head():
    out = git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"])
    return out.stdout.strip().removeprefix("origin/") if out.returncode == 0 else None


def discover_roots(config):
    configured = config.get("roots", {}).get("configured", []) or []
    discovered = []
    oh = origin_head()
    if oh:
        discovered.append({"name": oh, "source": "origin_head", "confidence": "high"})
    for candidate in ["main", "master", "develop", "trunk"]:
        if git(
            ["rev-parse", "--verify", f"{candidate}^{{commit}}"]
        ).returncode == 0 and candidate not in [x["name"] for x in discovered]:
            discovered.append(
                {
                    "name": candidate,
                    "source": "common_branch_name",
                    "confidence": "medium",
                }
            )
    return {"configured": configured, "discovered": discovered}


def collect_inventory(config, run_id):
    root = git_root()
    branch = git(["branch", "--show-current"]).stdout.strip() or None
    dirty = bool(lines(git(["status", "--porcelain"])))
    gh = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--json",
            "number,headRefName,baseRefName,headRefOid,title",
        ],
        capture_output=True,
        text=True,
    )
    pr_metadata = {"available": gh.returncode == 0, "items": []}
    if gh.returncode != 0:
        pr_metadata["reason"] = "gh CLI unavailable or not authenticated"
    else:
        import json

        try:
            pr_metadata["items"] = json.loads(gh.stdout or "[]")
        except Exception:
            pr_metadata = {
                "available": False,
                "reason": "gh output was not valid JSON",
                "items": [],
            }
    return {
        "run_id": run_id,
        "repo": {
            "path": root,
            "git_root": root,
            "current_branch": branch,
            "is_dirty": dirty,
        },
        "state": active_state(root),
        "branches": {"local": branch_list("local"), "remote": branch_list("remote")},
        "targets": discover_roots(config),
        "pr_metadata": pr_metadata,
    }
