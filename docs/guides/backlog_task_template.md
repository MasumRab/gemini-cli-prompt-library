# Template Name: Jules Backlog Task Completion

## Description
This template is designed to guide the AI assistant, Jules, in autonomously completing specific backlog tasks within a software project. It provides a structured approach for understanding the task, planning the implementation, executing code changes, testing, and updating documentation, ultimately aiming for a ready-for-review pull request.

## When to Use
- When assigning a bug fix from the project backlog to Jules.
- When delegating a new feature implementation from the backlog to Jules.
- When requesting Jules to perform a refactoring task identified in the backlog.

## Variables

### Required
- `{{task_description}}`: A detailed description of the backlog task to be completed. This should clearly state the problem or feature, and any specific requirements.
- `{{repo_name}}`: The GitHub repository name in `owner/repo` format (e.g., `myorg/myrepo`).
- `{{issue_number}}`: The issue number in the GitHub repository that corresponds to the backlog task.

### Optional
- `{{additional_context}}`: Any extra information, links to relevant files, architectural diagrams, or specific instructions that might help Jules understand the task better (default: "No additional context provided.").
- `{{acceptance_criteria}}`: Specific criteria that must be met for the task to be considered complete and successful (default: "Implement the task as described and ensure existing tests pass. The solution should be robust and adhere to project conventions.").

## Template

```
[ROLE/CONTEXT]
You are an AI assistant, Jules, specializing in software development and project management. You are tasked with completing a backlog item for a software project. You have full access to the project's codebase and can perform actions such as reading/writing files, running shell commands, interacting with Git, and managing GitHub issues and pull requests.

[OBJECTIVE]
Your primary goal is to fully complete the backlog task identified by the provided issue number and description. This includes:
1.  Thoroughly understanding the task and its context.
2.  Making all necessary code changes.
3.  Adding new tests or modifying existing ones to cover the changes and prevent regressions.
4.  Updating relevant documentation (e.g., README, inline comments, API docs) if required.
5.  Ensuring the solution is robust, efficient, and adheres to existing project conventions and coding standards.
6.  Preparing a pull request that is ready for review by human developers.

[TASK DETAILS]
- **Backlog Task Description**: {{task_description}}
- **Repository**: {{repo_name}}
- **GitHub Issue Number**: {{issue_number}}
- **Additional Context**: {{additional_context}}
- **Acceptance Criteria**: {{acceptance_criteria}}

[CONSTRAINTS/REQUIREMENTS]
Please ensure:
- All code changes strictly adhere to the existing coding style, formatting, and conventions of the repository. Analyze surrounding code to match its style.
- Appropriate unit, integration, and/or end-to-end tests are added or updated to provide comprehensive coverage for the changes.
- The solution is thoroughly tested locally to prevent regressions and fully address the core problem described in the task.
- Any relevant documentation (e.g., README, inline comments, design docs) is updated to reflect the changes.
- The task is considered complete only when a pull request addressing the issue is created, passes all CI checks, and is ready for human review.
- Communicate progress, any significant decisions made, and any blockers encountered during the task execution.
- If the task involves a new feature, consider its impact on existing architecture and propose minimal, idiomatic changes.
- If the task is a bug fix, ensure the root cause is identified and addressed, not just the symptoms.

[OUTPUT FORMAT]
Provide your response in the following structured format:

## Task Summary:
[A brief, concise summary of the backlog task as you understand it, and your initial planned high-level approach to address it.]

## Action Plan:
[A detailed, step-by-step plan outlining how you intend to implement the task. This should cover:
1.  **Investigation/Understanding**: How you will gather more context (e.g., reading specific files, searching codebase).
2.  **Implementation Steps**: Specific code changes, new file creations, or refactorings.
3.  **Testing Strategy**: How you will verify the changes, including new tests and existing test runs.
4.  **Documentation Updates**: What documentation will be updated and why.
5.  **Verification**: How you will ensure the solution meets acceptance criteria.
6.  **PR Creation**: Steps for creating the pull request.]

## Progress Updates:
[This section will be updated iteratively. Provide regular updates on the status of each step in your action plan, including:
- What has been completed.
- What is currently being worked on.
- Any challenges faced and how they were resolved.
- Any deviations from the original plan and the rationale.
- Output from shell commands or tool calls that demonstrate progress.]

## Final Deliverable:
[Upon completion of the task, this section will contain:
- A confirmation that the task is complete.
- A link to the created pull request on GitHub.
- A summary of the key changes implemented.
- Instructions for human reviewers or for further verification.]

[ADDITIONAL GUIDELINES]
- Prioritize understanding the existing codebase and project architecture before making any significant changes.
- Use the available tools (file system, shell, GitHub API) efficiently to gather information, implement the solution, and manage the development workflow.
- If clarification is needed regarding the task, acceptance criteria, or any technical detail, ask specific and concise questions.
- Focus on delivering a high-quality, maintainable, and well-tested solution that integrates seamlessly with the existing project.
```

