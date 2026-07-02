#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent.resolve()
execute_script = script_dir / "tools" / "execute_approved.py"
subprocess.run([sys.executable, str(execute_script)], check=True)
