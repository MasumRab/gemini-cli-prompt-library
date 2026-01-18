# CLI Library Compatibility Matrix

**Project**: gemini-cli-prompt-library  
**Purpose**: Complete decision matrix for CLI framework selection  
**Date**: 2026-01-18

---

## 1. Framework Comparison

| Library | Primary Goal | Type System | Learning Curve | Maintenance | Author |
|---------|-------------|-------------|----------------|-------------|--------|
| **typer** | FastAPI-style CLI from type hints | Full type hints | Low | Active | tiangolo (FastAPI team) |
| **cyclopts** | Faster typer alternative | Full type hints | Low | Active | Community |
| **click** | Composable CLI framework | Decorators | Medium | Active | Pallets |
| **python-fire** | Auto-CLI from any object | None required | Very Low | Active | Google |
| **argparse** | Standard library CLI | Manual | Medium | Stdlib | Python Core |

### Detailed Analysis

#### typer
- **GitHub Stars**: 15k+
- **Dependencies**: click, rich (optional)
- **Key Feature**: Type hints become CLI arguments automatically
- **Drawback**: Slightly slower startup than argparse
- **Best For**: Modern Python CLIs, teams familiar with FastAPI

#### cyclopts
- **Why It Exists**: Fixes 13 known Typer edge cases
- **Fixes**: Boolean flags, negative numbers, empty strings, list parsing
- **Key Feature**: Native `--json` output mode
- **Drawback**: Smaller community, less documentation
- **Best For**: When Typer edge cases cause problems

#### click
- **GitHub Stars**: 15k+
- **Key Feature**: Composable, plugin architecture
- **Drawback**: Decorator-heavy, code duplication
- **Note**: Typer is built on Click
- **Best For**: Complex plugin systems, when Typer insufficient

#### python-fire
- **GitHub Stars**: 27k+
- **Author**: Google
- **Key Feature**: Any Python object → CLI automatically
- **Drawback**: Ignores type hints, magic behavior
- **Best For**: Rapid prototyping, debugging tools

#### argparse
- **Key Feature**: Zero dependencies, always available
- **Drawback**: Verbose, no modern features
- **Current Usage**: `dspy_helm/cli.py`
- **Best For**: Stdlib-only requirements, simple scripts

---

## 2. Interactive/Prompt Libraries

| Library | Primary Goal | Prompt Types | Async | Customization | Maintained |
|---------|-------------|--------------|-------|---------------|------------|
| **InquirerPy** | Interactive prompts (JS Inquirer port) | Select, checkbox, input, confirm, fuzzy, filepath, password | ✅ | High | ✅ Active |
| **questionary** | Simple prompts | Select, checkbox, input, confirm | ❌ | Medium | ✅ Active |
| **prompt-toolkit** | Advanced terminal input | Full readline, autocomplete, syntax highlighting | ✅ | Very High | ✅ Active |
| **PyInquirer** | Original Inquirer port | Select, checkbox, input | ❌ | Medium | ❌ Unmaintained |

### InquirerPy Prompt Types

| Type | Description | Use Case |
|------|-------------|----------|
| `select` | Single choice from list | Pick one option |
| `checkbox` | Multiple choices | Select features |
| `input/text` | Free text input | Names, paths |
| `confirm` | Yes/No | Confirmations |
| `fuzzy` | Searchable select | Large lists |
| `filepath` | File/directory picker | File selection |
| `password/secret` | Hidden input | API keys |
| `number` | Numeric input | Quantities |
| `rawlist` | Numbered list | Quick selection |
| `expand` | Shortcut keys | Power users |

---

## 3. Output/Display Libraries

| Library | Primary Goal | Features | Performance | TUI Support |
|---------|-------------|----------|-------------|-------------|
| **rich** | Beautiful terminal output | Tables, syntax, progress, markdown, panels, trees, tracebacks | Fast | Partial |
| **Textual** | Full TUI framework | Widgets, layouts, CSS styling, reactive, 16.7M colors | Fast | Full |
| **colorama** | Cross-platform colors | ANSI colors only | Very Fast | None |
| **tqdm** | Progress bars only | Progress, ETA, nested bars | Fast | None |

