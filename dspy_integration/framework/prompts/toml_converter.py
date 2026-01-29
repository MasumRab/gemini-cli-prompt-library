"""
TOML to DSPy converter.

This module provides functionality to convert TOML prompt definitions to DSPy modules.
"""

import re
from typing import Dict, Any, Optional
import tomllib
from pathlib import Path


def convert_toml_to_dspy(toml_path: str) -> str:
    """
    Convert a TOML prompt definition to a DSPy module.
    
    Args:
        toml_path: Path to the TOML file containing the prompt
        
    Returns:
        String representation of the DSPy module
    """
    path = Path(toml_path)
    content = path.read_text()
    data = tomllib.loads(content)
    
    prompt_template = data.get("prompt", "")
    description = data.get("description", "")
    variables = _extract_variables(prompt_template)
    
    # Generate the DSPy module code
    module_code = _generate_dspy_module(
        path.stem, 
        description, 
        prompt_template, 
        variables
    )
    
    return module_code


def _extract_variables(prompt_template: str) -> list:
    """
    Extract {{variable}} patterns from prompt template.
    
    Args:
        prompt_template: The prompt template string
        
    Returns:
        List of variable names (without braces)
    """
    pattern = r"\{\{(\w+)\}\}"
    matches = re.findall(pattern, prompt_template)
    return list(set(matches))


def _generate_dspy_module(
    name: str, 
    description: str, 
    prompt_template: str, 
    variables: list
) -> str:
    """
    Generate DSPy module code from prompt information.
    
    Args:
        name: Name of the module
        description: Description of the prompt
        prompt_template: The prompt template
        variables: List of variables in the prompt
        
    Returns:
        String representation of the DSPy module
    """
    # Capitalize the name for the class
    class_name = "".join(word.capitalize() for word in name.split("_"))
    if not class_name.endswith("Module"):
        class_name += "Module"
    
    # Generate input/output fields
    input_fields = []
    output_fields = []
    
    # Assume the first variable is the main input
    if variables:
        main_var = variables[0]
        input_fields.append(f'    {main_var} = dspy.InputField(desc="The {main_var} to process")')
    
    # For output fields, we'll add common ones
    output_fields.append(f'    result = dspy.OutputField(desc="The result of the {name} operation")')
    
    # Add additional output fields based on common patterns
    if "improve" in name.lower():
        output_fields.append('    changes_summary = dspy.OutputField(desc="Summary of changes made")')
    elif "review" in name.lower():
        output_fields.append('    issues_found = dspy.OutputField(desc="Issues identified in the review")')
    elif "design" in name.lower():
        output_fields.append('    design_elements = dspy.OutputField(desc="Elements of the design")')
    
    # Escape quotes in the prompt template
    escaped_prompt = prompt_template.replace('"', '\\"').replace('\n', '\\n')
    
    module_code = f'''"""
DSPy module for {name}.

This module implements the {name} functionality using DSPy.
"""

import dspy


class {class_name}Signature(dspy.Signature):
    """
    Signature for {name} module.
    """
'''
    
    if input_fields:
        module_code += "\n".join(input_fields) + "\n"
    
    if output_fields:
        module_code += "\n".join(output_fields) + "\n"
    
    module_code += f'''

class {class_name}(dspy.Module):
    """
    DSPy module for {name}.
    
    {description}
    """

    def __init__(self):
        super().__init__()
        self.signature = {class_name}Signature
        self.predictor = dspy.Predict(self.signature)

    def forward(self, **kwargs):
        """
        Execute the {name} operation.
        """
        return self.predictor(**kwargs)


def create_{name}_module():
    """
    Factory function to create a {name} module.
    
    Returns:
        Instance of {class_name}
    """
    return {class_name}()
'''
    
    return module_code