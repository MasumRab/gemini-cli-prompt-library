# Phase 3: UI + CASS Integration

**Status**: NOT STARTED  
**Started**: -  
**Completed**: -  
**Duration Estimate**: 3-4 days

---

## Overview

Build rich UI for command recommendations, integrate CASS patterns for semantic search, implement all 5 approaches.

## Task Graph

```
PARALLEL TRACK A: UI Components
├── 3.1.1 Design Command Menu UI spec [INDEPENDENT]
├── 3.1.2 Create ui/menu.py - MenuRenderer [INDEPENDENT]
├── 3.1.3 Create ui/recommendation.py [DEPENDS: 3.1.2]
└── 3.1.4 Create ui/progression.py [INDEPENDENT]

PARALLEL TRACK B: CASS Integration
├── 3.2.1 Create semantic/hash_embedder.py [INDEPENDENT]
├── 3.2.2 Create semantic/edge_ngram.py [INDEPENDENT]
├── 3.2.3 Create semantic/vector_index.py [DEPENDS: 3.2.1]
└── 3.2.4 Integrate cass-style search [DEPENDS: 3.2.1, 3.2.2]

PARALLEL TRACK C: 5 Approaches
├── 3.3.1 Implement MIPROv2 approach [INDEPENDENT]
├── 3.3.2 Implement Bootstrap approach [INDEPENDENT]
├── 3.3.3 Implement Custom approach [INDEPENDENT]
└── 3.3.4 Add approach selection UI [DEPENDS: 3.3.1, 3.3.2, 3.3.3]

PARALLEL TRACK D: Interactive Mode
├── 3.4.1 Create interactive/session.py [INDEPENDENT]
├── 3.4.2 Create interactive/history.py [INDEPENDENT]
├── 3.4.3 Create interactive/completer.py [INDEPENDENT]
└── 3.4.4 Full REPL implementation [DEPENDS: 3.4.1, 3.4.2, 3.4.3]
```

---

## Tasks

### 3.1 UI Components (Track A)

#### 3.1.1 Design Command Menu UI spec
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 1 hour

Create docs/MENU_UI_SPEC.md with:
- Layout design (recommendation panel)
- Color scheme (success/warning/info)
- Keyboard shortcuts
- Interaction flows
- Mockup examples
```

#### 3.1.2 Create ui/menu.py - MenuRenderer
```
Status: PENDING
Priority: HIGH
Depends: 3.1.1
Assign: -
Est: 2 hours

MenuRenderer class:
- render_recommendation(command, alternatives)
- render_alternatives(results)
- render_checklist(progress)
- format_with_highlight(text)
- color_support() for ANSI colors

Dependencies:
- rich library for terminal formatting
```

#### 3.1.3 Create ui/recommendation.py
```
Status: PENDING
Priority: HIGH
Depends: 3.1.2
Assign: -
Est: 2 hours

RecommendationPanel class:
- display(command_match)
- show_alternatives(alternatives)
- show_examples(cass_results)
- get_user_choice() → selection

CassAugmentedSuggestions:
- async search for alternatives
- cache results
- display historical examples
```

#### 3.1.4 Create ui/progression.py
```
Status: PENDING
Priority: MEDIUM
Depends: 3.1.2
Assign: -
Est: 1 hour

ProgressionChecklist class:
- start_workflow(name)
- update_step(step_id, status)
- display() → styled table
- complete()

Status values: pending, in_progress, completed, failed
```

---

### 3.2 CASS Integration (Track B)

#### 3.2.1 Create semantic/hash_embedder.py
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 2 hours

HashEmbedder class (FNV-1a fallback):
- __init__() → instant (<1ms)
- embed(text) → vector[384]
- embed_batch(texts) → parallel
- cosine_similarity(v1, v2)

No ML dependencies - pure Python
Fallback when MiniLM not available
```

#### 3.2.2 Create semantic/edge_ngram.py
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 1 hour

EdgeNGramIndexer class:
- add_document(id, text)
- build_index()
- search(query) → O(1) prefix matching

Benefits:
- Fast prefix searches (cal → calculate)
- Pre-computed at index time
- BM25 + edge n-gram combination
```

#### 3.2.3 Create semantic/vector_index.py
```
Status: PENDING
Priority: MEDIUM
Depends: 3.2.1
Assign: -
Est: 2 hours

VectorIndex class (CVVI format):
- save(path)
- load(path) → memory-mapped
- add(vector, metadata)
- search(query_vector, top_k)
- similarity_search(text, top_k)

