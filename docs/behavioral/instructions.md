# Instructions for Jules

> This file governs how Jules operates in this repository. Read it fully before
> making any changes.

---

## Memory Overrides

The following statements in your context memory are **false** or **stale**. Do not act on them. Use the correct behaviour listed in the table below instead.

| Stale Memory Statement | Correct Behaviour |
|-----------------------|-------------------|
| "Verification tests... can be implemented by mocking missing modules... in `sys.modules` before importing" | **False.** Module-level mocking pollutes the pytest session and breaks unrelated tests. You must use `setUp`/`tearDown` (or `setUpClass`/`tearDownClass`) and explicitly restore/pop the mock to prevent test leakage. |
| "The older `kaggle_forensics` module is an earlier generation and should generally be left untouched." | **False.** `kaggle_forensics` is current, actively maintained, and strictly required at every pipeline phase. It provides `ErrorWorkflow` and the forensic analysis layer. It is complementary to `kaggle-qa-toolkit`. |
| "Ensure determinism by explicitly seeding random number generators (e.g., `np.random.default_rng(42)`)." | **Contextual.** During migration, **never change existing seeds**. If a notebook uses legacy `np.random.seed(42)`, keep it. For *new* utility/test code you write yourself, use the modern `default_rng(42)` API. |
| "The project uses `uv` for dependency management... install dependencies with `uv pip install`" | **Contextual.** Locally (your dev environment), use `uv pip install -e tools/kaggle-qa-toolkit -e tools/kaggle_forensics` and run commands via `uv run`. However, the CI (GitHub Actions) uses bare `pip`. Do not use bare `pip` locally, but don't break CI configurations. |

---

## Required Reading (in order)

1. **`AGENTS.md`** — Mandatory workflow for all agents: decision tree, phase
   sequencing, exit code contracts, multi-agent coordination rules, and
   code modification rules. **This is the authoritative workflow reference.**

2. **`CONTRIBUTING.md`** — 12 acceptance criteria (AC1–AC12) that every PR
   must satisfy. Covers directory structure, metadata schemas, linting,
   secrets scanning, output stripping, and platform-detection patterns.

3. **`TOOL-REGISTRY.md`** — Maps every tool to its pipeline phase, CLI
   invocation, exit codes, and dependencies. Use this to find the right
   tool for any task. *(If this file does not exist yet, use the phase
   reference below and CLAUDE.md for tool commands.)*

4. **`ML-CODING-STANDARDS.md`** — Required ML coding patterns: seed
   management, train/test split discipline, leakage prevention, model
   serialization, early stopping, evaluation metrics, and Kaggle resource
   constraints. *(If this file does not exist yet, follow the inline
   standards below.)*

---

## Critical Rules

These are non-negotiable. Violating any of these invalidates your work.

### Pipeline Rules
- **Never skip Phase 0 forensics** on any notebook — there is no "small change" exception
- **Never run Phase 5 quality gates before Phase 4 calibration exits 0**
- **Never call `model.predict(data)` without `InferenceGuard.wrap()`** in deployment code
- **Never bypass an `EnforcementError`** — fix the data instead
- **Never change model architectures, random seeds, or data split ratios** during migration
- **Never combine multiple migration phases in one commit** — one phase per commit per slug

### QA Tool Rules
- Both QA packages must be installed before any work begins:
  ```bash
  uv pip install -e tools/kaggle-qa-toolkit
  uv pip install -e tools/kaggle_forensics
  ```
  *(Note: The CI environment uses bare `pip`, but you must use `uv pip` locally).*
- Verify with: `uv run kaggle-qa --help` and
  `uv run python -c "from kaggle_forensics.workflows.error_workflow import ErrorWorkflow; print('ok')"`
- If either fails, **stop all work** until resolved

### Code Modification Rules
- **Preserve-by-default** — Do not remove any line of code unless you can explain
  why it is dead code (unreachable, no callers, no importers). Code that looks
  unused may have downstream importance: test fixtures, dynamic imports,
  monkey-patching, CI references, or conditional paths.
- **No silent simplification** — Do not "clean up" or "simplify" code you are
  not explicitly asked to modify.
- **Explain every deletion** — If you remove code, the commit message must
  explain why the code was dead or unnecessary.
- **One concern per commit** — Each commit addresses exactly one change.
- **Run diff review** — Before committing, review the full diff. If any lines
  were removed that you did not intentionally target, undo those changes.
