# Mock 2: MCP Server (Goose / Claude Desktop) Architecture
# Location: dspy_integration/framework/plugins/mcp_server.py

from mcp.server.fastmcp import FastMCP
from dspy_integration.framework.registry import get_command

mcp = FastMCP("DSPy Prompt Library")

@mcp.tool()
def design_architecture(system_description: str) -> str:
    """
    [COMPLEX PIPELINE] Designs a REST API architecture based on a system description.
    """
    # This is a complex pipeline because it may require recursive subtasking (opencode-subtask)
    # The MCP tool abstracts the DSPy optimization loop away from Goose.
    command = get_command("design-api")
    return execute_dspy_pipeline(command.prompt, system_description)

if __name__ == "__main__":
    mcp.run()
