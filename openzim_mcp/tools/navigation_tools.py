"""Navigation tools for OpenZIM MCP server."""

import logging
from typing import TYPE_CHECKING, Optional

from ..constants import INPUT_LIMIT_FILE_PATH, INPUT_LIMIT_QUERY
from ..security import sanitize_input

if TYPE_CHECKING:
    from ..server import OpenZimMcpServer

logger = logging.getLogger(__name__)


def register_navigation_tools(server: "OpenZimMcpServer") -> None:
    """Register navigation tools.

    Args:
        server: The OpenZimMcpServer instance to register tools on
    """

    @server.mcp.tool()
    async def search_with_filters(
        zim_file_path: str,
        query: str,
        namespace: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> str:
        """Search within ZIM file content with optional namespace and content type filters.

        Args:
            zim_file_path: Path to the ZIM file
            query: Search query term
            namespace: Optional namespace filter (C, M, W, X, etc.)
            content_type: Optional content type filter (text/html, text/plain, etc.)
            limit: Maximum number of results to return (default from config)
            offset: Result starting offset (for pagination)

        Returns:
            Search result text
        """
        try:
            # Sanitize inputs
            zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)
            query = sanitize_input(query, INPUT_LIMIT_QUERY)
            if namespace:
                namespace = sanitize_input(namespace, INPUT_LIMIT_QUERY)
            if content_type:
                content_type = sanitize_input(content_type, INPUT_LIMIT_QUERY)

            # Validate parameters
            if limit is not None and (limit < 1 or limit > 100):
                return (
                    "**Parameter Validation Error**\n\n"
                    f"**Issue**: limit must be between 1 and 100 "
                    f"(provided: {limit})\n\n"
                    "**Troubleshooting**: Adjust the limit or omit for default."
                )
            if offset < 0:
                return (
                    "**Parameter Validation Error**\n\n"
                    f"**Issue**: offset must be non-negative (provided: {offset})\n\n"
                    "**Troubleshooting**: Use offset=0 for first page."
                )

            # Perform the filtered search using async operations
            search_result = await server.async_zim_operations.search_with_filters(
                zim_file_path, query, namespace, content_type, limit, offset
            )

            return search_result

        except Exception as e:
            logger.error(f"Error in filtered search: {e}")
            return f"Error searching with filters: {e}"