- **No changing signatures without updating callers** — If you change a function
  signature, update every caller.

### Known Anti-Patterns (from prior PR reviews — DO NOT REPEAT)

**Shell scripts:**
- Always start with `set -euo pipefail`
- Never use untrusted download mirrors (use official sources only)
- Pin dependency versions — never use `/latest/` URLs
- Use current LTS versions (Node.js 20, not 18 which is EOL)
- Always install QA tools (`uv pip install -e tools/kaggle-qa-toolkit` and
  `uv pip install -e tools/kaggle_forensics`) with verification

**File formats:**
- Never wrap config files (`.gitignore`, `.env`, `requirements.txt`) in
  markdown code fences — these are not markdown files
- Never remove `.kaggle/` or `data/` from `.gitignore` — credentials and
  large datasets must never be committed
- Read existing config files before overwriting — preserve all entries

**ML / Data Science:**
- Never call `fit_transform()` on test/inference data — fit on train only,
  then use `.transform()` for test data.
- **Never apply stateful transformers to the full dataset before cross-validation.**
  `PowerTransformer`, `RobustScaler`, `StandardScaler`, and any other stateful
  sklearn transformer must live *inside* a `sklearn.pipeline.Pipeline` so that
  `cross_val_score` refits them on each fold's training split. Fitting outside
  CV leaks validation-fold statistics into training, inflating scores:
  ```python
  # WRONG — leaks validation statistics:
  pt = PowerTransformer()
  X_transformed = pt.fit_transform(X)   # sees all folds
  scores = cross_val_score(model, X_transformed, y, cv=kf)

  # RIGHT — transformer is inside Pipeline, refitted per fold:
  from sklearn.pipeline import Pipeline
  from sklearn.compose import ColumnTransformer
  preprocessor = ColumnTransformer([
      ("power", PowerTransformer(method="yeo-johnson"), skewed_cols),
      ("passthrough", "passthrough", other_cols),
  ])
  pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])
  scores = cross_val_score(pipeline, X, y, cv=kf)
  ```
- Never leave one-off repair/debug scripts in commits — delete before committing.

**Testing:**
- Never mock at module level (`sys.modules[...] = ...`) — use `setUp`/`tearDown`
  to install and restore mocks around each test method. Module-level replacement
  persists for the entire pytest session and poisons unrelated fixtures.
  Correct pattern:
  ```python
  def setUp(self):
      self._real_pandas = sys.modules.get('pandas')
      sys.modules['pandas'] = MagicMock()
  def tearDown(self):
      if self._real_pandas is not None:
          sys.modules['pandas'] = self._real_pandas
      else:
          sys.modules.pop('pandas', None)
  ```
- If the module under test uses **lazy imports** (`import pandas as pd` inside a
  function body, not at module top), the mock must be active at *call time*, not
  just at import time — setUp/tearDown handles this correctly.
- Test ALL code paths you protect — if you block `.pkl` and `.pickle`, test both.
- **No tautological assertions** — `assert len({"a", "b"}) == 2` always passes
  and validates nothing. Every assertion must depend on data produced by the code
  under test.
- **Verify golden fixture keys before accessing nested values** — golden fixtures
  have a defined schema; check the actual key names before writing tests. In this
  repo, `submission` records store `id_col` / `target_col`, not `columns`:
  ```python
  # WRONG:
  assert set(lanl_golden['submission']['columns']) == {'seg_id', 'time_to_failure'}
  # RIGHT:
  assert lanl_golden['submission']['id_col'] == 'seg_id'
  assert lanl_golden['submission']['target_col'] == 'time_to_failure'
  ```

**Git / PRs:**
- Never overwrite files from main without diffing first.
- Run `git diff --stat` and `git diff` before every commit.
- **Always rebase on the latest `main` before pushing** — upstream fixes (e.g.
  the `test_security.py` mock teardown fix, the conftest pandas-3.x fix) must be
  picked up before CI runs. A branch that was green when created can fail after
  other PRs land.
- **`.gitignore` must include `**/*.egg-info/` and `**/build/`** — never commit
  build artefacts. If `git add -A` stages them, run
  `git rm -r --cached <path>` and add the pattern to `.gitignore`.

