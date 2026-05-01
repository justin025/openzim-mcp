"""Content retrieval tools for OpenZIM MCP server."""

import logging
from typing import TYPE_CHECKING, Optional

from ..constants import INPUT_LIMIT_ENTRY_PATH, INPUT_LIMIT_FILE_PATH
from ..security import sanitize_input

if TYPE_CHECKING:
    from ..server import OpenZimMcpServer

logger = logging.getLogger(__name__)


def register_content_tools(server: "OpenZimMcpServer") -> None:
    """Register content retrieval tools.

    Args:
        server: The OpenZimMcpServer instance to register tools on
    """

    @server.mcp.tool()
    async def get_zim_entry(
        zim_file_path: str,
        entry_path: str,
        max_content_length: Optional[int] = None,
        content_offset: int = 0,
    ) -> str:
        """Get detailed content of a specific entry in a ZIM file.

        Args:
            zim_file_path: Path to the ZIM file
            entry_path: Entry path, e.g., 'A/Some_Article'
            max_content_length: Maximum length of content to return
            content_offset: Character offset to start reading from (default 0).
                Combine with max_content_length to page through long articles
                without re-fetching the prefix each time.

        Returns:
            Entry content text
        """
        try:
            # Sanitize inputs
            zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)
            entry_path = sanitize_input(entry_path, INPUT_LIMIT_ENTRY_PATH)

            # Validate parameters
            if max_content_length is not None and max_content_length < 100:
                return (
                    "**Parameter Validation Error**\n\n"
                    f"**Issue**: max_content_length must be at least 100 characters "
                    f"(provided: {max_content_length})\n\n"
                    "**Troubleshooting**: Increase max_content_length or omit for default.\n"
                )

            if content_offset < 0:
                return (
                    "**Parameter Validation Error**\n\n"
                    f"**Issue**: content_offset must be non-negative "
                    f"(provided: {content_offset})\n\n"
                    "**Troubleshooting**: Use 0 to read from the start."
                )

            # Use async operations to avoid blocking
            return await server.async_zim_operations.get_zim_entry(
                zim_file_path, entry_path, max_content_length, content_offset
            )

        except Exception as e:
            logger.error(f"Error getting ZIM entry: {e}")
            return f"Error getting ZIM entry: {e}"
