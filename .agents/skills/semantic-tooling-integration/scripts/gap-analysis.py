#!/usr/bin/env python3
"""Dependency scanner for semantic tooling integration

This script analyzes a project to identify which semantic tools are missing
and generates recommendations for installation.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and return stdout, stderr, and return code."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def check_dependency(name):
    """Check if a dependency is installed."""
    cmd = ["python", "-c", f"import {name}"]
    stdout, stderr, rc = run_command(cmd)
    return rc == 0


def find_language_servers():
    """Check for LSP servers that would be needed for semantic analysis."""
    # This is simplified - in practice would check for pygls, pylsp, etc.
    return ["pygls", "lsp-py", "vscode-languageserver"]


def analyze_project(project_path):
    """Analyze a project for semantic tooling gaps."""
    project_path = Path(project_path).resolve()
    print(f"Analyzing project: {project_path}")

    gaps = []

    # Check for Tree-sitter
    if not check_dependency("tree_sitter"):
        gaps.append("Missing Tree-sitter dependency")

    # Check for LSP servers
    for server in find_language_servers():
        if not check_dependency(server):
            gaps.append(f"Missing LSP server: {server}")

    # Check for AST utilities
    if not check_dependency("ast"):
        gaps.append("Missing AST utilities")

    return gaps


def main():
    if len(sys.argv) != 2:
        print("Usage: python dependency_scanner.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    gaps = analyze_project(project_path)

    if gaps:
        print("Semantic tooling gaps found:")
        for gap in gaps:
            print(f"  - {gap}")
        sys.exit(1)
    else:
        print("No semantic tooling gaps detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
