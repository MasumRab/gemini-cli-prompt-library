#!/usr/bin/env python3
"""
Execution Engine for Graphite Agent V8

Handles execution of Graphite commands and operations.
This is a STUB implementation for V8 completion.
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Any
from lib.run_context import RunContext


class Executor:
    """Executes Graphite commands."""
    
    def __init__(self, ctx: Optional[RunContext] = None):
        self.ctx = ctx or RunContext()
        self.dry_run = True  # defaults to dry run for safety
    
    def set_dry_run(self, dry_run: bool = True):
        """Set dry run mode."""
        self.dry_run = dry_run
    
    def execute_command(self, command: str) -> dict:
        """Execute a single Graphite command."""
        if self.dry_run:
            return {
                "status": "dry_run",
                "command": command,
                "message": "Would execute (dry run mode)"
            }
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return {
                "status": "pass" if result.returncode == 0 else "error",
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {
                "status": "error",
                "command": command,
                "error": str(e)
            }
    
    def execute_plan(self, plan_path: Optional[Path] = None) -> dict:
        """Execute a command plan."""
        if plan_path is None:
            plan_path = self.ctx.latest_dir / 'command_plan.json'
        
        if not plan_path.exists():
            return {
                "status": "error",
                "error": f"Command plan not found: {plan_path}"
            }
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        commands = plan.get('commands', [])
        results = []
        
        for cmd_info in commands:
            if isinstance(cmd_info, dict):
                command = cmd_info.get('command', '')
            else:
                command = str(cmd_info)
            
            result = self.execute_command(command)
            results.append(result)
            
            if result.get('status') == 'error' and not self.dry_run:
                # Stop on first real error
                break
        
        return {
            "status": "pass" if all(r.get('status') != 'error' for r in results) else "error",
            "executed": len(results),
            "results": results,
            "message": f"Executed {len(results)} commands in {'dry run' if self.dry_run else 'live'} mode"
        }
    
    def check_prerequisites(self) -> dict:
        """Check execution prerequisites."""
        checks = []
        
        # Check if we're in a valid git repo
        try:
            subprocess.run(['git', 'status'], capture_output=True, check=True)
            checks.append({"check": "git_repo", "status": "pass"})
        except:
            checks.append({"check": "git_repo", "status": "fail", "error": "Not a git repository"})
        
        # Check if Graphite CLI is available
        try:
            subprocess.run(['gt', '--version'], capture_output=True, check=False)
            checks.append({"check": "graphite_cli", "status": "pass"})
        except:
            checks.append({"check": "graphite_cli", "status": "warning", "error": "Graphite CLI not found"})
        
        # Check validation status
        validation_status = self.ctx.get_stage_status('validate')
        checks.append({
            "check": "validation_complete",
            "status": "pass" if validation_status.get('is_complete') else "warning"
        })
        
        return {
            "status": "pass" if all(c.get('status') == 'pass' for c in checks) else "warning",
            "checks": checks,
            "can_execute": all(c.get('status') != 'fail' for c in checks)
        }


def create_executor(ctx: Optional[RunContext] = None) -> Executor:
    """Create a new executor."""
    return Executor(ctx)
