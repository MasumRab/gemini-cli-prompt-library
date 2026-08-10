def branch_stacking_report(inventory, replay_risk, validation=None):
    validation = validation or {}
    repo = inventory.get("repo", {})
    state = inventory.get("state", {})
    summary = replay_risk.get("summary", {})
    lines = [
        "# Branch Stacking Report",
        "",
        "## Executive Summary",
        "",
        f"- Overall replay risk: **{summary.get('overall_risk', 'unknown')}**",
        f"- Execution allowed: **{summary.get('execution_allowed', False)}**",
        f"- Primary reason: {summary.get('primary_reason', 'unknown')}",
        "",
    ]
    if summary.get("overall_risk") == "high":
        lines += [
            "> Execution is not recommended.",
            "> Do not run Graphite restack until replay blockers are resolved.",
            "",
        ]
    lines += [
        "## Repository Inventory",
        "",
        f"- Git root: `{repo.get('git_root')}`",
        f"- Current branch: `{repo.get('current_branch')}`",
        f"- Dirty worktree: `{repo.get('is_dirty')}`",
        "",
        "## Current Git State",
        "",
        f"- Active rebase: `{state.get('active_rebase')}`",
        f"- Active merge: `{state.get('active_merge')}`",
        f"- Active cherry-pick: `{state.get('active_cherry_pick')}`",
        f"- Conflicted files: `{len(state.get('conflicted_files', []))}`",
        "",
        "## Target / Root Candidates",
        "",
    ]
    for item in inventory.get("targets", {}).get("discovered", []):
        lines.append(
            f"- `{item.get('name')}` ({item.get('source')}, {item.get('confidence')})"
        )
    if not inventory.get("targets", {}).get("discovered"):
        lines.append("- None discovered")
    lines += [
        "",
        "## Branch Topology Summary",
        "",
        "- V7.4 scaffold defers full topology to existing V7.3 tools.",
        "",
        "## Replay Risk Summary",
        "",
    ]
    for rec in replay_risk.get("recommendations", []):
        lines.append(f"- {rec}")
    lines += ["", "## Conflict Forecast", ""]
    conflicts = replay_risk.get("conflicts", {}).get("conflicted_files", [])
    if conflicts:
        for item in conflicts:
            lines.append(
                f"- `{item.get('path')}`: {item.get('conflict_type')} ({item.get('status')})"
            )
    else:
        lines.append("- No conflicted files detected.")
    lines += ["", "## Generated File Risks", ""]
    for item in replay_risk.get("generated_file_risks", []):
        lines.append(f"- `{item.get('path')}`: {item.get('recommendation')}")
    if not replay_risk.get("generated_file_risks"):
        lines.append("- None detected.")
    lines += ["", "## Large Mixed Commits", ""]
    for item in replay_risk.get("commit_risks", []):
        lines.append(
            f"- `{item.get('commit')}` {item.get('subject')} ({item.get('files_changed')} files, {item.get('lines_changed')} lines)"
        )
    if not replay_risk.get("commit_risks"):
        lines.append("- None above configured threshold.")
    lines += [
        "",
        "## Branches Safe to Stack",
        "",
        "- Not emitted by V7.4 replay scaffold.",
        "",
        "## Branches Blocked from Stacking",
        "",
    ]
    if validation.get("status") == "blocked":
        for check in validation.get("failed_checks", []):
            lines.append(f"- {check.get('id')}: {check.get('message')}")
    else:
        lines.append("- None from replay validator.")
    lines += [
        "",
        "## Manual Decisions Required",
        "",
        (
            "- Resolve semantic conflicts manually before execution."
            if summary.get("overall_risk") == "high"
            else "- None detected by replay scaffold."
        ),
        "",
        "## Recommended Next Commands",
        "",
        "```bash",
        "python .graphite-agent/tools/discover_repo.py --local-only",
        "python .graphite-agent/tools/replay_risk.py --local-only",
        "python .graphite-agent/tools/validate_replay.py",
        "python .graphite-agent/tools/write_report.py",
        "python .graphite-agent/tools/build_command_plan.py --dry-run",
        "```",
        "",
        "## Execution Status",
        "",
        f"Validation status: `{validation.get('status', 'not_run')}`",
        "",
    ]
    return "\n".join(lines)
