# Master Task Overview - Parallel Execution Guide

**Version**: 1.0  
**Date**: January 18, 2026  
**Purpose**: Quick reference for parallel task execution

---

## Phase Overview

| Phase | Duration | Parallel Tracks | Total Tasks |
|-------|----------|-----------------|-------------|
| **Phase 2** | 2-3 days | 4 tracks (A, B, C, D) | 14 tasks |
| **Phase 3** | 3-4 days | 4 tracks (A, B, C, D) | 15 tasks |
| **Phase 4** | 2-3 days | 3 tracks (A, B, C) | 9 tasks |
| **Phase 5** | 1 day | 4 tracks (A, B, C, D) | 11 tasks |

---

## Parallel Execution Matrix

### Phase 2: Framework + Dispatcher

```
Track A: Structure        Track B: Dispatcher       Track C: CLI           Track D: Consolidation
─────────────────────     ─────────────────────     ──────────────────     ─────────────────────
2.1.1 __init__.py         2.2.1 registry.py         2.3.1 forgiving       2.4.1 move providers
2.1.2 providers/          2.2.2 dispatcher.py       2.3.2 robot mode       2.4.2 move optimizers
2.1.3 optimizers/         2.2.3 CLI integration     2.3.3 complete CLI     2.4.3 move evaluation
2.1.4 evaluation/                                    (depends on B)       2.4.4 move scenarios

                                                            ↓               2.4.5 move data
                                                      2.3.3 needs         2.4.6 update imports
                                                      2.2.2 & 2.2.3       (depends on all)
```

**Can run in parallel:**
- Track A (1-4) + Track B (1) + Track C (1-2) + Track D (1-5)
- Track B (2-3) after Track B (1)
- Track C (3) after Track B (2-3)
- Track D (6) after Track D (1-5)

**Est parallel time:** 2 days (vs 4 days sequential)

---

### Phase 3: UI + CASS + Interactive

```
Track A: UI              Track B: CASS             Track C: Approaches     Track D: Interactive
─────────────────────    ─────────────────────     ──────────────────     ─────────────────────
3.1.1 UI spec            3.2.1 hash_embedder       3.3.1 MIPROv2           3.4.1 session.py
3.1.2 menu.py            3.2.2 edge_ngram          3.3.2 Bootstrap         3.4.2 history.py
3.1.3 recommendation    3.2.3 vector_index        3.3.3 Custom            3.4.3 completer.py
3.1.4 progression       3.2.4 cass search         3.3.4 approach UI       3.4.4 full REPL
                         (depends on 3.2.1,2)                              (depends on A, B, C)
```

**Can run in parallel:**
- Track A (1-2) + Track B (1-2) + Track C (1-3) + Track D (1-3)
- Track A (3) after Track A (2)
- Track B (3) after Track B (1)
- Track B (4) after Track B (1-2)
- Track C (4) after Track C (1-3)
- Track D (4) after Track D (1-3)

**Est parallel time:** 2 days (vs 5 days sequential)

---

### Phase 4: Agentic Integration

```
Track A: Suggestions      Track B: Self-Correct     Track C: Integration
─────────────────────    ─────────────────────     ─────────────────────
4.1.1 suggester.py       4.2.1 self_correct.py     4.3.1 agent mode CLI
4.1.2 detection logic    4.2.2 error analysis      4.3.2 agent config
4.1.3 suggestion UI      4.2.3 prompt rewriting    4.3.3 agent docs
4.1.4 CLI integration    4.2.4 retry mechanism
                         (depends on 4.2.2-3)
```

**Can run in parallel:**
- Track A (1-3) + Track B (1) + Track C (1-2)
- Track A (4) after Track A (1-3)
- Track B (4) after Track B (2-3)
- Track C (3) after Track C (1-2)

**Est parallel time:** 1.5 days (vs 3 days sequential)

---

### Phase 5: Cleanup

```
Track A: Cleanup         Track B: Testing          Track C: Verification   Track D: Release
─────────────────────    ─────────────────────     ──────────────────     ─────────────────────
5.1.1 delete dspy_helm   5.2.1 run tests           5.3.1 verify imports   5.4.1 pyproject.toml
5.1.2 delete optimizers  5.2.2 fix failures        5.3.2 verify CLI        5.4.2 CHANGELOG.md
5.1.3 orphaned files     5.2.3 add tests           5.3.3 benchmark         5.4.3 release notes
```

