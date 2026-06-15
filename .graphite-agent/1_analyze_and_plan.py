#!/usr/bin/env python3
import subprocess
from pathlib import Path

# If a V6.4 analyser exists elsewhere, keep using it. This wrapper is intentionally non-destructive.
if Path(".graphite-agent/tools/analyse.py").exists():
    subprocess.run("python .graphite-agent/tools/analyse.py", shell=True, check=True)
