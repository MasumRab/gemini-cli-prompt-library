#!/usr/bin/env python3
"""
Graphite Agent Main CLI for V8

Main entry point for Graphite Agent operations.
This is a STUB implementation that delegates to main.py.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Delegate to main.py dispatcher."""
    # For backwards compatibility, delegate to main.py
    main_py = Path(__file__).parent / 'main.py'
    if main_py.exists():
        # Run main.py with same args
        cmd = [sys.executable, str(main_py)] + sys.argv[1:]
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    else:
        print("❌ main.py not found, cannot delegate")
        return 1


if __name__ == '__main__':
    sys.exit(main())