### rich Features Detail

| Feature | Description | Agentic Safe |
|---------|-------------|--------------|
| Tables | Formatted data tables | ✅ Degrades gracefully |
| Progress | Progress bars, spinners | ✅ Can disable |
| Syntax | Code highlighting | ✅ Plain text fallback |
| Markdown | Render markdown | ✅ Plain text fallback |
| Panels | Bordered content boxes | ✅ Plain text fallback |
| Trees | Hierarchical data | ✅ Plain text fallback |
| Tracebacks | Pretty exceptions | ✅ Works everywhere |
| Console | Central output control | ✅ `force_terminal=False` |

### Textual Features Detail

| Feature | Description | Agentic Safe |
|---------|-------------|--------------|
| Widgets | Buttons, inputs, lists | ✅ Headless mode |
| CSS Styling | Textual CSS for layout | ✅ Headless mode |
| Reactive | Data binding | ✅ Headless mode |
| Mouse Support | Click, scroll, drag | N/A in headless |
| 16.7M Colors | True color support | ✅ Fallback |
| Pilot Testing | Automated UI testing | ✅ Designed for it |

---

## 4. Agentic Compatibility Matrix

| Library | JSON Output | Headless Mode | No TTY Safe | Env Detection | stdin Pipe |
|---------|-------------|---------------|-------------|---------------|------------|
| **typer** | ✅ `--json` flag | ✅ | ✅ | Manual | ✅ |
| **cyclopts** | ✅ Built-in | ✅ | ✅ | Manual | ✅ |
| **click** | ✅ Manual | ✅ | ✅ | Manual | ✅ |
| **python-fire** | ✅ Default | ✅ Native | ✅ | ✅ Auto | ✅ |
| **InquirerPy** | ❌ | ⚠️ Hangs | ❌ Blocks | Manual | ❌ |
| **questionary** | ❌ | ⚠️ Hangs | ❌ Blocks | Manual | ❌ |
| **prompt-toolkit** | ❌ | ⚠️ | ⚠️ | Manual | ⚠️ |
| **rich** | ✅ `force_terminal=False` | ✅ | ✅ | ✅ Auto | ✅ |
| **Textual** | ✅ Headless mode | ✅ Native | ✅ | ✅ Auto | ✅ |

### Legend
- ✅ Works out of box
- ⚠️ Needs configuration/wrapper
- ❌ Does not work / blocks

---

## 5. Agent Tool Compatibility

Tested with major AI coding agents:

| Library | gemini-cli | qwen-cli | opencode | claude-code | amp | cursor | aider |
|---------|------------|----------|----------|-------------|-----|--------|-------|
| **typer** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **cyclopts** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **python-fire** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **rich** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Textual** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **InquirerPy** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| **questionary** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| **prompt-toolkit** | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

**Note**: ⚠️ means needs `is_agentic()` wrapper for fallback behavior

---

## 6. Feature Overlap Matrix

| Feature | typer | cyclopts | click | fire | InquirerPy | rich | Textual |
|---------|-------|----------|-------|------|------------|------|---------|
| **Command groups** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Subcommands** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Auto help** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Shell completion** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Type validation** | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| **Interactive prompts** | ⚠️ basic | ⚠️ basic | ⚠️ basic | ❌ | ✅ | ❌ | ✅ |
| **Select menus** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Fuzzy search** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Progress bars** | ✅ (rich) | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Tables** | ✅ (rich) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Syntax highlight** | ✅ (rich) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Markdown render** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Widgets/layouts** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Mouse support** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **CSS styling** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 7. Recommended Stack Combinations

### Option A: typer + rich + InquirerPy ✅ SELECTED (TC-001)

```
Components:
├── typer          → CLI structure, commands, arguments
├── rich           → Tables, progress, syntax highlighting
└── InquirerPy     → Interactive menus, fuzzy search (with wrapper)
```

| Aspect | Rating |
|--------|--------|
| Human Experience | ⭐⭐⭐⭐⭐ |
| Agentic Support | ⭐⭐⭐⭐ (needs wrappers) |
| Learning Curve | ⭐⭐⭐⭐ (Low) |
| Flexibility | ⭐⭐⭐⭐⭐ |

