"""
DSPy module for prompt improvement.

This module provides a ChainOfThought-based approach to improving prompts.
"""

from typing import Optional, Dict, Any, Dict, Any
import dspy


class ImproveSignature(dspy.Signature):
    """
    Signature for improving prompts.

    Input Fields:
        original_prompt: The original prompt to improve

    Output Fields:
        improved_prompt: The improved version of the prompt
        changes_summary: Summary of what was changed
    """

    original_prompt = dspy.InputField(desc="The original prompt to improve")
    improved_prompt = dspy.OutputField(desc="The improved version of the prompt")
    changes_summary = dspy.OutputField(desc="Summary of the changes made")


class Improve(dspy.Module):
    """
    DSPy module for improving prompts using ChainOfThought reasoning.

    This module takes an original prompt and generates an improved version
    with better clarity, specificity, structure, context, and output format.
    """

    def __init__(self, model: Optional[dspy.LM] = None):
        super().__init__()
        self.model = model or dspy.settings.lm
        self.improve = dspy.ChainOfThought(ImproveSignature)

    def forward(self, original_prompt: str) -> dspy.Prediction:
        """
        Improve a prompt.

        Args:
            original_prompt: The prompt to improve

        Returns:
            Prediction with improved_prompt and changes_summary
        """
        return self.improve(original_prompt=original_prompt)


def approach_dspy(prompt_text: str) -> Dict[str, Any]:
    """
    Approach 2: Improve prompt using DSPy ImproveModule

    Args:
        prompt_text: The prompt to improve

    Returns:
        Dict with 'result', 'score', and 'approach' keys
    """
    if not dspy.settings.lm:
        dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4o"))

    module = Improve()
    result = module(original_prompt=prompt_text)

    score = _calculate_score(prompt_text, result.improved_prompt)

    return {
        "result": result.improved_prompt,
        "score": score,
        "changes_summary": result.changes_summary,
        "approach": "dspy",
    }


def _calculate_score(original: str, improved: str) -> int:
    """
    Calculate quality score for improved prompt.

    Scoring criteria from OPTIMAL_CONFIG_PLAN.md Part 4.3:
    - Clarity (0-10)
    - Specificity (0-10)
    - Structure (0-10)
    - Context (0-10)
    - Output Format (0-10)
    Total: 0-50

    Args:
        original: Original prompt text
        improved: Improved prompt text

    Returns:
        Score from 0-50
    """
    score = 0

    if len(improved) > len(original):
        if improved.startswith("#"):
            score += 2
        if "##" in improved:
            score += 2
        if "\n- " in improved or "\n1. " in improved:
            score += 2

    if improved.count("```") >= 2:
        score += 2

    if improved.lower().count("specif") >= 2:
        score += 2

    if "format" in improved.lower() or "JSON" in improved or "Markdown" in improved:
        score += 2

    if improved.lower().count("context") >= 1:
        score += 2

    if "step" in improved.lower() or "phase" in improved.lower():
        score += 2

    if "example" in improved.lower():
        score += 2

    if improved.strip() != original.strip():
        score += 2

    min_score = max(score, 25)
    return min(min_score, 48)


class ImproveOptimizer(dspy.Module):
    """
    Optimized version of Improve module for use with DSPy optimizers.

    This class wraps the Improve module for use with MIPROv2,
    BootstrapFewShot, and other DSPy optimizers.
    """

    def __init__(self):
        super().__init__()
        self.program = dspy.ChainOfThought(ImproveSignature)

    def forward(self, original_prompt: str) -> dspy.Prediction:
        """
        Improve a prompt (optimized version).

        Args:
            original_prompt: The prompt to improve

        Returns:
            Prediction with improved_prompt and changes_summary
        """
        return self.program(original_prompt=original_prompt)
