#!/usr/bin/env python3
"""
Gemini DSPy Wrapper

This script provides a unified interface to execute DSPy-based operations
through the gemini-cli-prompt-library. It bridges traditional command execution
with advanced DSPy optimization and evaluation capabilities.
"""

import sys
import argparse
from typing import Optional, Dict, Any
from pathlib import Path

# Add the project root to the path to import modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def execute_dspy_operation(operation: str, args: str, **kwargs) -> Dict[str, Any]:
    """
    Execute a DSPy-based operation.
    
    Args:
        operation: The operation to perform (e.g., 'improve', 'review', 'optimize')
        args: Arguments for the operation
        **kwargs: Additional keyword arguments
        
    Returns:
        Dictionary with result, status, and metadata
    """
    try:
        # Import the necessary modules
        from dspy_integration.modules import get_module_for_scenario
        from dspy_integration.toml import approach_toml
        import dspy
        
        # Initialize DSPy if needed
        if not dspy.settings.lm:
            # Try to configure with a default model
            try:
                dspy.settings.configure(lm=dspy.OpenAI(model="gpt-3.5-turbo"))
            except:
                # If OpenAI fails, try another provider
                try:
                    dspy.settings.configure(lm=dspy.OllamaLocal(model="llama2"))
                except:
                    # If all else fails, create a dummy model for testing
                    pass
        
        # Map operation to DSPy scenario
        scenario_map = {
            'improve': 'improve',
            'code-review': 'code_review',
            'security-review': 'security_review',
            'unit-test': 'unit_test',
            'documentation': 'documentation',
            'architecture': 'architecture',
        }
        
        scenario_name = scenario_map.get(operation, operation)
        
        # Try to get the DSPy module for the scenario
        try:
            module = get_module_for_scenario(scenario_name)
            if module:
                # Execute the module with the provided arguments
                result = module.forward(original_prompt=args)
                return {
                    'result': result,
                    'status': 'success',
                    'operation': operation,
                    'method': 'dspy_module'
                }
        except ValueError:
            # If the scenario is not found in DSPy modules, fall back to TOML
            pass
        
        # Fall back to TOML approach if DSPy module is not available
        result = approach_toml(args)
        return {
            'result': result,
            'status': 'success',
            'operation': operation,
            'method': 'toml_fallback'
        }
        
    except Exception as e:
        return {
            'result': None,
            'status': 'error',
            'error': str(e),
            'operation': operation
        }


def main():
    parser = argparse.ArgumentParser(
        description="Gemini DSPy Wrapper - Bridge between gemini-cli and DSPy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python gemini_dspy_wrapper.py --operation improve --args "Improve this prompt: Write a function"
    python gemini_dspy_wrapper.py --operation code-review --args "Review this code: def func(): pass"
        """
    )
    
    parser.add_argument(
        '--operation', '-o',
        type=str,
        required=True,
        help='Operation to perform (e.g., improve, code-review, security-review)'
    )
    
    parser.add_argument(
        '--args', '-a',
        type=str,
        required=True,
        help='Arguments for the operation'
    )
    
    parser.add_argument(
        '--output-format',
        type=str,
        default='text',
        choices=['text', 'json'],
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Executing operation: {args.operation}")
        print(f"With args: {args.args}")
    
    result = execute_dspy_operation(args.operation, args.args)
    
    if args.output_format == 'json':
        import json
        print(json.dumps(result, indent=2, default=str))
    else:
        if result['status'] == 'success':
            print("Operation completed successfully:")
            print(f"Method used: {result['method']}")
            print(f"Result: {result['result']}")
        else:
            print(f"Operation failed: {result['error']}")
            sys.exit(1)


def improve_prompt(prompt_text: str) -> Dict[str, Any]:
    """
    Convenience function to improve a prompt using DSPy.
    
    Args:
        prompt_text: The prompt to improve
        
    Returns:
        Dictionary with improvement result
    """
    return execute_dspy_operation('improve', prompt_text)


def review_code(code_text: str) -> Dict[str, Any]:
    """
    Convenience function to review code using DSPy.
    
    Args:
        code_text: The code to review
        
    Returns:
        Dictionary with review result
    """
    return execute_dspy_operation('code-review', code_text)


def generate_tests(code_text: str) -> Dict[str, Any]:
    """
    Convenience function to generate tests for code using DSPy.
    
    Args:
        code_text: The code to generate tests for
        
    Returns:
        Dictionary with test generation result
    """
    return execute_dspy_operation('unit-test', code_text)


if __name__ == "__main__":
    main()