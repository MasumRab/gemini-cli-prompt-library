"""
Graphite Agent V8 Tools Package

This package contains all the CLI tools for Graphite Agent V8.

Structure:
- lib/ - Library modules
- main.py - Unified dispatcher ( Entry point)
- analyse.py - Analysis pipeline
- agent_core.py - Core analysis and triage
- discover_repo.py - Repository discovery
- discover_targets.py - Target discovery
- replay_risk.py - Replay risk assessment
- validate_replay.py - Replay validation
- write_report.py - Report generation
- build_command_plan.py - Command plan building
- checklist.py - Checklist generation
- execute_approved.py - Execution engine
- And many more...

Usage:
    python -m tools.main discover
    python -m tools.main run
    python .graphite-agent/tools/main.py analyse
"""

__version__ = "8.0"