**Python packaging (`pyproject.toml` / `requirements*.txt`):**
- **Editable local installs:** use `file:./relative/path`, never
  `file://${PWD}/path` — shell variable expansion does not occur inside
  `pyproject.toml`, so `${PWD}` is treated as a literal string and `pip install`
  will fail.
- **`pytest` is a dev/test dependency, not a runtime dependency.** Put it in
  `[project.optional-dependencies] test = ["pytest>=7.0"]`, not under
  `[project] dependencies`. Listing it as a runtime dep means every user of the
  package pulls in pytest unnecessarily.
- **Never add upper-bound version pins (`<X.Y`) to shared requirements files
  without a concrete reason.** A `pandas<3.0.0` cap blocks all consumers from
  upgrading and is a regression if added to fix a test-infrastructure bug rather
  than a real incompatibility.

---

## Behavioral Rules

### When to ask vs. when to act

1. **Default to action when the prompt is explicit** — if the prompt says
   "fix any discrepancies found", fix them directly. Do not ask permission
   to fix something the prompt already told you to fix.
2. **Questions are welcome for genuinely ambiguous decisions** — if the prompt
   leaves multiple equally valid approaches and the consequences of choosing
   wrong are significant, ask. But before asking, check whether the answer
   is already in the repository docs (this file, AGENTS.md, CONTRIBUTING.md,
   TOOL-REGISTRY.md, ML-CODING-STANDARDS.md).
3. **Do not ask questions the prompt already answers** — if the prompt says
   "verify cross-references" and you wonder *how* to verify them, read the
   referenced files and compare. The method is implied by the task.

### Common decisions — pre-answered

These are decisions that come up often. Follow the defaults below unless the
prompt explicitly says otherwise:

- **Where to document changes:** In the commit message and the PR description.
  Do not create new markdown files unless the prompt asks for one.
- **How to determine if a script is COMPLETE vs PARTIAL:** A script is PARTIAL
  if it contains `pass`, `TODO`, `raise NotImplementedError`, `...` (ellipsis
  as placeholder), or if key functions have empty bodies. Otherwise it's COMPLETE.
- **If instructions overlap between files:** `.jules/INSTRUCTIONS.md` rules are
  a superset of `AGENTS.md` rules. If `AGENTS.md` has a rule not in this file,
  follow it. If this file has a stricter version, follow this file.
- **If you find errors in config files:** Fix them directly in your PR. Config
  files (`.pre-commit-config.yaml`, CI YAML, `.gitignore`) should be correct.
  Do not ask permission to fix a syntax error or a missing hook.
- **If you're unsure which QA tool to use:** Check the "Using QA Tools in
  Your Workflow" section below. It has the full decision tree.

### General behavior

4. **Use repository conventions** — if you need to decide a file name, format,
   or location, look at what already exists in the repo and follow that pattern.
5. **Document decisions in commit messages** — if you made a judgment call,
   explain it in the commit message so reviewers understand your reasoning.
6. **Use QA tools to validate your own work** — do not rely on manual review
   alone. Run forensics, calibration, and gates to catch issues before pushing.
   See "Using QA Tools in Your Workflow" below.
7. **Read before writing** — before creating or overwriting any file, read the
   existing version first. Use `git diff` to verify your changes don't
   accidentally remove content you didn't intend to touch.
8. **Augment your work with forensics and QA** — the tools in `tools/` are
   not just for the migration pipeline. Use them as part of your development
   workflow to catch issues early. See the next section for specific patterns.

---

## Using QA Tools in Your Workflow

The QA tools are not just for the migration pipeline — **they are your primary
development aids**. Use them proactively in every task, not just when a prompt
tells you to. They catch issues that manual review misses: data leakage,
silent metric regressions, schema violations, and unreliable pipeline stages.

**Rule of thumb:** If you're about to touch a notebook, run forensics first.
If you're about to push code, run the QA pipeline. If something fails
silently, use SilentFailureDetector. These tools exist to make your work
higher quality — treat them as your safety net.

### Before touching any notebook

Run forensics first to understand what you're working with:
```bash
uv run kaggle-qa analyze <notebook.ipynb> \
    -o qa_reports/<slug>/forensic.md --json qa_reports/<slug>/forensic.json
```

Read `forensic.json` before making changes:
- `toxicity.total_score` — if > 20, flag to user before proceeding
- `original_bugs` — these are pre-existing bugs, not your responsibility to fix
  (but document them in `analysis/<slug>/BUGS.md`)
