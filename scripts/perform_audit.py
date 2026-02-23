import os
import re
import datetime

AUDIT_DATE = datetime.datetime.now().strftime("%B %Y")
date_str = datetime.datetime.now().strftime('%b_%Y').upper()
REPORT_NAME = f"AUDIT_REPORT_{date_str}.md"
AUDIT_REPORT_FILE = REPORT_NAME

FINDINGS = {
    "Architecture": [],
    "Performance": [],
    "Security": [],
    "Documentation": [],
    "DSPy": [],
}

INSERTED_TODOS = []


def check_registry_performance(filepath="dspy_integration/framework/registry.py"):
    """Checks for inefficient registry instantiation."""
    if not os.path.exists(filepath):
        return

    with open(filepath, "r") as f:
        content = f.read()

    pattern = (
        r"def get_command\(name\):\s+.*registry = CommandRegistry\(\)"
    )
    if re.search(pattern, content, re.DOTALL):
        FINDINGS["Performance"].append(
            f"Inefficient `CommandRegistry` instantiation in `{filepath}`. "
            "Creates a new registry (scanning all files) on every call."
        )

        # Insert TODO if not present
        todo_comment = (
            "    # TODO [High Priority]: Implement singleton/caching for "
            "CommandRegistry\n"
            "    # to avoid O(N) re-parsing."
        )
        if "Implement singleton/caching" not in content:
            new_content = content.replace(
                "    registry = CommandRegistry()",
                f"{todo_comment}\n    registry = CommandRegistry()"
            )
            with open(filepath, "w") as f:
                f.write(new_content)
            INSERTED_TODOS.append(
                (
                    filepath,
                    "High",
                    "Implement singleton/caching for CommandRegistry"
                )
            )


def check_dispatcher_architecture(
    filepath="dspy_integration/framework/dispatcher.py"
):
    """Checks for missing IntelligentDispatcher usage."""
    if not os.path.exists(filepath):
        return

    with open(filepath, "r") as f:
        content = f.read()

    if "IntelligentDispatcher" not in content:
        FINDINGS["Architecture"].append(
            f"`{filepath}` uses a simple dispatch function instead of the "
            "`IntelligentDispatcher` class available in the framework."
        )

        # Insert TODO if not present
        todo_comment = (
            "    # TODO [Medium Priority]: Integrate `IntelligentDispatcher`\n"
            "    # for better routing logic."
        )
        if "Integrate `IntelligentDispatcher`" not in content:
            # Find a good place to insert
            if "def dispatch(user_input):" in content:
                new_content = content.replace(
                    "def dispatch(user_input):",
                    f"def dispatch(user_input):\n{todo_comment}"
                )
                with open(filepath, "w") as f:
                    f.write(new_content)
                INSERTED_TODOS.append(
                    (filepath, "Medium", "Integrate IntelligentDispatcher")
                )


def check_dspy_modules(directory="dspy_integration/modules"):
    """Checks DSPy modules for optimization."""
    if not os.path.exists(directory):
        return

    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != "__init__.py":
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as f:
                content = f.read()

            if ("dspy.Module" in content and
                    "BootstrapFewShot" not in content and
                    "MIPROv2" not in content):
                # Check if TODO already exists
                if "TODO" in content and (
                    "Optimize" in content or "MIPRO" in content
                ):
                    continue

                FINDINGS["DSPy"].append(
                    f"`{filepath}`: Module appears to lack advanced optimizers "
                    "(BootstrapFewShot/MIPROv2)."
                )

                # Insert TODO
                # Try to insert into Optimizer class if it exists, else Module
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
                        "    # TODO [Low Priority]: Optimize this module using "
                        "dspy.MIPROv2\n"
                        "    # or BootstrapFewShot for better prompt "
                        "performance."
                    )

                    if content.count(class_line) == 1:
                        new_content = content.replace(
                            class_line,
                            f"{class_line}\n{todo_comment}"
                        )
                        with open(filepath, "w") as f:
                            f.write(new_content)
                        INSERTED_TODOS.append(
                            (
                                filepath,
                                "Low",
                                "Optimize module using dspy.MIPROv2"
                            )
                        )


def generate_report():
    """Generates the Markdown report."""
    with open(AUDIT_REPORT_FILE, "w") as f:
        f.write("# Scheduled Codebase Audit Report\n")
        f.write(f"**Date**: {AUDIT_DATE}\n")
        f.write("**Auditor**: Jules (AI Agent)\n")
        f.write("**Scope**: `dspy_integration/` framework and modules\n\n")

        f.write("## 1. Executive Summary\n")
        # Dynamic summary
        summary = "This audit identifies several areas for improvement. "
        if FINDINGS["Performance"]:
            summary += (
                f"Critical performance bottlenecks found "
                f"({len(FINDINGS['Performance'])}). "
            )
        if FINDINGS["Architecture"]:
            summary += (
                f"Architectural inconsistencies noted "
                f"({len(FINDINGS['Architecture'])}). "
            )
        if FINDINGS["DSPy"]:
            summary += (
                f"DSPy optimization opportunities detected in "
                f"{len(FINDINGS['DSPy'])} modules. "
            )
        f.write(f"{summary}\n\n")

        f.write("## 2. Findings\n\n")
        for category, items in FINDINGS.items():
            if items:
                f.write(f"### {category}\n")
                for item in items:
                    f.write(f"* {item}\n")
                f.write("\n")

        f.write("## 3. List of Inserted TODOs\n\n")
        f.write("| File Path | Priority | Issue Description |\n")
        f.write("|-----------|----------|-------------------|\n")
        for filepath, priority, desc in INSERTED_TODOS:
            f.write(f"| `{filepath}` | {priority} | {desc} |\n")

        f.write("\n## 4. Recommendations & Roadmap\n\n")

        f.write("### Short-Term (Immediate Fixes)\n")
        if FINDINGS["Performance"]:
            f.write(
                "* **Refactor Registry**: Implement singleton pattern/caching "
                "for `CommandRegistry`.\n"
            )
        f.write("* **Fix Linting**: Address minor style issues.\n\n")

        f.write("### Medium-Term (Integration)\n")
        if FINDINGS["Architecture"]:
            f.write(
                "* **Unified Dispatch**: Update `dispatcher.py` to use "
                "`IntelligentDispatcher`.\n"
            )
        f.write(
            "* **Test Coverage**: Increase test coverage for framework "
            "components.\n\n"
        )

        f.write("### Long-Term (Evolution)\n")
        if FINDINGS["DSPy"]:
            f.write(
                "* **Optimization Pipeline**: Systematically apply "
                "`BootstrapFewShot` to all modules.\n"
            )
        f.write(
            "* **Agentic Workflow**: Move towards fully autonomous agent "
            "workflows.\n"
        )


def main():
    print("Starting audit...")
    check_registry_performance()
    check_dispatcher_architecture()
    check_dspy_modules()
    generate_report()
    print(f"Audit complete. Report generated at {AUDIT_REPORT_FILE}")


if __name__ == "__main__":
    main()