**Sequential:**
- Track A (1-3) → Track B (1-3) → Track C (1-3) → Track D (1-3)
- All tracks depend on previous phase completion

**Est time:** 1 day

---

## Worker Assignment Suggestions

### 2 Workers

| Worker | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|--------|---------|---------|---------|---------|
| **Worker 1** | Track A + Track D | Track A + Track C | Track A | Track A + Track D |
| **Worker 2** | Track B + Track C | Track B + Track D | Track B + Track C | Track B + Track C |

### 3 Workers

| Worker | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|--------|---------|---------|---------|---------|
| **Worker 1** | Track A | Track A | Track A | Track A |
| **Worker 2** | Track B | Track B | Track B | Track B |
| **Worker 3** | Track C + Track D | Track C + Track D | Track C | Track C + Track D |

### 4 Workers (Optimal)

| Worker | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|--------|---------|---------|---------|---------|
| **Worker 1** | Track A | Track A | Track A | Track A |
| **Worker 2** | Track B | Track B | Track B | Track B |
| **Worker 3** | Track C | Track C | Track C | Track C |
| **Worker 4** | Track D | Track D | - | Track D |

---

## Task Dependencies Summary

### Critical Path (Longest Chain)

**Phase 2:**
```
2.1.1 → 2.2.1 → 2.2.2 → 2.2.3 → 2.3.3 → 2.4.6
│         │         │         │         │
│         │         │         │         └── Update imports
│         │         │         └───────────── Complete CLI methods
│         │         └───────────────────────── Dispatcher
│         └─────────────────────────────────── Registry
└───────────────────────────────────────────── Framework __init__.py
```

**Phase 3:**
```
3.1.1 → 3.1.2 → 3.1.3 → 3.3.1 ──┐
                                ├──→ 3.3.4 → 3.4.4
3.2.1 → 3.2.4 ─────────────────┘
        │
        └─────────────────────────→ CASS integration
```

**Phase 4:**
```
4.1.1 → 4.1.2 → 4.1.4 ──┐
                        ├──→ All Phase 4 done
4.2.1 → 4.2.4 ──────────┘
```

---

## Quick Start Commands

### Run Phase 2 in Parallel (4 workers)

```bash
# Worker 1: Framework structure
python -m dspy_integration create framework --structure

# Worker 2: Dispatcher
python -m dspy_integration create dispatcher

# Worker 3: CLI improvements
python -m dspy_integration create cli --forgiving --robot

# Worker 4: Consolidation
python -m dspy_integration consolidate dspy_helm
```

### Run Phase 3 in Parallel (4 workers)

```bash
# Worker 1: UI
python -m dspy_integration create ui --menu --recommendation --progression

# Worker 2: CASS patterns
python -m dspy_integration create semantic --hash-embedder --edge-ngram

# Worker 3: Approaches
python -m dspy_integration create approaches --all

# Worker 4: Interactive
python -m dspy_integration create interactive --repl
```

---

## Progress Tracking

### Per-Phase Checklist

- [ ] Track A complete
- [ ] Track B complete
- [ ] Track C complete
- [ ] Track D complete
- [ ] All dependencies resolved
- [ ] Tests pass
- [ ] Documentation updated

### Daily Standup Questions

1. What did you complete yesterday?
2. What are you working on today?
3. Any blockers (waiting for other tracks)?
4. Any tasks that can be parallelized?

---

## Files Created

| Phase | File | Purpose |
|-------|------|---------|
| 2 | `PHASE2_TASKS.md` | Phase 2 detailed tasks |
| 3 | `PHASE3_TASKS.md` | Phase 3 detailed tasks |
| 4 | `PHASE4_TASKS.md` | Phase 4 detailed tasks |
| 5 | `PHASE5_TASKS.md` | Phase 5 detailed tasks |
| All | `MASTER_TASKS.md` | This file |

---

*This file should be read alongside individual phase task files.*