- `lifecycle` — variable read/write tracking helps you understand data flow
- `reliability_score` — low scores mean the notebook is fragile; extra caution needed

### When writing or modifying pipeline code

Wrap every pipeline stage in ErrorWorkflow — this gives you automatic error
classification, checkpointing, and diagnostic context if something fails:
```python
from kaggle_forensics.workflows.error_workflow import ErrorWorkflow, MismatchDetector

with ErrorWorkflow("preprocessing", cell_idx=3, reliability_score=0.82) as stage:
    df = preprocess(raw_df)
    stage.checkpoint("after_imputation", df)

    # Validate intermediate state
    MismatchDetector.check_shape(tensor, expected=(224, 224, 3), stage="image_load")
    MismatchDetector.check_distribution(df["score"], expected_range=(0, 1), stage="scoring")
```

### When writing feature engineering or preprocessing

Use leakage detectors to catch train/test contamination:
```python
from kaggle_forensics import TimeseriesLeakageDetector, StaticLeakageAnalyzer

# Runtime check: does this feature use future data?
leak_detector = TimeseriesLeakageDetector()
leaks = leak_detector.check(df, time_col="date", target_col="sales")

# Static check: AST-level analysis of a notebook
static = StaticLeakageAnalyzer()
static_leaks = static.analyze("notebooks/rossmann/rossmann-pipeline.ipynb")
```

### When modifying or creating schemas

Always recalibrate after schema changes:
```bash
uv run kaggle-qa adversarial schemas/<slug>_master_schema.json \
    --output-dir qa_reports/<slug>/adversarial/
```

Check the exit code:
- **Exit 0** — guards are calibrated, proceed
- **Exit 2** — FN detected (guards are missing violations). Fix the schema, re-run.
- Review `guard_patch.py` for recommended guard relaxations (FP reduction)

### When predictions look wrong but no error is thrown

Use silent failure detection:
```python
from kaggle_qa import SilentFailureDetector

detector = SilentFailureDetector()
issues = detector.check_prediction_drift(old_preds, new_preds)
subgroup = detector.check_subgroup_collapse(pred_df, group_col="anatom_site")
```

### Before pushing any PR

Run the full QA pipeline to validate end-to-end:
```bash
# Via the bridge script (simplest)
uv run python scripts/qa_integration.py full-run <slug>

# Or via the CLI directly
uv run kaggle-qa run \
    --schema schemas/<slug>_master_schema.json \
    --notebook notebooks/<slug>/kaggle/02-training.ipynb \
    --policy correct \
    --output-dir qa_reports/<slug>/
```

Exit 0 or 5 = safe to push. Exit 4 = do not push, fix first.

### When enforcing data quality at inference

Wrap every `model.predict()` with InferenceGuard:
```python
from kaggle_qa.enforcement import InferenceGuard, EnforcementPolicy
from kaggle_qa import MasterSchemaDocument

schema = MasterSchemaDocument.load(f"schemas/{slug}_master_schema.json")
guard = InferenceGuard(schema, policy=EnforcementPolicy.CORRECT)
safe_predict = guard.wrap(model.predict)

# safe_predict auto-validates, corrects, and audits
predictions, report = safe_predict(input_data)
if not report.clean:
    print(report.summary_lines())  # shows what was corrected
```

### Quick reference: QA bridge commands

```bash
# Phase 0: forensics + schema bootstrap
uv run python scripts/qa_integration.py pre-migrate <notebook.ipynb> <slug>

# Phase 4: adversarial calibration after schema tuning
uv run python scripts/qa_integration.py post-extract <slug>

# Phases 0-5: full pipeline (CI/CD gate)
uv run python scripts/qa_integration.py full-run <slug>

# Anytime: enforce schema on data before prediction
uv run python scripts/qa_integration.py enforce <slug> <data.json> --policy correct

# Anytime: check enforcement drift over time
uv run python scripts/qa_integration.py drift-check <slug>
```

---

## Pipeline Phase Reference

Every notebook goes through all 7 phases in order. No phase can be skipped.

