# Clustering / Search-Analyse Process (from engine/branch_clustering.py blob a899049affa, 12211 bytes)

## Stage One — parallel analyzers (run concurrently)
| Substage | Component | Signal | Weight |
|---|---|---|---|
| 21.1 | `CommitHistoryAnalyzer` (BranchAnalyzer.get_changed_files / git diff --name-only) | shared commits, common ancestors | **0.35** |
| 21.2 | `CodebaseStructureAnalyzer` | AST + LibCST semantic features (functions, classes, imports, docstrings, comments, structural/content hash) | **0.35** |
| 21.3 | `DiffDistanceCalculator` | structural churn / conflict-distance metrics | **0.30** |

Constants: `DEFAULT_SIMILARITY_SCORE = 0.5`, `MIN_BRANCH_AGE_DAYS = 1`,
`CLUSTERING_THRESHOLD = 0.25`. Optional deps (numpy/scipy, libcst) degrade gracefully
(`HAS_SCIENTIFIC`, `HAVE_LIBCST` flags) — clustering still runs.

## Stage Two — integrate
`BranchClusterer` (21.4): consumes 21.1–21.3, builds similarity matrix, produces semantic clusters.

## Stage Three — decide target
`IntegrationTargetAssigner` (21.5–21.6): emits, per branch:
```
target: "main" | "scientific" | "orchestration-tools" | "taskmaster"
confidence: 0..1
reasoning: "<natural-language>"
tags: ["<feature>", ...]
metrics: { files_changed:[...], imports:[...], ... }
```
Primary excluded from candidates: `main`, `scientific`, `orchestration-tools` (they are targets, not
clustered). `ClusterBranchesCommand` excludes them before calling `engine.execute(...)`.

## Stage Four — Natural Language Validation Layer (Validator, blob 2aa026faba)
`src/cli/commands/task/engine/validation_framework.py`:
- Conditions (`condition` block): `branch_contains`, `branch_not_contains`,
  `path_contains`, `has_tag`, `has_import`
- Assertions (`assert` block): `target`, `confidence_min`
- Each rule carries `name`, `label` (default `heuristic_proposed`), `provenance`.
- `Validator(rules_file).validate(clustering_results)` → **True only if every matching branch
  passes its assertion; any failure sets all_passed=False and the run aborts (`return 1`)**.

## I/O schema
### Input rules YAML (`clustering_rules.yaml`)
```yaml
rules:
  - name: "no_taskmaster_tooling_on_main"
    label: "arch_guard"
    provenance: "PRD-C4 / no-merge rule"
    condition: { branch_contains: "taskmaster", path_contains: "src/cli/commands/task" }
    assert: { target: "taskmaster", confidence_min: 0.7 }
  - name: "bolt_branches_are_noise"
    condition: { branch_contains: "bolt-" }
    assert: { target: "orchestration-tools", confidence_min: 0.0 }   # kept out of taskmaster sink
```
### Output JSON (`assignments.json`)
```jsonc
{
  "timestamp": <epoch>,
  "primary_branch": "origin/main",
  "mode": "hybrid",
  "assignments": {
    "feature/xyz": {
      "target": "taskmaster",
      "confidence": 0.82,
      "reasoning": "shared CommitHistory + structural similarity to src/cli/commands/task",
      "tags": ["cli", "submodule"],
      "metrics": { "files_changed": [...], "imports": [...] }
    }
  }
}
```
## Modes
`identification` (history fast scan) | `clustering` (full AST/LibCST) | `hybrid` (default:
identify then cluster ambiguous).

> Sparse. Cluster threshold (0.25) and weights (0.35/0.35/0.30) are read from source; Phase 2
> confirms no overrides were set via env/flags in the real runs.
