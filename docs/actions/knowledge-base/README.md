# Jules GitHub Actions Knowledge Base

## Knowledge Base Purpose and Scope

This knowledge base serves as a comprehensive reference for GitHub Actions workflows specifically designed for the Jules AI agent system. It contains reusable workflow templates, best practices, and standardized patterns for CI/CD pipelines that integrate with Jules' capabilities.

### Purpose
- Provide standardized GitHub Actions workflows for Jules-related projects
- Document best practices for automating Jules development workflows
- Enable consistent CI/CD processes across all Jules repositories
- Facilitate knowledge sharing about Jules-specific automation patterns

### Scope
- Workflow templates for testing, building, and deploying Jules components
- Automation patterns for Jules skill development and maintenance
- Integration workflows with external services used by Jules
- Documentation and examples for Jules-specific GitHub Actions usage
- Guidelines for contributing to and maintaining this knowledge base

## How to Use This Knowledge Base

### For Developers
1. **Finding Workflows**: Browse the directory structure to find workflow templates relevant to your needs
2. **Using Templates**: Copy workflow files to your project's `.github/workflows/` directory
3. **Customizing**: Modify workflow parameters to match your project's specific requirements
4. **Contributing**: Follow the maintenance process to add new workflows or improve existing ones

### For Maintainers
1. **Review Process**: All new workflows should follow established patterns and conventions
2. **Documentation**: Ensure new additions include clear usage instructions
3. **Testing**: Validate workflows in test environments before promoting to production
4. **Updates**: Periodically review workflows for improvements and deprecations

## Directory Structure Overview

```
jules/docs/actions/knowledge-base/
├── README.md                 # This file
├── workflows/                # Ready-to-use workflow templates
│   ├── ci.yml                # Continuous Integration workflows
│   ├── cd.yml                # Continuous Deployment workflows
│   ├── testing.yml           # Testing workflows
│   └── deployment.yml        # Deployment workflows
├── patterns/                 # Reusable workflow patterns and snippets
│   ├── setup-jules.yml       # Jules environment setup
│   ├── test-jules.yml        # Jules testing patterns
│   └── deploy-jules.yml      # Jules deployment patterns
├── examples/                 # Complete workflow examples
│   ├── skill-development.yml # Example: Jules skill development workflow
│   ├── model-training.yml    # Example: Model training workflow
│   └── agent-deployment.yml  # Example: Agent deployment workflow
├── guides/                   # Detailed guides and tutorials
│   ├── getting-started.md    # Getting started with Jules workflows
│   ├── best-practices.md     # Best practices for Jules automation
│   └── troubleshooting.md    # Common issues and solutions
└── templates/                # Workflow template files for generation
    ├── workflow-template.yml
    └── action-template.yml
```

## Quick Reference: Jules Workflow Families

### Continuous Integration (CI)
- **ci.yml**: Runs tests, linting, and validation on every pull request
- **testing.yml**: Comprehensive test suite execution including unit, integration, and end-to-end tests
- **security.yml**: Security scanning and vulnerability assessment workflows

### Continuous Deployment (CD)
- **cd.yml**: Automated deployment to staging and production environments
- **deployment.yml**: Environment-specific deployment workflows
- **release.yml**: Release management and versioning workflows

### Jules-Specific Workflows
- **skill-development.yml**: Workflows for developing, testing, and publishing Jules skills
- **model-training.yml**: Workflows for training and validating Jules AI models
- **agent-deployment.yml**: Workflows for deploying and managing Jules agents
- **documentation.yml**: Workflows for generating and publishing Jules documentation

### Utility Workflows
- **cleanup.yml**: Resource cleanup and maintenance workflows
- **monitoring.yml**: Health checks and performance monitoring workflows
- **notification.yml**: Alerting and notification workflows

### Canonical Workflows (Currently Documented)
1. `jules-pr-review.yml` - Auto PR review + deferred (993 lines)
2. `jules-pr-force-review.yml` - Manual label/slash review + deferred (920 lines)
3. `jules-pr-auto-fix.yml` - Two-phase plan/approve fixes (985 lines)
4. `jules-pr-walkthrough.yml` - Architectural walkthrough (482 lines)
5. `jules-pr-address-comments.yml` - Forward unresolved threads to Jules (270 lines)
6. `jules-pr-resolve-conflicts.yml` - Stability watch + conflict resolution (648 lines)
7. `jules-pr-rebuild.yml` - Two-session analyze → rebuild in-place (559 lines)
8. `jules-pr-automerge-label.yml` - Hourly auto-merge labeling (78 lines)
9. `jules-dispatch.yml` - Central @jules command router (119 lines)
10. `jules-issue-triage.yml` - Single + batch issue triage (305 lines)
11. `jules-backlog-review.yml` - Weekly stale PR functional review (296 lines)

### Shared Component
- `.github/scripts/jules-comment-classifier.cjs` (398 lines) - Loaded from trusted base branch

## Related Documentation Links

- [Jules Documentation](https://github.com/masum/github/remote/jules/README.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jules Skills Development Guide](https://github.com/masum/github/remote/jules/docs/skills/development.md)
- [Jules Architecture Overview](https://github.com/masum/github/remote/jules/ARCHITECTURE.md)
- [Jules Contributing Guidelines](https://github.com/masum/github/remote/jules/CONTRIBUTING.md)
- [Jules Best Practices](https://github.com/masum/github/remote/jules/docs/best-practices.md)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/security-guides-for-github-actions)
- [Jules Workflow Examples Repository](https://github.com/masum/github/remote/jules/examples/workflows)

## Maintenance and Update Process

### Adding New Workflows
1. **Create Workflow**: Develop new workflow in the appropriate directory
2. **Document**: Add clear usage instructions and examples
3. **Test**: Validate workflow functionality in a test repository
4. **Review**: Submit for review following Jules contribution guidelines
5. **Publish**: Merge to main branch after approval

### Updating Existing Workflows
1. **Identify Need**: Determine what requires updating (bug fixes, improvements, deprecations)
2. **Create Branch**: Work from the latest main branch
3. **Implement Changes**: Make necessary modifications
4. **Test**: Verify changes don't break existing functionality
5. **Document Updates**: Update any relevant documentation
6. **Submit**: Create pull request for review

### Deprecation Process
1. **Announce**: Mark workflow as deprecated with clear timeline
2. **Provide Alternatives**: Suggest replacement workflows or approaches
3. **Maintain**: Keep deprecated workflow functional but unsupported during notice period
4. **Remove**: Remove workflow after deprecation period ends

### Versioning
- Workflows follow semantic versioning when appropriate
- Major changes that break compatibility require major version bump
- Minor improvements and bug fixes use minor version increments
- Documentation updates use patch version increments

### Review Criteria
- Follows Jules coding standards and conventions
- Includes proper error handling and logging
- Uses appropriate permissions and security practices
- Well-documented with clear usage instructions
- Tested and verified to work as expected
- Follows GitHub Actions best practices

---

*Last updated: August 2026*
*Maintained by the Jules team*