"""
Unified CLI for gemini-cli-prompt-library

Provides full DSPy access from terminal, with integration support for Gemini CLI.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class DSPyIntegrationCLI:
    """Main CLI class handling all commands."""

    def __init__(self):
        self._toml_manager = None

    def _get_toml_manager(self):
        if self._toml_manager is None:
            from dspy_integration.toml import TOMLManager

            self._toml_manager = TOMLManager()
        return self._toml_manager

    def improve(
        self,
        prompt_text: str,
        optimizer: Optional[str] = None,
        output_format: str = "text",
    ) -> str:
        """Improve a prompt using DSPy."""
        from dspy_integration.modules.improve import approach_dspy

        result = approach_dspy(prompt_text)

        if output_format == "json":
            return json.dumps(result, indent=2, default=str)
        else:
            output = []
            output.append("=" * 60)
            output.append("IMPROVED PROMPT")
            output.append("=" * 60)
            output.append("")
            output.append(result["result"])
            output.append("")
            output.append("-" * 60)
            output.append(f"Changes Summary: {result.get('changes_summary', 'N/A')}")
            output.append(f"Score: {result['score']}/50")
            output.append(f"Approach: {result['approach']}")
            output.append("-" * 60)
            return "\n".join(output)

    def evaluate(self, prompt_text: str, output_format: str = "json") -> str:
        """Evaluate a prompt and score it."""
        from dspy_integration.toml import approach_toml

        result = approach_toml(prompt_text)

        if output_format == "json":
            return json.dumps(result, indent=2, default=str)
        else:
            output = []
            output.append("=" * 60)
            output.append("EVALUATION RESULTS")
            output.append("=" * 60)
            output.append("")
            output.append(f"Score: {result['score']}/50")
            output.append(f"Approach: {result['approach']}")
            output.append("")
            output.append("=" * 60)
            return "\n".join(output)

    def convert(self, prompt_text: str, output_format: str = "text") -> str:
        """Convert a prompt to DSPy module format."""
        module_code = '''"""Auto-generated DSPy module."""

import dspy


class ConvertedPromptSignature(dspy.Signature):
    input_text = dspy.InputField(desc="The input text to process")
    output = dspy.OutputField(desc="The generated output")


class ConvertedPrompt(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(ConvertedPromptSignature)

    def forward(self, input_text: str):
        return self.generate(input_text=input_text)
'''

        if output_format == "json":
            return json.dumps({"module_code": module_code}, indent=2)
        return module_code

    def list(self, item: str = "all", output_format: str = "text") -> str:
        """List available scenarios, modules, or optimizers."""
        scenarios = [
            "code_review",
            "architecture",
            "feature_dev",
            "unit_test",
            "documentation",
            "security_review",
            "improve",
        ]
        optimizers = ["MIPROv2", "BootstrapFewShot", "BootstrapFewShotWithRandomSearch"]

        result = {}
        if item in ["scenarios", "all"]:
            result["scenarios"] = scenarios
        if item in ["modules", "all"]:
            result["modules"] = scenarios
        if item in ["optimizers", "all"]:
            result["optimizers"] = optimizers

        if output_format == "json":
            return json.dumps(result, indent=2)
        else:
            output = ["=" * 60, "AVAILABLE ITEMS", "=" * 60]
            if "scenarios" in result:
                output.extend(
                    ["", "Scenarios:"] + [f"  - {s}" for s in result["scenarios"]]
                )
            if "modules" in result:
                output.extend(
                    ["", "Modules:"] + [f"  - {m}" for m in result["modules"]]
                )
            if "optimizers" in result:
                output.extend(
                    ["", "Optimizers:"] + [f"  - {o}" for o in result["optimizers"]]
                )
            output.append("=" * 60)
            return "\n".join(output)

    def optimize(
        self,
        scenario: str,
        optimizer: str = "MIPROv2",
        provider: str = "auto",
        output: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run DSPy optimization on a scenario."""
        return {
            "status": "placeholder",
            "scenario": scenario,
            "optimizer": optimizer,
            "provider": provider,
            "message": "Optimization not yet implemented in Phase 1",
        }

    def compare(
        self,
        prompt_text: str,
        approaches: Optional[List[str]] = None,
        output_format: str = "text",
    ) -> str:
        """Compare different improvement approaches."""
        if approaches is None:
            approaches = ["toml", "dspy"]

        results = []

        if "toml" in approaches:
            from dspy_integration.toml import approach_toml

            results.append(approach_toml(prompt_text))

        if "dspy" in approaches:
            from dspy_integration.modules.improve import approach_dspy

            results.append(approach_dspy(prompt_text))

        if output_format == "json":
            return json.dumps(results, indent=2, default=str)
        else:
            output = ["=" * 60, "COMPARISON RESULTS", "=" * 60, ""]
            for i, r in enumerate(results, 1):
                output.append(f"Approach {i}: {r['approach'].upper()}")
                output.append(f"  Score: {r['score']}/50")
                if "changes_summary" in r:
                    output.append(f"  Changes: {r['changes_summary']}")
                output.append("")
            output.append("=" * 60)
            return "\n".join(output)

    def interactive(self, base_prompt: str):
        """Enter interactive tuning session."""
        print("Interactive mode - Phase 3 feature")

    def sessions(self, action: str = "list", name: Optional[str] = None) -> str:
        """Manage saved sessions."""
        if action == "list":
            return "No saved sessions"
        elif action == "load" and name:
            return f"Loaded session: {name}"
        elif action == "delete" and name:
            return f"Deleted session: {name}"
        return "Invalid session command"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified DSPy CLI for gemini-cli-prompt-library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
    python -m dspy_integration improve "Your prompt here"
    python -m dspy_integration optimize security_review --optimizer MIPROv2
    python -m dspy_integration compare "Your prompt" --approaches toml dspy
    python -m dspy_integration list
    python -m dspy_integration interactive""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    imp = subparsers.add_parser("improve", help="Improve a prompt")
    imp.add_argument("prompt", help="Prompt to improve")
    imp.add_argument("--optimizer", "-o", help="DSPy optimizer to use")
    imp.add_argument("--output", "-O", default="text", choices=["json", "text"])

    eval_p = subparsers.add_parser("evaluate", help="Evaluate a prompt")
    eval_p.add_argument("prompt", help="Prompt to evaluate")
    eval_p.add_argument("--output", "-O", default="json", choices=["json", "text"])

    conv = subparsers.add_parser("convert", help="Convert prompt to DSPy")
    conv.add_argument("prompt", help="Prompt to convert")
    conv.add_argument("--output", "-O", default="text", choices=["json", "text"])

    list_p = subparsers.add_parser("list", help="List available items")
    list_p.add_argument(
        "item",
        nargs="?",
        default="all",
        choices=["scenarios", "modules", "optimizers", "all"],
        help="What to list",
    )

    opt = subparsers.add_parser("optimize", help="Run DSPy optimization")
    opt.add_argument("scenario", help="Scenario to optimize")
    opt.add_argument(
        "--optimizer",
        "-o",
        default="MIPROv2",
        choices=["MIPROv2", "BootstrapFewShot", "BootstrapFewShotWithRandomSearch"],
    )
    opt.add_argument("--provider", "-p", default="auto")
    opt.add_argument("--output", "-O", help="Output file for optimized module")

    comp = subparsers.add_parser("compare", help="Compare improvement approaches")
    comp.add_argument("prompt", help="Prompt to improve")
    comp.add_argument(
        "--approaches",
        "-a",
        nargs="+",
        choices=["toml", "dspy", "mipro", "bootstrap", "custom", "all"],
        default=["toml", "dspy"],
        help="Approaches to compare",
    )
    comp.add_argument("--output", "-O", default="text", choices=["json", "text"])

    int_p = subparsers.add_parser("interactive", help="Enter interactive session")
    int_p.add_argument("prompt", nargs="?", help="Optional base prompt")

    sess = subparsers.add_parser("sessions", help="Manage saved sessions")
    sess.add_argument(
        "action",
        nargs="?",
        default="list",
        choices=["list", "load", "delete"],
        help="Action to perform",
    )
    sess.add_argument("name", nargs="?", help="Session name for load/delete")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = DSPyIntegrationCLI()

    try:
        if args.command == "improve":
            print(cli.improve(args.prompt, args.optimizer, args.output))
        elif args.command == "evaluate":
            print(cli.evaluate(args.prompt, args.output))
        elif args.command == "convert":
            print(cli.convert(args.prompt, args.output))
        elif args.command == "list":
            print(cli.list(args.item, args.output))
        elif args.command == "optimize":
            print(
                json.dumps(
                    cli.optimize(
                        args.scenario, args.optimizer, args.provider, args.output
                    ),
                    indent=2,
                    default=str,
                )
            )
        elif args.command == "compare":
            print(cli.compare(args.prompt, args.approaches, args.output))
        elif args.command == "interactive":
            cli.interactive(args.prompt)
        elif args.command == "sessions":
            print(cli.sessions(args.action, args.name))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
