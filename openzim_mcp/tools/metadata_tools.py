"""Namespace listing tool for OpenZIM MCP server."""

import logging
from typing import TYPE_CHECKING

from ..constants import INPUT_LIMIT_FILE_PATH
from ..security import sanitize_input

if TYPE_CHECKING:
    from ..server import OpenZimMcpServer

logger = logging.getLogger(__name__)


def register_metadata_tools(server: "OpenZimMcpServer") -> None:
    """Register namespace listing tools.

    Args:
        server: The OpenZimMcpServer instance to register tools on
    """

    @server.mcp.tool()
    async def list_namespaces(zim_file_path: str) -> str:
        """List available namespaces and their entry counts.

        Args:
            zim_file_path: Path to the ZIM file

        Returns:
            JSON string containing namespace information
        """
        try:
            # Sanitize inputs
            zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)

            # Use async operations
            return await server.async_zim_operations.list_namespaces(zim_file_path)

        except Exception as e:
            logger.error(f"Error listing namespaces: {e}")
            return f"Error listing namespaces: {e}"