Format:
- Header (magic, version, dimension)
- Entries (hash, source_id, timestamp, vector)
- CRC32 validation
```

#### 3.2.4 Integrate cass-style search
```
Status: PENDING
Priority: HIGH
Depends: 3.2.1, 3.2.2
Assign: -
Est: 3 hours

In toml.py or new search/ directory:
- create_search_index(commands_dir)
- semantic_search(query) → HashEmbedder
- lexical_search(query) → EdgeNGram
- hybrid_search(query) → RRF combination

Search modes:
- lexical (BM25)
- semantic (hash or ML)
- hybrid (RRF combination)
```

---

### 3.3 5 Approaches (Track C)

#### 3.3.1 Implement MIPROv2 approach
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 3 hours

In modules/improve.py or new approaches/:
- approach_mipro(prompt, trainset, valset)
- MIPROv2 optimizer configuration
- Metric function for prompt quality

Tests:
- test_mipro_approach.py
```

#### 3.3.2 Implement Bootstrap approach
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 2 hours

In approaches/:
- approach_bootstrap(prompt)
- BootstrapFewShotWithRandomSearch
- Fewer API calls than MIPROv2

Tests:
- test_bootstrap_approach.py
```

#### 3.3.3 Implement Custom approach
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 2 hours

In approaches/:
- approach_custom(prompt, focus, examples)
- Focus options: clarity, specificity, structure, context, output
- Examples: 0-5 few-shot examples

Usage:
python -m dspy_integration improve "prompt" --approach custom --focus clarity --examples 3
```

#### 3.3.4 Add approach selection UI
```
Status: PENDING
Priority: MEDIUM
Depends: 3.3.1, 3.3.2, 3.3.3
Assign: -
Est: 1 hour

In cli.py:
- --approach flag (toml, dspy, mipro, bootstrap, custom)
- --focus flag (for custom)
- --examples flag (for custom)
- Display approach comparison table
```

---

### 3.4 Interactive Mode (Track D)

#### 3.4.1 Create interactive/session.py
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 2 hours

InteractiveSession class:
- __init__(base_prompt)
- add_attempt(approach, result)
- set_selected(attempt_id)
- save(path) → JSON
- load(path) → Session

Session format:
{
  "session_id": "...",
  "base_prompt": "...",
  "attempts": [...],
  "selected_attempt": 1
}
```

#### 3.4.2 Create interactive/history.py
```
Status: PENDING
Priority: MEDIUM
Depends: 3.4.1
Assign: -
Est: 1 hour

SessionHistory class:
- list_sessions() → names
- load_session(name)
- delete_session(name)
- get_path(name) → ~/.dspy_tuning/

Storage: ~/.dspy_tuning/sessions/
```

#### 3.4.3 Create interactive/completer.py
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 1 hour

CommandCompleter class:
- complete_command(text) → suggestions
- complete_approach(text) → ['toml', 'dspy', 'mipro', ...]
- complete_filename(text) → file paths

For readline integration in interactive mode
```

#### 3.4.4 Full REPL implementation
```
Status: PENDING
Priority: HIGH
Depends: 3.4.1, 3.4.2, 3.4.3
Assign: -
Est: 3 hours

In interactive/:
- main() → run_repl()
- prompt: "dspy> "
- Commands: try, compare, diff, pick, save, load, sessions, help, quit

Readline features:
- History (Up/Down arrows)
- Tab completion
- Vi mode (Ctrl+J)

Example session:
dspy> try mipro
[Running MIPROv2...]
Score: 44/50
dspy> try toml
Score: 32/50
dspy> compare
┌─────┬──────────┬───────┐
│ #   │ Approach  │ Score │
├─────┼──────────┼───────┤
│ 1   │ mipro     │ 44/50 │
│ 2   │ toml      │ 32/50 │
└─────┴──────────┴───────┘
dspy> pick 1
dspy> save my-prompt
Saved: ~/.dspy_tuning/sessions/my-prompt.json
dspy> quit
```

---

## Deliverables

After Phase 3:
- [ ] Rich UI with Command Menu, Alternatives, Progression Checklist
- [ ] HashEmbedder for zero-dep semantic search
- [ ] Edge N-Gram for fast prefix matching
- [ ] All 5 approaches implemented (TOML, DSPy, MIPROv2, Bootstrap, Custom)
- [ ] Full interactive REPL with history and completion
- [ ] cass-style hybrid search (lexical + semantic)

## Dependencies

- rich (terminal formatting)
- readline (or pyreadline3 for Windows)
- tomli (already installed)

## Notes

- CASS patterns adopted from Dicklesworthstone/coding_agent_session_search
- Hash embedder provides semantic-like search without ML model
- Hybrid search uses Reciprocal Rank Fusion (RRF)