| Phase | Name | Command | Exit Codes |
|-------|------|---------|------------|
| 0 | Forensics | `kaggle-qa analyze <nb> -o report.md --json report.json` | 0=pass, >0=review |
| 0 | Schema Bootstrap | `kaggle-qa bootstrap <nb> <slug> -o schema.json` | 0=pass |
| 1 | Analysis | `python scripts/notebook_analyzer.py analyze <nb>` | — |
| 2 | Extraction | `python scripts/notebook_extractor.py extract <nb>` | — |
| 3 | Planning | `python scripts/build_planned_notebooks.py --competition <slug>` | — |
| 4 | Calibration | `kaggle-qa adversarial schemas/<slug>_master_schema.json` | 0=pass (FP non-blocking), **2=FN (STOP)** |
| 5 | Quality Gates | `kaggle-qa run --schema <s> --notebook <n> --policy correct` | 0=pass, **4=FAIL**, 5=warn |
| 6 | Deployment | `python scripts/consolidate_notebooks.py --competition <slug>` | — |

**Master orchestrator** (runs all phases in sequence):
```bash
uv run python scripts/run_pipeline.py <slug> --notebook analysis/<slug>/<notebook>.ipynb
```

### Exit Code Contract

| Code | Meaning | Required Action |
|------|---------|----------------|
| `0` | Clean pass | Proceed to next phase |
| `1` | Violations corrected/warned | Review report, proceed |
| `2` | **Adversarial FN — guards missing** | Fix schema, re-run Phase 4. DO NOT proceed. |
| `3` | Enforcement RAISE triggered | Fix data, do not bypass |
| `4` | **Pipeline FAIL** | Fix gates, re-run from Phase 4 |
| `5` | Pipeline WARN | Document warnings, proceed with caution |

---

## Required Outputs Per Phase

Before claiming any phase is complete, verify these files exist:

| Phase | Required Outputs |
|-------|-----------------|
| 0 | `qa_reports/<slug>/forensic.md`, `qa_reports/<slug>/forensic.json`, `schemas/<slug>_master_schema.json` |
| 1 | `analysis/<slug>/HAZARDS.md` (if HIGH hazards found) |
| 2 | `analysis/<slug>/EXTRACTED_CODE.md` |
| 3 | Planned notebooks in `notebooks/` |
| 4 | `qa_reports/<slug>/adversarial/calibration_report.json` (exit 0) |
| 5 | `qa_reports/<slug>/pipeline_result.json` (`"status": "PASS"`) |
| 6 | Final notebooks in `notebooks/<slug>/kaggle/` |

---

## Mandatory Code Patterns

### ErrorWorkflow (required for every pipeline stage)
```python
from kaggle_forensics.workflows.error_workflow import ErrorWorkflow

with ErrorWorkflow("stage_name", cell_idx=N) as stage:
    result = run_stage(data)
    stage.checkpoint("after_stage", result)
```

### InferenceGuard (required for every model.predict in deployment)
```python
from kaggle_qa.enforcement import InferenceGuard, EnforcementPolicy
from kaggle_qa import MasterSchemaDocument

schema = MasterSchemaDocument.load(f"schemas/{slug}_master_schema.json")
guard = InferenceGuard(schema, policy=EnforcementPolicy.CORRECT)
safe_predict = guard.wrap(model.predict)
predictions, report = safe_predict(input_data)
```

---

## Project-Specific API Facts

These are hard-won facts about this repo's internal tools. Get them wrong and
tests or the pipeline will fail silently.

### `MasterSchemaDocument`

```python
# Constructor takes competition_name as a positional str — NOT a dict
doc = MasterSchemaDocument(competition_name="house-prices")   # CORRECT
doc = MasterSchemaDocument({"competition": "house-prices"})   # WRONG — TypeError

# load() reads the JSON and calls cls(data["competition"])
doc = MasterSchemaDocument.load("schemas/house-prices_master_schema.json")

# to_dict() serialises competition_name under the key "competition"
d = doc.to_dict()
assert d["competition"] == "house-prices"
```

### `TabularFeature` — enum fields

`TabularFeature.missing_policy` and `.transform` are **enum** instances
(`MissingPolicy`, `TransformRule`), not strings. When constructing a
`TabularFeature` from raw JSON (where these fields are strings), convert them
first:

```python
from kaggle_qa.schema import MissingPolicy, TransformRule

def tabular_feature_from_dict(d: dict) -> TabularFeature:
    f = dict(d)
    f["missing_policy"] = MissingPolicy(f["missing_policy"])
    f["transform"] = TransformRule(f["transform"])
    return TabularFeature(**f)
```

