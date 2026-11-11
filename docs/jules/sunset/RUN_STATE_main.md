# PR Audit Report

### Baseline Measurement
Command: `python -m pytest`
Exit Code: 2 (Collection errors)
Collected: 162 items
Errors: 2 (`tests/test_dispatcher.py`, `tests/test_manifest.py`)
Details: `ImportError: cannot import name 'Provider' from 'dspy_helm.providers.base'` is pre-existing on `main`.

### PR Verdicts

| PR  | Head SHA | Base SHA | Lines Changed | Markers | Commits Ahead | Verdict |
|-----|----------|----------|---------------|---------|---------------|---------|
| 64 | fe1072a15faac12621cd423e8cab627458a8d115 | 64de601b | 7 files changed | 0 | 2 | CONFLICT |
| 63 | 6af4da98030c58fe1782097c9f3419d69f42b204 | 64de601b | 31 files changed | 0 | 3 | CONFLICT |
| 62 | 5ba17a0589776a62350b8b9b38fb93e23052aad1 | 64de601b | 40 files changed | 0 | 17 | CONFLICT |
| 61 | 9e4b36b51f3a7af9a982a571aadbd1e69844284c | 64de601b | 149 files changed | 0 | 3 | CONFLICT |
| 60 | 9c353325eafb6824c31d1e3897386a22c661a403 | 17930fe2 | 24 files changed | 0 | 2 | CONFLICT |
| 59 | 93a59383581d95daec1d262624a28e219f1bf6b4 | 64de601b | 2 files changed | 0 | 2 | RED* |
| 56 | 87ee4d4a3926b7aeaaabf9838aa2a82b21973c4f | 9205e343 | 15 files changed | 0 | 8 | CONFLICT |
| 55 | e061ab1a5fcfc2a3613f9c35f51996edf7a3e306 | c87ca7a3 | 27 files changed | 0 | 6 | CONFLICT |
| 53 | 6efd18438551afc0f1d0ce8ceda3174431bbf6a1 | 29556659 | 50 files changed | 0 | 6 | CONFLICT |
| 52 | e333ff5731eebbe6c0e6d91eb7ba1c6fca5cd30c | 0c732a17 | 111 files changed | 0 | 2 | CONFLICT |
| 51 | 53026024f62a483cd19081f18e90b94c92d393c5 | 4fe38b97 | 4 files changed | 0 | 7 | CONFLICT |
| 50 | 5b3dd52f8437cf6ca852912303c6eca7d5e147f4 | eeb0b42e | 110 files changed | 0 | 6 | CONFLICT |
| 49 | 1fdf3e631fddb30ac10654f84664084831331db9 | eeb0b42e | 17 files changed | 0 | 4 | CONFLICT |
| 48 | 15de6113295cd7d8850b784f67b8e86f16a2d4d1 | eeb0b42e | 114 files changed | 0 | 4 | CONFLICT |
| 47 | cb310394ed9dce16b48c09abfead5e86001344eb | eeb0b42e | 5 files changed | 0 | 6 | CONFLICT |
| 46 | 0607201deae134bd497539c93c78a85967f19bb1 | eeb0b42e | 6 files changed | 0 | 7 | CONFLICT |
| 37 | fe8a3061bf5f06a256bee5e0f1d2ecd71367c546 | d0ff842f | 52 files changed | 2 | 8 | CONFLICT |
| 35 | 252e93364b3c3340c4192ae52e9f0e6445a87344 | d0ff842f | 61 files changed | 0 | 7 | CONFLICT |
| 33 | c7ee12056ca13df48413c41d9dfc8d20abfe15a6 | d0ff842f | 6 files changed | 0 | 7 | CONFLICT |
| 26 | 28d0d74ea30a60839c32f97585e76f8d7197de07 | 64de601b | 7996 files changed | 572 | 2 | RED* |

*\* PRs 59 and 26 result in the exact same RED collection errors as the baseline on `main`, but still fail the suite test.*

### Conclusion
The CLEAN-GREEN set is empty. No PRs can be merged at this time.
