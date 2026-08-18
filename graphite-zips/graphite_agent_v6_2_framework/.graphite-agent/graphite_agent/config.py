import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GraphiteAgentConfig:
    configured_roots: list[str]
    default_root: str
    primary_remote: str = "origin"
    output_dir: str = ".graphite-agent/outputs"
    schema_version: str = "6.2"
    write_legacy_aliases: bool = True


def load_config() -> GraphiteAgentConfig:
    raw_roots = os.getenv("GRAPHITE_TRUNK_BRANCHES", "main")
    roots = [root.strip() for root in raw_roots.split(",") if root.strip()] or ["main"]
    return GraphiteAgentConfig(
        configured_roots=roots,
        default_root=roots[0],
        primary_remote=os.getenv("GRAPHITE_PRIMARY_REMOTE", "origin"),
        output_dir=os.getenv("GRAPHITE_AGENT_OUTPUT_DIR", ".graphite-agent/outputs"),
        schema_version=os.getenv("GRAPHITE_AGENT_SCHEMA_VERSION", "6.2"),
        write_legacy_aliases=os.getenv("GRAPHITE_WRITE_LEGACY_ALIASES", "1") != "0",
    )