`MasterSchemaDocument.load()` already does this internally. Only apply the
conversion when constructing `TabularFeature` objects directly from raw dicts
(e.g. in tests that bypass `load()`).

### Golden output fixture schema

Golden JSON files live in `golden_outputs/` (project root, **not**
`scripts/tests/golden_outputs/`). The `submission` object stores:

```json
{
  "submission": {
    "id_col":     "seg_id",
    "target_col": "time_to_failure",
    "shape":      [2624, 2],
    ...
  }
}
```

There is **no** `columns` key — use `id_col` and `target_col`.

### Platform Detection (required for all data paths)
```python
import os, pathlib

ON_KAGGLE = os.path.exists('/kaggle/input')
if ON_KAGGLE:
    DATA_DIR = pathlib.Path('/kaggle/input/<competition-slug>')
else:
    DATA_DIR = pathlib.Path('data/<competition-slug>')
```

### Random Seed (required at top of every notebook/script)
```python
import random, numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
# Add torch.manual_seed(SEED) / tf.random.set_seed(SEED) if applicable
```

---

## Acceptance Criteria (AC1–AC12)

Every PR must pass all 12 criteria from `CONTRIBUTING.md`:

| AC | Check | How to Validate |
|----|-------|-----------------|
| AC1 | Correct path under `notebooks/` | Manual |
| AC2 | `metadata.yaml` valid | `uv run python scripts/validate_notebook.py --path notebooks/<slug>` |
| AC3 | `datasets.yaml` valid | Same validator |
| AC4 | `requirements.txt` present | Same validator |
| AC5 | Notebook outputs stripped | Same validator |
| AC6 | Passes `nbqa ruff` lint | CI: `ci-pr-validation.yml` |
| AC7 | No secrets in cells | CI: `detect-secrets` |
| AC8 | No hardcoded absolute paths | Same validator (allows platform guard pattern) |
| AC9 | Executes in CI | CI: `ci-notebooks.yml` |
| AC10 | `inventory/migration-mapping.csv` updated | Manual |
| AC11 | Kaggle source URL in `metadata.yaml` | AC2 check |
| AC12 | PR approved by maintainer | GitHub review |

## Multi-Agent Coordination Rules

When multiple agents work on this repository simultaneously:

1. **One agent per competition slug** — no concurrent work on the same `<slug>`
2. **Schema ownership** — the agent that runs Phase 0 owns the schema until Phase 5 completes
3. **Phase atomicity** — one commit per phase per slug. Never batch multiple phases in one commit
4. **No phase skipping** — if a previous phase output is missing, re-run that phase before continuing
5. **Calibration invalidation** — if another agent modifies `schemas/<slug>_master_schema.json`, your Phase 4 result is stale. Re-run Phase 4.

---

## Directory Structure

```
kaggle-notebook-analysis/
├── tools/
│   ├── kaggle-qa-toolkit/           # QA enforcement, calibration, pipeline
│   └── kaggle_forensics/            # Forensic analysis, ErrorWorkflow
├── scripts/                         # Pipeline scripts (phases 0-6)
│   ├── run_pipeline.py              # Master orchestrator
│   ├── qa_integration.py            # QA bridge
│   └── tests/                       # Golden output tests
├── schemas/                         # Per-competition data contracts
├── qa_reports/                      # QA output (forensic, adversarial, pipeline)
├── analysis/                        # Source notebooks + analysis artifacts
├── notebooks/<slug>/
│   ├── local/                       # Development tier
│   └── kaggle/                      # Deployment tier
├── lib/                             # Shared utilities (config, loaders, metrics)
├── AGENTS.md                        # Agent workflow (THIS IS AUTHORITATIVE)
├── CONTRIBUTING.md                  # Acceptance criteria
└── .github/workflows/               # CI/CD
```

## Known Anti-Patterns

- **Ignoring Exit Codes:** Do not proceed if a phase tool returns a non-zero exit code (unless it's a documented warning).
- **Silent Failures:** Using `try...except` without logging or re-raising the error hides extraction bugs.
- **Over-Scraping:** Extracting unused variables clutters the pipeline and breaks dependencies.

## Behavioral Rules

- Ask clarifying questions when requirements are ambiguous.
- Verify work after every modification.
- Always use the tools registry to find the right commands.
