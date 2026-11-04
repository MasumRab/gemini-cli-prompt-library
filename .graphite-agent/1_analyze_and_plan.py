#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent.resolve()
analyse_script = script_dir / "tools" / "analyse.py"
subprocess.run([sys.executable, str(analyse_script)], check=True)
