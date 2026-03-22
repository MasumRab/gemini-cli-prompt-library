# Ecosystem Integration

This library can be integrated into other developer ecosystems like **Goose** and **Claude**.

## Goose (Block/Square)

The Goose developer agent allows customization via an `AGENTS.md` file in your project root. To use these prompts with Goose:

1.  **Create or Edit `AGENTS.md`**:
    In the root of your project, create an `AGENTS.md` file (or `.goosehints`).

2.  **Import Prompts**:
    Since Goose does not yet support dynamic extension loading from Git for prompts, you can manually add the specific instructions you need.

    *Example: Adding the Code Review Security Workflow*

    Copy the content of the relevant `.toml` prompt (excluding the metadata) into your `AGENTS.md`:

    ```markdown
    # Security Review Instructions
    When I ask for a security review, please follow these guidelines:

    [Paste content from commands/code-review/security.toml here]
    ```

3.  **Usage**:
    Simply ask Goose: "Perform a security review of this file following the guidelines in AGENTS.md".

## Claude (Model Context Protocol)

The **Model Context Protocol (MCP)** allows Claude to connect to external data and tools.

### Option 1: Using `gemini-cli` as an MCP Server
If your version of `gemini-cli` supports acting as an MCP server, you can configure Claude Desktop to connect to it. Refer to the `gemini-cli` documentation for `mcp` commands.

### Option 2: Manual "Project" Integration
For Claude Projects (available in Claude Pro/Team):
1.  Download this repository.
2.  In your Claude Project, go to "Project Knowledge".
3.  Upload the specific `.toml` or `GEMINI.md` files you want Claude to have access to.
4.  Claude will now be able to reference these prompts when you mention them (e.g., "Use the security review prompt from the knowledge base").

### Option 3: Future MCP Server
There are community tools (like `claude-prompts-mcp`) that can serve a directory of prompts to Claude. You can configure such a server to point to the `commands/` directory of this repository to expose these prompts dynamically to Claude Desktop.
