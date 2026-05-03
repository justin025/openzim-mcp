"""Search tools for OpenZIM MCP server."""

import logging
from typing import TYPE_CHECKING, Optional

from ..constants import INPUT_LIMIT_FILE_PATH, INPUT_LIMIT_QUERY
from ..security import sanitize_input

if TYPE_CHECKING:
    from ..server import OpenZimMcpServer

logger = logging.getLogger(__name__)


def register_search_tools(server: "OpenZimMcpServer") -> None:
    """
    Register search-related tools.

    Args:
        server: The OpenZimMcpServer instance to register tools on
    """

    @server.mcp.tool()
    async def search_zim_file(
        zim_file_path: str,
        query: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> str:
        """Search within a specific ZIM file's content.

        **PREFERRED: Use this AFTER `search_zim_files`** to find a specific archive.
        First call `search_zim_files` with the project name to get the file path,
        then call this tool with that path for targeted, low-token results.

        Args:
            zim_file_path: Path to the ZIM file (get from search_zim_files first)
            query: Search query term
            limit: Maximum number of results to return (default from config)
            offset: Result starting offset (for pagination)

        Returns:
            Search result text
        """
        try:
            # Sanitize inputs
            zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)
            query = sanitize_input(query, INPUT_LIMIT_QUERY)

            # Validate parameters
            if limit is not None and (limit < 1 or limit > 100):
                return (
                    "**Parameter Validation Error**\n\n"
                    f"**Issue**: Search limit must be between 1 and 100 "
                    f"(provided: {limit})\n\n"
                    "**Troubleshooting**: Adjust the limit parameter to be "
                    "within the valid range.\n"
                    "**Example**: Use `limit=10` for 10 results."
                )

            if offset < 0:
                return (
                    "**Parameter Validation Error**\n\n"
                    f"**Issue**: Offset must be non-negative (provided: {offset})\n\n"
                    "**Troubleshooting**: Use `offset=0` for first page."
                )

            # Perform the search using async operations
            search_result = await server.async_zim_operations.search_zim_file(
                zim_file_path, query, limit, offset
            )

            return search_result

        except Exception as e:
            logger.error(f"Error searching ZIM file: {e}")
            return f"Error searching ZIM file: {e}"

    @server.mcp.tool()
    async def search_all(
        query: str,
        limit_per_file: int = 5,
    ) -> str:
        """Run an exact-string search across EVERY ZIM file in the allowed directories.

        **EXPENSIVE: Returns hundreds of hits when you only need a specific file.**
        Only use this when you do NOT know the project name. Preferred flow:
        1) Call `search_zim_files` with the project name (e.g., "Pandas")
        2) Call `search_zim_file` with the specific file path from step 1

        Only use `search_all` as a fallback when the project name is unknown.


        Args:
            query: Search query term (required)
            limit_per_file: Max hits per ZIM file (1-50, default: 5)

        Returns:
            JSON containing per-file result groups and counts
        """
        try:
            query = sanitize_input(query, INPUT_LIMIT_QUERY)
            return await server.async_zim_operations.search_all(query, limit_per_file)

        except Exception as e:
            logger.error(f"Error in search_all: {e}")
            return f"Error searching across ZIM files: {e}"

    @server.mcp.tool()
    async def find_entry_by_title(
        zim_file_path: str,
        title: str,
        cross_file: bool = False,
        limit: int = 10,
    ) -> str:
        """Resolve a title to one or more entry paths.

        Cheaper than full-text search when the caller knows the article title.

        Args:
            zim_file_path: Path to the ZIM file (used unless cross_file=True)
            title: Title or partial title to resolve (case-insensitive)
            cross_file: If True, search across all allowed ZIM files
            limit: Max results to return (1-50, default: 10)

        Returns:
            JSON with query, ranked results, fast_path_hit flag, files_searched
        """
        try:
            title = sanitize_input(title, INPUT_LIMIT_QUERY)
            if not cross_file:
                zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)

            return await server.async_zim_operations.find_entry_by_title(
                zim_file_path, title, cross_file, limit
            )

        except Exception as e:
            logger.error(f"Error in find_entry_by_title: {e}")
            return f"Error finding entry by title: {e}"
