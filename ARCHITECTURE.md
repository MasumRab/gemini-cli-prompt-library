# Architecture Documentation

This document describes the architecture of the Gemini CLI Prompt Library with DSPy integration.

TODO: Add architecture diagrams showing component relationships
TODO: Include performance benchmarks and scalability information
TODO: Document the testing strategy and coverage targets
TODO: Add security considerations and best practices
TODO: Include deployment guidelines for different environments
TODO: Add troubleshooting and debugging guidelines
TODO: Document API contracts and versioning strategy

## Overview

The Gemini CLI Prompt Library is a comprehensive framework for managing and executing AI prompts through a command-line interface. It supports both traditional TOML-based prompts and advanced DSPy modules for optimization and evaluation.

## Components

### 1. Command Infrastructure
- **commands/**: Contains all TOML-based prompt definitions
- **commands_manifest.json**: Defines the mapping between command names and descriptions
- **Command Registry**: Dynamically discovers and registers commands

### 2. DSPy Integration
- **dspy_integration/**: Core DSPy integration package
- **dspy_integration/modules/**: DSPy modules for various scenarios (code review, documentation, etc.)
- **dspy_integration/framework/**: Evaluation and optimization framework
- **dspy_integration/cli.py**: CLI entry point for DSPy operations

### 3. Framework Components
- **Framework Core**: Provides evaluation, optimization, and provider management
- **Scenarios**: Defines evaluation scenarios for different prompt types
- **Providers**: Implements multiple LLM providers with failover capabilities
- **Optimizers**: Implements DSPy optimization algorithms (MIPROv2, BootstrapFewShot)

### 4. TOML Integration
- **TOML Manager**: Loads and executes prompts from TOML files
- **Variable Substitution**: Handles {{variable}} replacement in prompts
- **Fallback System**: Falls back to DSPy if TOML processing fails

## Key Features

### Multi-Provider Support
- Automatic failover between providers
- Rate limit management
- Cost optimization (free tier prioritization)

### Optimization Capabilities
- MIPROv2 for advanced prompt optimization
- BootstrapFewShot for few-shot learning
- Custom evaluation metrics

### Extensibility
- Plugin architecture for new scenarios
- Dynamic command discovery
- Modular provider system

## Data Flow

1. User executes command: `gemini-cli prompts:improve "my prompt"`
2. Command router identifies appropriate handler
3. Handler loads prompt from TOML or DSPy module
4. Prompt is processed with user input
5. Result is returned to user

## Configuration

Configuration is managed through:
- Environment variables for API keys
- FrameworkConfig class for provider/model settings
- Per-command TOML files for prompt definitions

## Testing and Evaluation

The framework includes:
- Built-in evaluation metrics
- Scenario-based testing
- Performance benchmarks
- Quality assurance tools