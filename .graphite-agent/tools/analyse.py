#!/usr/bin/env python3
import subprocess
from pathlib import Path
from agent_core import run_diagnostics

# Preserve V6.4 analyser if present, then add V7 diagnostics.
if Path(".graphite-agent/1_analyze_and_plan.py").exists():
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    # sourcery skip: command-injection
    subprocess.run(
        "python .graphite-agent/1_analyze_and_plan.py", shell=True, check=True
    )
print(run_diagnostics(write=True)["summary"])
