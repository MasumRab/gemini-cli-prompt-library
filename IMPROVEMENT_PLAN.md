
# Gemini CLI - `prompt improve` Enhancement Plan

## 1. Executive Summary

This document outlines a phased plan to transform the `/prompts:improve` command from a simple text-enhancer into an intelligent, user-centric workflow assistant for the Gemini CLI. The core objective is to reduce user friction by translating vague, conversational requests into precise, executable commands and workflows, guided by a transparent and interactive UI.

This plan is the result of a detailed analysis of the existing project structure, user interaction patterns discovered via the `cass` tool, and established SOTA principles for CLI design.

## 2. Core Problem: The Conversational Gap

Our investigation revealed two primary modes of interaction with the CLI:

1.  **Conversational Mode:** Most users begin with a vague, natural-language goal (e.g., "my test is broken"). This is the most common entry point.
2.  **Agentic Mode:** The system executes precise, structured commands (e.g., `/workflows:debug-and-fix`) as part of a larger, automated plan.

The core problem is the **gap between these two modes.** The user is currently forced to manually translate their conversational goal into a specific command, which requires them to know the entire command library.

## 3. The Solution: A Phased Enhancement

We will evolve `/prompts:improve` in three distinct phases:

*   **Phase 1: Foundational Technical Spike & Dispatcher**
*   **Phase 2: Unified & Transparent UI**
*   **Phase 3: Full Agentic Integration**

---

## 4. Phase 1: Foundational Technical Spike & Dispatcher

**Goal:** Enable the core user-to-command workflow by translating natural language into precise, executable commands.

### 4.1. (CRITICAL) Technical Spike: TUI Capabilities

*   **Action:** A blocking investigation to determine if the TUI framework allows programmatic control over the user's input buffer.
*   **Rationale:** This single question dictates the entire UI/UX path forward.

### 4.2. "Intelligent Dispatcher" Meta-Prompt

*   **Action:** Engineer a new "meta-prompt" to power `/prompts:improve`.
*   **Function:** This prompt will act as a "router." It will:
    1.  Analyze the user's natural language request.
    2.  Select the single most appropriate command (e.g., `/code-review:security`) from an internal manifest of all available commands.
    3.  Generate a high-quality, refined prompt specifically for the selected command.
    4.  Construct the final, complete, ready-to-run command string.

### 4.3. Core User Workflow

*   **Path A (Preferred - If Spike Succeeds):** The "Direct Edit" Workflow. The user's input buffer will be automatically populated with the fully constructed command from the dispatcher, ready for them to edit or execute immediately.
*   **Path B (Fallback - If Spike Fails):** The "Reference-Based" Workflow. The system will output the command and assign it a reference number (e.g., `[1]`), which the user can then execute via a follow-up command (e.g., `run 1`).

---

## 5. Phase 2: Unified & Transparent UI

**Goal:** Build a complimentary UI for both immediate action-feedback and long-running workflow-progression.

### 5.1. The "Command Recommendation" Menu

*   **Action:** When `/prompts:improve` runs, instead of just populating the input buffer, it will display a rich, interactive menu.
*   **Design:**

    ```
    --- Command Recommendation ---

    ✅ Based on your request, I recommend executing the following **Workflow**:

       /workflows:debug-and-fix --error "login test is failing..."

    **Why this choice?**
    Your request indicates a bug that needs a solution. This is a multi-step **Workflow** designed to execute a full plan...

    **What would you like to do next?**
    1. ▶️ **Run Workflow** (Initiate the agentic process)
    2. ✍️ **Edit Command** (Load into your input buffer)
    3. 💡 **View Alternatives (preparing...)**
    4. ❌ **Cancel**
    ---
    This command was inferred from the `debug-and-fix.toml` definition.
    ```

*   **Adherence to SOTA Principles:** This design provides **Discoverability** ("Why?"), **User Control** ("Edit"), **Safety** ("Run"), and **Guidance** ("Alternatives").

### 5.2. Asynchronous, `cass`-Augmented Suggestions

*   **Action:** Implement a background process to pre-calculate the content for the "View Alternatives" menu.
*   **Workflow:**
    1.  The primary menu is shown instantly.
    2.  In the background, the system runs `cass search` for each alternative command, looking for historical examples of its usage.
    3.  When the user selects "View Alternatives," a pre-rendered menu appears instantly, showing not just other commands, but real-world examples of how they were used successfully in the past.

#### Smart Search Strategy
To ensure this feature is fast and effective, a "Smart Search" layer will be implemented to prevent naive or inaccurate searches.

1.  **Pre-computation of Search Terms:** Before searching, the user's raw input will be processed to extract structured search entities:
    *   **Keywords:** Core nouns and verbs (e.g., `login`, `failing`, `pointer`).
    *   **Regex Patterns:** Patterns for relevant entities like file paths (e.g., `test_.*login.*\.py`).
    *   **Negative Keywords:** Terms to exclude to reduce noise (e.g., `javascript` if the context is Python).

2.  **Layered Search Execution:** The system will execute a sequence of pre-defined query patterns, falling back to broader searches only if a more specific one fails. This maximizes relevance while ensuring a result is always found quickly.
    *   **Pattern 1: Exact Match:** Search for the alternative command plus the user's core keywords.
        `cass search '"/debugging:trace-issue" AND "login" AND "failing"'`
    *   **Pattern 2: Concept Match:** If no results, broaden the search with synonyms and related concepts.
        `cass search '"/debugging:trace-issue" AND ("login" OR "auth") AND ("fail" OR "error")'`
    *   **Pattern 3: "Command Only" Fallback:** As a final option, find the best generic example of the command being used successfully.
        `cass search '"/debugging:trace-issue" AND (passed OR fixed OR resolved)'`

This strategy ensures that the `cass`-augmented suggestions are retrieved with minimal delay and maximum relevance, directly addressing the need to pre-compute content efficiently.

### 5.3. The "Progression Checklist"

*   **Action:** When a workflow is executed, the menu transitions into a real-time checklist.
*   **Design:**

    ```
    Workflow: /workflows:debug-and-fix
    Status: In Progress...

    1. [✓] Confirmed failure by running the test.
    2. [in_progress] Analyzing user_service.py...
    3. [ ] Proposing a code fix.
    ...
    ```

*   **Rationale:** This provides critical transparency for long-running agentic tasks, a direct need identified from the `cass` analysis of existing workflows.

---

## 6. Phase 3: Full Agentic Integration

**Goal:** Evolve the system so that "improving prompts" is no longer a command the user runs, but a native skill the agent uses autonomously.

### 6.1. Proactive Workflow Suggestions

*   **Action:** The agent will be programmed to recognize when a user's request for a simple command could be better served by a more powerful workflow.
*   **Example:** User runs `/code-review:refactor`. The agent replies, *"I can do that, but I can also use the `smart-refactor` workflow to automatically verify my changes with tests. Would you like to proceed with the workflow?"*

### 6.2. Self-Correction via Internal Skill

*   **Action:** The "Intelligent Dispatcher" logic from Phase 1 will be refactored into an internal agent skill.
*   **Function:** When a step in a workflow fails (e.g., a tool returns an error), the agent can call this internal skill to analyze the error, re-read the context, and rewrite its own prompt to try a different approach, making it more resilient and autonomous.
