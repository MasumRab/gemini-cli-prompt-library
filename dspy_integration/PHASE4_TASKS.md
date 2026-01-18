# Phase 4: Agentic Integration

**Status**: NOT STARTED  
**Started**: -  
**Completed**: -  
**Duration Estimate**: 2-3 days

---

## Overview

Implement proactive workflow suggestions and self-correction skills for autonomous agent behavior.

## Task Graph

```
PARALLEL TRACK A: Proactive Suggestions
├── 4.1.1 Create agents/suggester.py [INDEPENDENT]
├── 4.1.2 Add workflow detection logic [DEPENDS: 4.1.1]
├── 4.1.3 Create suggestion UI [DEPENDS: 4.1.1]
└── 4.1.4 Integrate with CLI [DEPENDS: 4.1.2, 4.1.3]

PARALLEL TRACK B: Self-Correction Skills
├── 4.2.1 Create agents/self_correct.py [INDEPENDENT]
├── 4.2.2 Add error analysis logic [DEPENDS: 4.2.1]
├── 4.2.3 Add prompt rewriting [DEPENDS: 4.2.1]
└── 4.2.4 Add retry mechanism [DEPENDS: 4.2.2, 4.2.3]

PARALLEL TRACK C: Integration
├── 4.3.1 Update CLI for agent mode [INDEPENDENT]
├── 4.3.2 Add agent config [INDEPENDENT]
└── 4.3.3 Create agent docs [DEPENDS: 4.3.1]
```

---

## Tasks

### 4.1 Proactive Suggestions (Track A)

#### 4.1.1 Create agents/suggester.py
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 2 hours

WorkflowSuggester class:
- analyze_request(request) → is_workflow_candidate()
- get_suggestion(request) → Suggestion

Suggestion format:
{
  "is_candidate": bool,
  "workflow_name": str,
  "workflow_description": str,
  "confidence": float,
  "reason": str,
  "alternative": str
}

Detection patterns:
- Multi-step requests ("fix X and verify Y")
- Testing requests ("test my code")
- Refactoring requests ("refactor my code")
- Debugging requests ("debug why X is failing")
```

#### 4.1.2 Add workflow detection logic
```
Status: PENDING
Priority: HIGH
Depends: 4.1.1
Assign: -
Est: 2 hours

In agents/detection.py:
- detect_workflow_type(request) → workflow_type
- detect_implied_steps(request) → [steps]
- estimate_complexity(request) → low/medium/high
- detect_context_requirements(request) → [requirements]

Workflow types:
- debugging (trace-issue → fix → test)
- refactoring (analyze → refactor → verify)
- testing (generate → run → fix)
- comprehensive (multiple combined)
```

#### 4.1.3 Create suggestion UI
```
Status: PENDING
Priority: MEDIUM
Depends: 4.1.1
Assign: -
Est: 1 hour

SuggestionDisplay class:
- show_suggestion(suggestion) → user_response
- format_workflow_steps(steps) → styled list
- format_comparison(simple, workflow) → side-by-side

Example output:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Proactive Suggestion

I noticed your request might be better served by a workflow.

Option A: /code-review:refactor
─────────────────────────────────
Single command approach

Option B: /workflows:smart-refactor
─────────────────────────────────
Multi-step approach:
1. Analyze code structure
2. Identify refactoring opportunities
3. Apply changes
4. Verify with tests

Would you like to use Option B? [Y/n]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 4.1.4 Integrate with CLI
```
Status: PENDING
Priority: HIGH
Depends: 4.1.2, 4.1.3
Assign: -
Est: 1 hour

In cli.py:
- Add --auto-suggest flag
- Add --auto-accept flag
- Modify improve command to check suggestions
- Add "suggest" command

Usage:
python -m dspy_integration improve "fix my login bug" --auto-suggest
python -m dspy_integration suggest "write tests for user auth"
```

---

### 4.2 Self-Correction Skills (Track B)

#### 4.2.1 Create agents/self_correct.py
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 2 hours