**Best For**: Human-friendly interactive CLI with beautiful output  
**Agentic Note**: Needs wrapper for InquirerPy headless fallback

---

### Option B: typer + rich (Simplified)

```
Components:
├── typer          → CLI structure + typer.prompt() for basic input
└── rich           → Tables, progress, syntax highlighting
```

| Aspect | Rating |
|--------|--------|
| Human Experience | ⭐⭐⭐⭐ |
| Agentic Support | ⭐⭐⭐⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐⭐ (Very Low) |
| Flexibility | ⭐⭐⭐ |

**Best For**: Agentic-first with optional human formatting  
**Agentic Note**: Fully compatible, no wrappers needed

---

### Option C: cyclopts + rich

```
Components:
├── cyclopts       → Faster typer alternative, native JSON
└── rich           → Tables, progress, syntax highlighting
```

| Aspect | Rating |
|--------|--------|
| Human Experience | ⭐⭐⭐⭐ |
| Agentic Support | ⭐⭐⭐⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐ (Low) |
| Flexibility | ⭐⭐⭐⭐ |

**Best For**: When Typer edge cases cause problems  
**Agentic Note**: Fully compatible, native JSON mode

---

### Option D: python-fire + rich

```
Components:
├── python-fire    → Zero-config CLI from objects
└── rich           → Tables, progress, syntax highlighting
```

| Aspect | Rating |
|--------|--------|
| Human Experience | ⭐⭐⭐ |
| Agentic Support | ⭐⭐⭐⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐⭐ (Lowest) |
| Flexibility | ⭐⭐ |

**Best For**: Rapid prototyping, auto-CLI from objects  
**Agentic Note**: Native compatibility, no interactive prompts

---

### Option E: Textual (Full TUI)

```
Components:
└── Textual        → Complete TUI framework (includes rich)
```

| Aspect | Rating |
|--------|--------|
| Human Experience | ⭐⭐⭐⭐⭐ |
| Agentic Support | ⭐⭐⭐⭐⭐ |
| Learning Curve | ⭐⭐⭐ (Medium) |
| Flexibility | ⭐⭐⭐⭐⭐ |

**Best For**: Complex terminal applications, dashboards  
**Agentic Note**: Built-in headless mode for testing

---

## 8. Decision Criteria

### When to Choose Each Option

| Requirement | Recommended Stack |
|-------------|-------------------|
| Interactive menus + beautiful output | **Option A**: typer + rich + InquirerPy |
| Agentic-first, minimal wrappers | **Option B**: typer + rich |
| Boolean flags, native JSON | **Option C**: cyclopts + rich |
| Rapid prototyping | **Option D**: python-fire + rich |
| Full terminal application | **Option E**: Textual |
| Stdlib only | **argparse** (no stack) |

### Project-Specific Recommendation

For **gemini-cli-prompt-library**:

**Selected**: Option A (typer + rich + InquirerPy)

**Rationale**:
1. Interactive prompt workflows (guided-dev, guided-pr)
2. Beautiful output for human users
3. Agentic compatibility via wrappers
4. Type-safe CLI development
5. FastAPI-like development experience

---

## 9. Implementation Priority

### Phase 1: Core Infrastructure
```
src/utils/
├── agentic.py     # is_agentic() detection
├── prompts.py     # smart_* wrappers for InquirerPy
└── output.py      # OutputFormat handler (human/json)
```

### Phase 2: CLI Migration
```
dspy_helm/cli.py   # argparse → typer
```

### Phase 3: Interactive Features
```
Guided workflows using smart_* prompts
```

### Phase 4: Full TUI (Future)
```
Consider Textual for dashboard/monitoring features
```

---

## 10. References

- **Session**: 2026-01-13T10-46 (CLI framework decision)
- **Technical Constraint**: TC-001
- [Typer Documentation](https://typer.tiangolo.com/)
- [Cyclopts Documentation](https://cyclopts.readthedocs.io/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Textual Documentation](https://textual.textualize.io/)
- [InquirerPy Documentation](https://inquirerpy.readthedocs.io/)
- [Python Fire Documentation](https://github.com/google/python-fire)
