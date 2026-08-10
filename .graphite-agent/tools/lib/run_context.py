#!/usr/bin/env python3
"""
Run Context - Shared state for Graphite Agent V8 pipeline.

This module provides a shared state object that flows through all pipeline stages,
ensuring consistent data access and state management across the entire workflow.
"""

import uuid
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from datetime import datetime


@dataclass
class RunContext:
    """Shared state object flowing through all pipeline stages."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_dir: Path = field(default_factory=lambda: Path('.graphite-agent'))
    outputs_dir: Path = field(default_factory=lambda: Path('.graphite-agent/outputs'))
    config: dict = field(default_factory=dict)
    inventory: Optional[dict] = None
    replay_risk: Optional[dict] = None
    replay_validation: Optional[dict] = None
    snapshot: Optional[dict] = None
    decisions: Optional[dict] = None
    execution_plan: Optional[dict] = None
    command_plan: Optional[dict] = None
    checklist: Optional[dict] = None
    validated_at_utc: Optional[str] = None

    def __post_init__(self):
        """Initialize paths and directories."""
        self.agent_dir = Path(self.agent_dir)
        self.outputs_dir = Path(self.outputs_dir)
        
        if not self.agent_dir.exists():
            raise FileNotFoundError(f"Agent directory not found: {self.agent_dir}")

        # Ensure outputs directory exists
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    @property
    def run_dir(self) -> Path:
        """Directory for this specific run's outputs."""
        return self.outputs_dir / 'runs' / self.run_id

    @property
    def latest_dir(self) -> Path:
        """Directory for latest run outputs."""
        return self.outputs_dir / 'latest'

    @property
    def validation_dir(self) -> Path:
        """Directory for validation outputs."""
        return self.latest_dir / 'validation'

    def save_state(self, filename: str = 'run_context.json') -> None:
        """Save context state to JSON file."""
        data = asdict(self)
        # Convert Path objects to strings for JSON serialization
        data = {k: str(v) if isinstance(v, Path) else v 
                for k, v in data.items()}
        
        self.run_dir.mkdir(parents=True, exist_ok=True)
        with open(self.run_dir / filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def save_latest_state(self, filename: str = 'run_context.json') -> None:
        """Save context state to latest directory."""
        data = asdict(self)
        data = {k: str(v) if isinstance(v, Path) else v 
                for k, v in data.items()}
        
        self.latest_dir.mkdir(parents=True, exist_ok=True)
        with open(self.latest_dir / filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load_state(cls, run_id: str) -> 'RunContext':
        """Load context from a specific run ID."""
        run_dir = Path('.graphite-agent/outputs/runs') / run_id
        context_file = run_dir / 'run_context.json'
        
        if not context_file.exists():
            raise FileNotFoundError(f"Run context not found: {context_file}")
        
        with open(context_file, 'r') as f:
            data = json.load(f)
        
        return cls(**data)

    @classmethod
    def load_latest(cls) -> 'RunContext':
        """Load the latest run context."""
        context_file = Path('.graphite-agent/outputs/latest/run_context.json')
        
        if not context_file.exists():
            # Return a fresh context if no latest exists
            return cls()
        
        with open(context_file, 'r') as f:
            data = json.load(f)
        
        return cls(**data)

    def save_output(self, filename: str, data: Any, to_latest: bool = True) -> Path:
        """Save an output file to both run and latest directories."""
        self.run_dir.mkdir(parents=True, exist_ok=True)
        path = self.run_dir / filename
        
        # Save to run directory
        self._write_output(path, data)
        
        # Save to latest directory
        if to_latest:
            self.latest_dir.mkdir(parents=True, exist_ok=True)
            latest_path = self.latest_dir / filename
            self._write_output(latest_path, data)
        
        return path

    def _write_output(self, path: Path, data: Any) -> None:
        """Write data to a file path."""
        if isinstance(data, dict):
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            with open(path, 'w') as f:
                f.write(str(data))

    def is_stale(self) -> bool:
        """Check if any input file is newer than the last validation timestamp."""
        if not self.validated_at_utc:
            return True  # Never validated

        try:
            validated_at = datetime.fromisoformat(
                self.validated_at_utc.replace('Z', '+00:00')
            )
        except (ValueError, AttributeError):
            return True

        # List of input files that affect validation
        input_files = [
            'analysis_snapshot.json',
            'target_matrix.json', 
            'root_health.json',
            'stack_order.json',
            'repo_inventory.json',
            'replay_risk.json'
        ]

        for filename in input_files:
            path = self.latest_dir / filename
            if path.exists():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime > validated_at:
                    return True

        return False

    def mark_validated(self) -> None:
        """Mark the current timestamp as validated."""
        self.validated_at_utc = datetime.utcnow().isoformat() + 'Z'

    @classmethod
    def from_config(cls, config_path: Optional[Path] = None) -> 'RunContext':
        """Create a new context from a config file."""
        ctx = cls()
        
        if config_path:
            config_path = Path(config_path)
        else:
            # Try multiple possible config locations
            for candidate in [
                Path('.graphite-agent/config/repo.yaml'),
                Path('.graphite-agent/config/repo.yml'),
                Path('config/repo.yaml')
            ]:
                if candidate.exists():
                    config_path = candidate
                    break
            else:
                config_path = None
        
        if config_path and config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                ctx.config = config
            except ImportError:
                # PyYAML not installed, try with json
                if config_path.suffix in ['.json']:
                    with open(config_path, 'r') as f:
                        ctx.config = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
        
        return ctx

    def get_stage_status(self, stage: str) -> dict:
        """Get the status of a specific pipeline stage."""
        stage_files = {
            'discover': ['repo_inventory.json', 'replay_risk.json', 'replay_validation.json'],
            'analyse': ['analysis_snapshot.json'],
            'triage': ['target_matrix.json', 'root_health.json', 'stack_order.json', 
                      'triage_packets.json', 'question_queue.json'],
            'plan': ['execution_plan.json', 'command_plan.json'],
            'validate': ['checklist_report.json'],
            'execute': []
        }
        
        files = stage_files.get(stage, [])
        completed = []
        missing = []
        
        for f in files:
            path = self.latest_dir / f
            if path.exists():
                completed.append(f)
            else:
                missing.append(f)
        
        return {
            'stage': stage,
            'completed': completed,
            'missing': missing,
            'is_complete': len(missing) == 0
        }
