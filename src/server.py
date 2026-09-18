from mcp.server import MCPServer

from prompts import register_prompts
from servers import register_all_tools
from shared.instructions import SERVER_INSTRUCTIONS


mcp = MCPServer("Bio-Bridge", instructions=SERVER_INSTRUCTIONS)
register_all_tools(mcp)
register_prompts(mcp)


def main() -> None:
    """Run Bio-Bridge over the default stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
