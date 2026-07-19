# Multi-Repo Tools for Jules

These tools are designed to manage Jules sessions that span across multiple repositories.

## Scripts

### `jules_multi_repo.py`
Analyzes multiple repository paths to provide a high-level summary of code changes and consistency.

**Usage:**
```bash
python3 -m tools.multi_repo.jules_multi_repo /path/to/repo1 /path/to/repo2
```

### `check_all_repos.sh`
A wrapper script that runs analysis on a predefined list of repositories.

**Usage:**
```bash
./tools/check_all_repos.sh
```

## Best Practices
- Ensure all repositories are on the same base branch (usually `main`) before starting.
- Use `jules_multi_repo.py` to verify that Jules hasn't introduced inconsistent patterns across different codebases.
