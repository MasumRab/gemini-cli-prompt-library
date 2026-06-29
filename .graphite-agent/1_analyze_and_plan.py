#!/usr/bin/env python3
import subprocess
import shutil
import sys

python_exec = shutil.which("python") or sys.executable
# sourcery skip: command-injection
subprocess.run([python_exec, ".graphite-agent/tools/analyse.py"], check=True)
