import copy
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency path
    yaml = None

DEFAULT_CONFIG = {
    "repo": {"name": "auto", "mode": "local_only"},
    "analysis": {
        "include_remote_branches": True,
        "include_local_branches": True,
        "include_pr_metadata": "auto",
        "default_base_strategy": "discover",
    },
    "roots": {"configured": [], "discover": True},
    "generated_files": {
        "patterns": ["dist/**", "build/**", "*.generated.*", "*.lock"],
        "treat_as_replay_risk": True,
    },
    "ignore_paths": [".git/**", ".venv/**", "node_modules/**"],
    "replay": {
        "large_commit_file_threshold": 20,
        "large_commit_line_threshold": 800,
        "detect_active_rebase": True,
        "detect_conflict_markers": True,
        "detect_delete_modify": True,
        "detect_both_modified": True,
    },
    "execution": {"default_mode": "analyzer_only", "require_explicit_approval": True},
}


def _merge(base, override):
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def _read_yaml(path):
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(text) or {}
    # Minimal fallback for absent PyYAML: defaults still work, explicit config is optional.
    return {}


def load_config(agent_dir=".graphite-agent", overrides=None):
    agent_dir = Path(agent_dir)
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg = _merge(cfg, _read_yaml(agent_dir / "config" / "repo.yaml"))
    cfg = _merge(cfg, overrides or {})
    cfg["_meta"] = {
        "agent_dir": str(agent_dir),
        "config_source": (
            "repo.yaml" if (agent_dir / "config" / "repo.yaml").exists() else "defaults"
        ),
    }
    return cfg
