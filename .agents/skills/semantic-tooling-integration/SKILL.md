# Semantic Tooling Integration Skill

## SKILL.md

<|start|>SKILL<|end|>
<|begin|YAML<|begin|>---
name: semantic-tooling-integration
description: This skill should be used when the user asks to "analyze semantic gaps in codebase", "identify missing Tree-sitter/LSP tools", "analyze V8 semantic scaffold", "generate semantic tooling implementation plan", "check semantic validation readiness", or "audit semantic tooling requirements".
---

## Purpose

This skill provides a systematic approach to analyze and implement semantic tooling for codebases that require advanced code understanding beyond basic syntax analysis. It identifies missing semantic tools (Tree-sitter, LSP, AST analyzers) and creates implementation plans to bridge these gaps.

## When to Use

Use this skill when:

- You need to analyze semantic tooling gaps in a codebase
- You want to implement Tree-sitter/LSP integration for code understanding
- You're analyzing a semantic scaffold that's missing critical components
- You need to validate semantic tooling readiness for codebase analysis
- You're auditing semantic validation requirements for code understanding systems

## How OpenHands Uses This Skill

When a user asks to analyze semantic gaps or implement semantic tooling, OpenHands will:

1. Load this skill to understand the systematic approach
2. Follow the gap analysis process to identify missing components
3. Generate implementation plans for Tree-sitter/LSP integration
4. Create verification tests for semantic readiness
5. Provide implementation instructions for semantic tooling

## Process Overview

### 1. Gap Analysis

- Identify semantic tooling components (Tree-sitter, LSP, AST analyzers)
- Check current implementation status
- Compare against semantic validation requirements

### 2. Implementation Planning

- Determine required dependencies and installation steps
- Design integration with existing workflows
- Create test cases for semantic validation
- Generate implementation instructions

### 4. Verification

- Create test scenarios for semantic tooling readiness
- Develop validation scripts to check tooling functionality
- Generate post-fix verification reports

## Required Resources

### Core Components

- Tree-sitter parser integration
- Language Server Protocol (LSP) server
- AST analysis utilities
- Semantic validation framework

### Dependencies

- Tree-sitter JavaScript/TypeScript
- LSP server (e.g., pygls, pyright)
- AST parsing libraries
- Code understanding frameworks

### Output Files

- Implementation plan documentation
- Installation scripts for dependencies
- Verification test cases
- Semantic gap analysis report

## Implementation Steps

### Step 1: Gap Analysis

1. Scan codebase for semantic tooling components
2. Check current implementation status
3. Identify missing semantic components
4. Document current validation readiness

### Step 2: Dependency Assessment

1. Identify required dependencies
2. Check version compatibility
3. Create installation plan

### Step 3: Implementation Plan

1. Design integration architecture
2. Create installation scripts
3. Document configuration requirements
4. Generate test scenarios

### Step 4: Verification

1. Create test scenarios
2. Develop validation scripts
3. Generate post-fix reports

## Implementation Resources

### Scripts Directory

- `scripts/gap-analysis.py` - Gap analysis script
- `scripts/install-dependencies.sh` - Dependency installation script
- `scripts/validate-semantic.sh` - Semantic validation script

### Reference Files

- `references/semantic-patterns.md` - Common semantic patterns
- `references/validation-checklist.md` - Semantic validation checklist
- `references/implementation-patterns.md` - Integration patterns

### Assets Directory

- `assets/implementation-plan-template.md` - Implementation plan template
- `assets/verification-report.md` - Verification report template

## Writing Style

- Use imperative/infinitive form in instructions (verb-first)
- Keep SKILL.md body under 2,000 words
- Move detailed content to references/
- Include specific trigger phrases in description
- Use third-person in description
- Maintain objective, instructional tone

## Example Usage

When a user asks to analyze semantic gaps in a V8 graphite agent:

> "Analyze semantic gaps in the graphite agent V8 implementation"

OpenHands will:

1. Load this skill
2. Analyze the V8 semantic scaffold
3. Identify missing Tree-sitter/LSP components
4. Create implementation plan with scripts and tests
5. Generate verification report
6. Provide step-by-step implementation instructions

<|end|>SKILL<|end|>
