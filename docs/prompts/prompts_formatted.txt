# Jules MCP Task Prompts - EmailIntelligence Project
# Extracted from jules_mcp_schedule.json (commit 4db2a3b7)
# Copy and paste these prompts directly into Jules command line

## Task 1: Recover Lost Backend Modules and Features (CRITICAL - Foundation)
Execute Task 1: Recover Lost Backend Modules and Features. Begin by creating a comprehensive list of expected features and modules based on the PRD. Use Git commands to audit the repository's history for lost code. Key commands: `git reflog`, `git log --diff-filter=D --summary`, `git log -S'<unique_code_string>'`. Once found, use `git checkout <commit_hash> -- <file_path>` or `git cherry-pick <commit_id>` to restore the code into a dedicated recovery branch. All recovered code must be documented in `docs/recovery_log.md`. Focus on scientific branch which contains the most advanced backend implementation.

## Task 2: Backend Migration from 'backend' to 'src/backend' (CRITICAL - Foundation)
Execute Task 2: Backend Migration from 'backend' to 'src/backend'. Create a new branch from the scientific branch (which contains the most advanced backend implementation with 20+ modules, AI/NLP features, security enhancements, and comprehensive testing). Physically move the entire `backend` directory into `src/` and rename it to `src/backend`. Perform a project-wide find-and-replace to update all Python import statements from `from backend...` to `from src.backend...`. Update configuration files (PYTHONPATH in Dockerfiles, docker-compose.yml, CI/CD scripts). Run full test suite and perform application smoke test. Delete original top-level `backend` directory.

## Task 11.1: Refactor High-Complexity AI Modules (HIGH - Core Enhancement)
Execute Task 11.1: Refactor High-Complexity AI Modules. Work in scientific branch which contains advanced AI modules (smart_filters.py 1598 lines, smart_retrieval.py 1198 lines) with comprehensive testing framework. Break down monolithic smart_filters.py and smart_retrieval.py into modular packages. Extract rule_parsers.py, filter_evaluators.py, data_transformers.py from smart_filters.py. Extract query_builders.py, ranking_algorithms.py, source_integrations.py from smart_retrieval.py. Implement dependency injection and maintain 100% test coverage using scientific's testing framework. Run unit tests for each new module and integration tests for refactored functionality.

## Task 11.2: Integrate Backend Migration (HIGH - Core Enhancement)
Execute Task 11.2: Integrate Backend Migration. Work in scientific branch which contains 20+ advanced backend modules, comprehensive testing suite, and migration-ready structure. Validate migration completeness using scientific's advanced backend (20+ modules), update import references, merge to scientific, run full test suite. Perform import validation, regression testing, and functionality verification using scientific's comprehensive testing infrastructure.

## Task 11.3: Leverage Scientific Security Framework (HIGH - Core Enhancement)
Execute Task 11.3: Leverage Scientific Security Framework. Work in scientific branch which contains advanced security framework (security_manager.py, RBAC, MFA, node engine security, audit logging). Review and integrate scientific's security_manager.py, authentication enhancements, and audit logging. Implement RBAC, MFA, session management, and auditing. Add any missing security features from main branch. Run security unit tests and integration tests using scientific's security test suite.

## Task 11.4: Security Testing & Validation (HIGH - Core Enhancement)
Execute Task 11.4: Security Testing & Validation. Work in scientific branch which contains comprehensive security testing suite, vulnerability scanning tools, and compliance validation framework. Leverage scientific's security test suite, vulnerability scanning, compliance validation, audit verification. Implement automated security scans, manual testing, and compliance audits using scientific's testing framework.

## Task 11.5: Comprehensive Testing Integration (HIGH - Core Enhancement)
Execute Task 11.5: Comprehensive Testing Integration. Work in scientific branch which contains 90+ test files, comprehensive testing infrastructure, and advanced test automation framework. Review scientific's testing framework, ensure 90%+ coverage maintained, add missing tests, integrate API and performance testing. Implement coverage reports, automated test execution, and regression prevention using scientific's advanced testing infrastructure.

