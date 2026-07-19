# Sentinel Security Journal

This document records critical security learnings, reusable patterns, unexpected side effects, and blockers discovered during Sentinel operations within this specific codebase.

## 2024-XX-XX: Command Injection via Subprocess with shell=True in Script Utilities

*   **Vulnerability Discovered:** Several maintenance scripts (`intelligent_merge_analyzer.py`, `path_change_detector.py`, `intelligent_merger.py`, `branch_rename_migration.py`) used `subprocess.run(cmd, shell=True)` with string interpolation for git commands containing branches or paths. While primarily used for internal maintenance, this pattern creates a high risk of command injection if run on unsanitized inputs (e.g., malformed branch names or paths).
*   **Learning:** Codebase scripts rely heavily on shell calls to perform Git operations. These need to be consistently enforced to use `shell=False` and pass arguments as lists to the subprocess module to leverage the implicit safety of `execve`.
*   **Prevention Note:** Do not use `shell=True` unless absolutely necessary (e.g., chained pipes, shell built-ins). When calling git operations inside scripts or other utilities, always construct the command as a list of arguments `["git", "branch", ...]` and pass to `subprocess` with `shell=False`.
