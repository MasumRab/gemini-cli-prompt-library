"""
Scenario for evaluating improve prompts.

This module defines the ImproveScenario for evaluating prompt improvement tasks.
"""

from typing import List, Dict, Any, Tuple, Optional
from dspy import Example
from .base import ScenarioRegistry, BaseScenario


@ScenarioRegistry.register("improve")
class ImproveScenario(BaseScenario):
    """
    Scenario for evaluating prompt improvement tasks.

    This scenario handles the evaluation of prompt improvement modules
    by providing training/validation data and evaluation metrics.
    """

    INPUT_FIELDS = ["original_prompt"]
    OUTPUT_FIELDS = ["improved_prompt", "changes_summary"]

    def __init__(self):
        """Initialize the ImproveScenario."""
        self.train_data = []
        self.val_data = []
        self._load_data()

    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """
        Load raw data for the improve scenario.
        
        Returns:
            List of dictionaries containing original and improved prompts
        """
        # Sample data for training and validation
        sample_data = [
            {
                "original_prompt": "Write a function that adds two numbers.",
                "improved_prompt": "# Function to Add Two Numbers\n\nCreate a function that takes two numeric inputs and returns their sum.\n\n## Requirements:\n- Accept two numeric parameters\n- Return the sum of the parameters\n- Handle integer and float inputs\n\n## Example:\n```python\ndef add_numbers(a, b):\n    return a + b\n```",
                "changes_summary": "Added clear structure, requirements, and example"
            },
            {
                "original_prompt": "Fix this broken code.",
                "improved_prompt": "# Code Debugging Task\n\nIdentify and fix issues in the provided code.\n\n## Steps:\n1. Analyze the code structure\n2. Identify syntax errors\n3. Identify logical errors\n4. Propose fixes with explanations\n5. Provide corrected code\n\n## Input:\n{{code}}\n\n## Output:\n- Error descriptions\n- Fixed code\n- Explanation of fixes",
                "changes_summary": "Added structured debugging steps and clear output format"
            }
        ]
        return sample_data

    def _load_data(self):
        """
        Load and split data into train and validation sets.
        """
        raw_data = self._load_raw_data()
        
        # Simple split: 80% train, 20% validation
        split_idx = int(len(raw_data) * 0.8)
        self.train_data = [Example(**item).with_inputs(*self.INPUT_FIELDS) for item in raw_data[:split_idx]]
        self.val_data = [Example(**item).with_inputs(*self.INPUT_FIELDS) for item in raw_data[split_idx:]]

    def load_data(self) -> Tuple[List[Example], List[Example]]:
        """
        Load training and validation data.
        
        Returns:
            Tuple of (train_data, val_data) lists of Examples
        """
        return self.train_data, self.val_data

    def metric(
        self,
        example: "dspy.Example",
        pred: "dspy.Prediction",
        trace: Optional[Any] = None,
    ) -> float:
        """
        Evaluate the quality of an improved prompt.

        Scoring criteria from OPTIMAL_CONFIG_PLAN.md Part 4.3:
        - Clarity (0-10)
        - Specificity (0-10)
        - Structure (0-10)
        - Context (0-10)
        - Output Format (0-10)
        Total: 0-50

        Args:
            example: Ground truth example
            pred: Predicted result
            trace: Optional trace information

        Returns:
            Score from 0-50
        """
        # Convert pred to dict if it's a DSPy prediction object
        if hasattr(pred, 'improved_prompt'):
            improved = getattr(pred, 'improved_prompt', '')
        else:
            improved = str(pred)

        # Get original from example
        original = getattr(example, 'original_prompt', '')

        score = 0

        # Clarity: Check for headers and clear sections
        if improved.startswith("#"):
            score += 2
        if "##" in improved:
            score += 2

        # Structure: Check for lists, steps, or organized content
        if "\n- " in improved or "\n1. " in improved:
            score += 2

        # Formatting: Check for code blocks or examples
        if improved.count("```") >= 2:
            score += 2

        # Specificity: Check for specific keywords
        if improved.lower().count("specif") >= 1:
            score += 2

        # Output format: Check for format specifications
        if "format" in improved.lower() or "json" in improved.lower() or "markdown" in improved.lower():
            score += 2

        # Context: Check for context-related terms
        if improved.lower().count("context") >= 1:
            score += 2

        # Steps/process: Check for process-related terms
        if "step" in improved.lower() or "phase" in improved.lower() or "process" in improved.lower():
            score += 2

        # Examples: Check for example-related terms
        if "example" in improved.lower():
            score += 2

        # Improvement: Check if the improved prompt is significantly different
        if len(improved) > len(original) * 1.2:  # At least 20% longer
            score += 2

        # Ensure score is within bounds
        min_score = max(score, 10)  # Minimum score of 10
        return min(min_score, 50)

    def make_prompt(self, row: Dict[str, Any]) -> str:
        """
        Create an improve prompt from a data row.

        Args:
            row: Dictionary containing original prompt

        Returns:
            Formatted prompt string
        """
        return f"Improve the following prompt:\n\n{row['original_prompt']}"


# For backward compatibility
def get_improve_scenario():
    """Get an instance of the ImproveScenario."""
    return ImproveScenario()