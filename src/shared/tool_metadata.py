"""Reusable MCP tool annotations.

Annotations are hints for MCP clients, not an authorization boundary.
"""

from mcp.types import ToolAnnotations


READ_ONLY_OPEN_WORLD = ToolAnnotations(
    read_only_hint=True,
    open_world_hint=True,
)
