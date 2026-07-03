from mcp.server.fastmcp import FastMCP

from servers import register_all_tools
from shared.instructions import SERVER_INSTRUCTIONS


mcp = FastMCP("Bio-Bridge", instructions=SERVER_INSTRUCTIONS)
register_all_tools(mcp)


if __name__ == "__main__":
    mcp.run()