## Task 11.6: CI/CD Pipeline Enhancement (MEDIUM - Integration)
Execute Task 11.6: CI/CD Pipeline Enhancement. Work in scientific branch which contains orchestration system, monitoring dashboard, and advanced CI/CD workflow automation. Leverage scientific's orchestration tools, enhance GitHub Actions, integrate scientific's monitoring dashboard. Implement automated testing, deployment procedures, and rollback capabilities. Perform pipeline validation, deployment testing, and rollback verification using scientific's monitoring infrastructure.

## Task 11.7: Database Performance Optimization (MEDIUM - Performance)
Execute Task 11.7: Database Performance Optimization. Work in scientific branch which contains performance_monitor.py, advanced database optimization tools, and monitoring infrastructure. Leverage scientific's performance_monitor.py, optimize queries, implement connection pooling, enhance caching. Perform performance benchmarks, query analysis, and load testing using scientific's monitoring tools.

## Task 11.8: AI Engine Performance Optimization (MEDIUM - Performance)
Execute Task 11.8: AI Engine Performance Optimization. Work in scientific branch which contains AI training routes, model management system, and advanced AI performance monitoring tools. Leverage scientific's AI training routes, implement batch processing, optimize memory usage. Perform inference benchmarks, memory profiling, and concurrent load testing using scientific's AI monitoring infrastructure.

## Task 11.9: System Monitoring & Alerting (MEDIUM - Performance)
Execute Task 11.9: System Monitoring & Alerting. Work in scientific branch which contains orchestration status monitoring, comprehensive alerting system, and incident response automation. Utilize scientific's orchestration status monitoring, implement performance monitoring dashboard, and alerting system. Perform monitoring validation, alert testing, and incident simulation using scientific's monitoring infrastructure.

---

## Execution Strategy Summary

**Phase 1 - Foundation (Sequential - 3-5 days):**
1. Task 1: Recover Lost Backend Modules and Features
2. Task 2: Backend Migration from 'backend' to 'src/backend'

**Phase 2 - Core Enhancement (Parallel - 8-12 days):**
- 11.1: Refactor High-Complexity AI Modules
- 11.2: Integrate Backend Migration
- 11.3: Leverage Scientific Security Framework
- 11.4: Security Testing & Validation
- 11.5: Comprehensive Testing Integration

**Phase 3 - Performance & Integration (Parallel/Sequential - 6-9 days):**
- 11.6: CI/CD Pipeline Enhancement (Sequential)
- 11.7: Database Performance Optimization (Parallel)
- 11.8: AI Engine Performance Optimization (Parallel)
- 11.9: System Monitoring & Alerting (Parallel)

**Total Timeline: 16-25 days**
**Max Concurrent Tasks: 3**
**Primary Branch: scientific**
**Quality Gates: 90% test coverage, security scans, performance benchmarks**

---

## Quick Start Commands for Jules

# Start with foundation tasks (sequential)
jules "Execute Task 1: Recover Lost Backend Modules and Features. Begin by creating a comprehensive list of expected features and modules based on the PRD. Use Git commands to audit the repository's history for lost code. Key commands: `git reflog`, `git log --diff-filter=D --summary`, `git log -S'<unique_code_string>'`. Once found, use `git checkout <commit_hash> -- <file_path>` or `git cherry-pick <commit_id>` to restore the code into a dedicated recovery branch. All recovered code must be documented in `docs/recovery_log.md`. Focus on scientific branch which contains the most advanced backend implementation."

# Then migration
jules "Execute Task 2: Backend Migration from 'backend' to 'src/backend'. Create a new branch from the scientific branch (which contains the most advanced backend implementation with 20+ modules, AI/NLP features, security enhancements, and comprehensive testing). Physically move the entire `backend` directory into `src/` and rename it to `src/backend`. Perform a project-wide find-and-replace to update all Python import statements from `from backend...` to `from src.backend...`. Update configuration files (PYTHONPATH in Dockerfiles, docker-compose.yml, CI/CD scripts). Run full test suite and perform application smoke test. Delete original top-level `backend` directory."