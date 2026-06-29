#!/usr/bin/env python3
import subprocess
import shutil
import sys

# sourcery skip: command-injection
python_exec = shutil.which("python") or sys.executable
subprocess.run([python_exec, ".graphite-agent/tools/analyse.py"], check=True)