SelfCorrectSkill class:
- analyze_failure(error, context) → FailureAnalysis
- rewrite_prompt(prompt, feedback) → new_prompt
- should_retry(error) → bool
- get_retry_strategy(error) → RetryStrategy

FailureAnalysis format:
{
  "root_cause": str,
  "is_retryable": bool,
  "suggested_fix": str,
  "related_docs": [str]
}

RetryStrategy format:
{
  "strategy": str,  # "rewrite", "alternative", "escalate"
  "new_prompt": str,
  "max_retries": int
}
```

#### 4.2.2 Add error analysis logic
```
Status: PENDING
Priority: HIGH
Depends: 4.2.1
Assign: -
Est: 2 hours

In agents/error_analyzer.py:
- categorize_error(error) → category
- extract_error_pattern(error) → pattern
- find_similar_issues(context) → [issues]
- generate_fix_suggestion(error, context) → suggestion

Error categories:
- syntax_error → "Check your code syntax"
- runtime_error → "Review error traceback"
- timeout_error → "Simplify or reduce scope"
- validation_error → "Check input format"
- api_error → "Check API configuration"
```

#### 4.2.3 Add prompt rewriting
```
Status: PENDING
Priority: HIGH
Depends: 4.2.1
Assign: -
Est: 2 hours

In agents/prompt_rewriter.py:
- rewrite_with_context(original, context) → rewritten
- add_constraints(prompt, constraints) → constrained
- simplify_prompt(prompt) → simplified
- expand_prompt(prompt, details) → expanded

Rewriting strategies:
- Add specific examples
- Add constraints
- Simplify complex requests
- Clarify ambiguous terms
- Add output format specifications
```

#### 4.2.4 Add retry mechanism
```
Status: PENDING
Priority: MEDIUM
Depends: 4.2.2, 4.2.3
Assign: -
Est: 1 hour

RetryManager class:
- execute_with_retry(command, max_retries=3)
- on_failure(error, attempt) → action
- track_attempts(command) → history

Actions:
- "retry" → try same command again
- "rewrite" → use rewritten prompt
- "alternative" → try different command
- "escalate" → ask user for help

Exponential backoff for retries
```

---

### 4.3 Integration (Track C)

#### 4.3.1 Update CLI for agent mode
```
Status: PENDING
Priority: HIGH
Depends: None
Assign: -
Est: 1 hour

In cli.py:
- Add --agent-mode flag
- Add --auto-correct flag
- Add --max-retries flag

Agent mode behavior:
- Auto-suggest workflows
- Auto-correct on failures
- Auto-retry with backoff
- Quiet output (--robot style)

Example:
python -m dspy_integration improve "fix bug" --agent-mode --auto-correct
```

#### 4.3.2 Add agent config
```
Status: PENDING
Priority: MEDIUM
Depends: None
Assign: -
Est: 30 min

Create config/agent.yaml:
```yaml
agent:
  auto_suggest: true
  auto_correct: true
  max_retries: 3
  retry_backoff: exponential
  suggestion_threshold: 0.7
```

In config/__init__.py:
- load_agent_config()
- validate_agent_config()
```

#### 4.3.3 Create agent docs
```
Status: PENDING
Priority: LOW
Depends: 4.3.1
Assign: -
Est: 1 hour

Create docs/AGENT_MODE.md:
- How agent mode works
- Configuration options
- Examples
- Troubleshooting

Update AGENTIC_COMPATIBILITY.md:
- Agent integration details
- Cross-agent knowledge sharing
```

---

## Deliverables

After Phase 4:
- [ ] WorkflowSuggester for proactive recommendations
- [ ] SelfCorrectSkill for error recovery
- [ ] Retry mechanism with exponential backoff
- [ ] Agent mode CLI flags (--agent-mode, --auto-correct)
- [ ] Agent configuration file
- [ ] Agent mode documentation

## Dependencies

- Same as Phase 3
- No new external dependencies

## Notes

- Agent skills can be used independently or together
- Self-correction can be triggered by tool failures
- Proactive suggestions require user opt-in
- All agent features should be disable-able
