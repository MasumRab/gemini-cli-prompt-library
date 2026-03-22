import os
import re
import datetime
import tempfile

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _empty_findings():
    return {
        "Architecture": [],
        "Performance": [],
        "Security": [],
        "Documentation": [],
        "DSPy": [],
    }


def _atomic_write(filepath, content):
    """Writes content to a file atomically."""
    try:
        dir_ = os.path.dirname(os.path.abspath(filepath))
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=dir_, delete=False, suffix=".tmp"
        ) as tmp:
            tmp.write(content)
        os.replace(tmp.name, filepath)
        return True
    except OSError as exc:
        print(f"Warning: could not write {filepath}: {exc}")
        if os.path.exists(tmp.name):
            try:
                os.remove(tmp.name)
            except OSError:
                pass
        return False


def check_registry_performance(
    filepath=None, findings=None, inserted_todos=None
):
    """Checks for inefficient registry instantiation."""
    if filepath is None:
        filepath = os.path.join(
            _REPO_ROOT, "dspy_integration", "framework", "registry.py"
        )
    if findings is None:
        findings = _empty_findings()
    if inserted_todos is None:
        inserted_todos = []

    if not os.path.exists(filepath):
        return findings, inserted_todos

    with open(filepath, "r") as f:
        content = f.read()

    pattern = r"def get_command\(name\):\n[^\n]*registry = CommandRegistry\(\)"
    if re.search(pattern, content):
        findings["Performance"].append(
            f"Inefficient `CommandRegistry` instantiation in `{filepath}`. "
            "Creates a new registry (scanning all files) on every call."
        )

        todo_comment = (
            "    # TODO [High Priority]: Implement singleton/caching for "
            "CommandRegistry\n"
            "    # to avoid O(N) re-parsing."
        )
        if "Implement singleton/caching" not in content:
            new_content = content.replace(
                "    registry = CommandRegistry()",
                f"{todo_comment}\n    registry = CommandRegistry()",
            )
            if _atomic_write(filepath, new_content):
                inserted_todos.append(
                    (
                        filepath,
                        "High",
                        "Implement singleton/caching for CommandRegistry",
                    )
                )

    return findings, inserted_todos


def check_dispatcher_architecture(
    filepath=None, findings=None, inserted_todos=None
):
    """Checks for missing IntelligentDispatcher usage."""
    if filepath is None:
        filepath = os.path.join(
            _REPO_ROOT, "dspy_integration", "framework", "dispatcher.py"
        )
    if findings is None:
        findings = _empty_findings()
    if inserted_todos is None:
        inserted_todos = []

    if not os.path.exists(filepath):
        return findings, inserted_todos

    with open(filepath, "r") as f:
        content = f.read()

    if "IntelligentDispatcher" not in content:
        findings["Architecture"].append(
            f"`{filepath}` uses a simple dispatch function instead of the "
            "`IntelligentDispatcher` class available in the framework."
        )

        todo_comment = (
            "    # TODO [Medium Priority]: Integrate `IntelligentDispatcher`\n"
            "    # for better routing logic."
        )
        if "Integrate `IntelligentDispatcher`" not in content:
            if "def dispatch(user_input):" in content:
                new_content = content.replace(
                    "def dispatch(user_input):",
                    f"def dispatch(user_input):\n{todo_comment}",
                )
                if _atomic_write(filepath, new_content):
                    inserted_todos.append(
                        (filepath, "Medium", "Integrate IntelligentDispatcher")
                    )

    return findings, inserted_todos


