#!/usr/bin/env python3
import subprocess

# sourcery skip: command-injection
subprocess.run("python .graphite-agent/tools/analyse.py", shell=True, check=True)