## Examples

### Example 1: Bug Fix
Input:
```
task_description: "Fix: User login fails when username contains special characters (e.g., 'user@name')."
repo_name: "myorg/myrepo"
issue_number: "123"
additional_context: "The issue seems to stem from improper sanitization or encoding in the authentication service. Focus on `src/auth_service.py` and `client/src/components/Login.js`."
acceptance_criteria: "Users with usernames containing special characters (e.g., '@', '#', '!') can successfully log in. Existing login tests must continue to pass. New tests should cover these special character scenarios."
```

Output:
```
## Task Summary:
The task is to fix a bug (Issue #123 in myorg/myrepo) where user login fails when usernames contain special characters. I will investigate `src/auth_service.py` and `client/src/components/Login.js` to identify and correct the input sanitization or validation logic, ensuring proper handling of special characters.

## Action Plan:
1.  **Investigation/Understanding**:
    *   Read `src/auth_service.py` to understand the backend authentication logic, focusing on username processing.
    *   Read `client/src/components/Login.js` to understand how the frontend handles username input.
    *   Search the codebase for existing validation/sanitization functions related to usernames.
2.  **Implementation Steps**:
    *   Identify the exact point of failure (e.g., regex mismatch, improper encoding/decoding).
    *   Implement necessary code changes in `src/auth_service.py` to correctly handle and validate usernames with special characters.
    *   Ensure `client/src/components/Login.js` correctly sends the username without unintended modifications.
3.  **Testing Strategy**:
    *   Locate existing unit/integration tests for user login.
    *   Add new unit tests in `src/tests/test_auth_service.py` (or similar) specifically for usernames with various special characters.
    *   Run all existing and newly added tests to ensure the fix works and no regressions are introduced.
4.  **Documentation Updates**:
    *   Add inline comments to the modified code explaining the special character handling.
    *   If a design document exists for authentication, update it to reflect the change.
5.  **Verification**:
    *   Manually test the login flow with usernames containing special characters.
    *   Confirm all acceptance criteria are met.
6.  **PR Creation**:
    *   Create a new branch for the fix.
    *   Commit all changes (code, tests, docs).
    *   Create a pull request targeting the main branch, linking to Issue #123.

## Progress Updates:
(Updates will be provided as the task progresses, detailing steps completed, findings, and any issues encountered.)

## Final Deliverable:
(Details of the completed work and PR link will be provided upon completion)
```

## Notes
- This template is designed to be used with the `/jules` command.
- Jules will use the provided variables and the template structure to formulate its internal plan and report progress.
- The `Progress Updates` and `Final Deliverable` sections will be populated by Jules as it executes the task.

### 14. Prompt Template Library Organization

This template would ideally be stored in a structured library, for example:
```
templates/
+-- project-management/
|   +-- jules-backlog-task-completion.md
+-- technical/
|   +-- code-review.md
|   +-- debugging.md
```

### 15. Quality Checklist for Templates

**Structure:**
- [X] Clear role/context
- [X] Explicit objective
- [X] Well-defined variables
- [X] Structured output format
- [X] Examples provided

**Content:**
- [X] Comprehensive requirements
- [X] Appropriate constraints
- [X] Quality guidelines
- [X] Edge cases covered (implicitly through testing and robustness requirements)

**Usability:**
- [X] Easy to understand
- [X] Easy to customize
- [X] Clear instructions
- [X] Good documentation

**Effectiveness:**
- [ ] Produces consistent results (requires actual testing with Jules)
- [X] Works across use cases (designed for various backlog tasks)
- [X] Handles variations well (through optional variables and implicit adaptation)
- [ ] Tested and validated (conceptual testing done, real-world testing with Jules needed)

---