def check_dspy_modules(directory=None, findings=None, inserted_todos=None):
    """Checks DSPy modules for optimization."""
    if directory is None:
        directory = os.path.join(_REPO_ROOT, "dspy_integration", "modules")
    if findings is None:
        findings = _empty_findings()
    if inserted_todos is None:
        inserted_todos = []

    if not os.path.exists(directory):
        return findings, inserted_todos

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                content = f.read()

            if (
                "dspy.Module" in content
                and "BootstrapFewShot" not in content
                and "MIPROv2" not in content
            ):
                if "TODO" in content and (
                    "Optimize" in content or "MIPRO" in content
                ):
                    continue

                findings["DSPy"].append(
                    f"`{filepath}`: Module lacks advanced optimizers "
                    "(BootstrapFewShot/MIPROv2)."
                )

                target_class_pattern = (
                    r"class .*Optimizer\(.*dspy\.Module.*\):"
                )
                match = re.search(target_class_pattern, content)
                if not match:
                    target_class_pattern = r"class .*\(*dspy\.Module.*\):"
                    match = re.search(target_class_pattern, content)

                if match:
                    class_line = match.group(0)
                    todo_comment = (
                        "    # TODO [Low Priority]: Optimize module using "
                        "dspy.MIPROv2\n"
                        "    # or BootstrapFewShot for better prompt "
                        "performance."
                    )

                    if content.count(class_line) == 1:
                        new_content = content.replace(
                            class_line, f"{class_line}\n{todo_comment}"
                        )
                        if _atomic_write(filepath, new_content):
                            inserted_todos.append(
                                (
                                    filepath,
                                    "Low",
                                    "Optimize module using dspy.MIPROv2",
                                )
                            )

    return findings, inserted_todos


def generate_report(findings, inserted_todos):
    """Generates the Markdown report."""
    audit_date = datetime.datetime.now().strftime("%B %Y")
    date_str = datetime.datetime.now().strftime('%Y_%m_%d')
    report_name = f"AUDIT_REPORT_{date_str}.md"
    audit_report_file = os.path.join(_REPO_ROOT, report_name)

    with open(audit_report_file, "w") as f:
        f.write("# Scheduled Codebase Audit Report\n")
        f.write(f"**Date**: {audit_date}\n")
        f.write("**Auditor**: Jules (AI Agent)\n")
        f.write("**Scope**: `dspy_integration/` framework and modules\n\n")

        f.write("## 1. Executive Summary\n")
        summary = "This audit identifies several areas for improvement. "
        if findings["Performance"]:
            summary += (
                f"Critical performance bottlenecks found "
                f"({len(findings['Performance'])}). "
            )
        if findings["Architecture"]:
            summary += (
                f"Architectural inconsistencies noted "
                f"({len(findings['Architecture'])}). "
            )
        if findings["DSPy"]:
            summary += (
                f"DSPy optimization opportunities detected in "
                f"{len(findings['DSPy'])} modules. "
            )
        f.write(f"{summary}\n\n")

        f.write("## 2. Findings\n\n")
        for category, items in findings.items():
            if items:
                f.write(f"### {category}\n")
                for item in items:
                    f.write(f"* {item}\n")
                f.write("\n")

        if inserted_todos:
            f.write("## 3. List of Inserted TODOs\n\n")
            f.write("| File Path | Priority | Issue Description |\n")
            f.write("|-----------|----------|-------------------|\n")
            for filepath, priority, desc in inserted_todos:
                rel_path = os.path.relpath(filepath, _REPO_ROOT)
                f.write(f"| `{rel_path}` | {priority} | {desc} |\n")
            f.write("\n")

        f.write("## 4. Recommendations & Roadmap\n\n")

        f.write("### Short-Term (Immediate Fixes)\n")
        if findings["Performance"]:
            f.write(
                "* **Refactor Registry**: Implement singleton pattern/caching "
                "for `CommandRegistry`.\n"
            )
        f.write("* **Fix Linting**: Address minor style issues.\n\n")

        f.write("### Medium-Term (Integration)\n")
        if findings["Architecture"]:
            f.write(
                "* **Unified Dispatch**: Update `dispatcher.py` to use "
                "`IntelligentDispatcher`.\n"
            )
        f.write(
            "* **Test Coverage**: Increase test coverage for framework "
            "components.\n\n"
        )

        f.write("### Long-Term (Evolution)\n")
        if findings["DSPy"]:
            f.write(
                "* **Optimization Pipeline**: Systematically apply "
                "`BootstrapFewShot` to all modules.\n"
            )
        f.write(
            "* **Agentic Workflow**: Move towards fully autonomous agent "
            "workflows.\n"
        )
    return audit_report_file


def main():
    print("Starting audit...")
    findings, inserted_todos = check_registry_performance()
    findings, inserted_todos = check_dispatcher_architecture(
        findings=findings, inserted_todos=inserted_todos
    )
    findings, inserted_todos = check_dspy_modules(
        findings=findings, inserted_todos=inserted_todos
    )
    report_path = generate_report(findings, inserted_todos)
    print(f"Audit complete. Report generated at {report_path}")


if __name__ == "__main__":
    main()
