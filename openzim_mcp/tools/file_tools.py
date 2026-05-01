"""File listing tools for OpenZIM MCP server."""

import json
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..server import OpenZimMcpServer

logger = logging.getLogger(__name__)


def register_file_tools(server: "OpenZimMcpServer") -> None:
    """
    Register file listing tools.

    Args:
        server: The OpenZimMcpServer instance to register tools on
    """

    @server.mcp.tool()
    async def search_zim_files(query: str, limit: int = 10) -> str:
        """Search ZIM file names by keyword.

        Searches only the ZIM file names (not paths or metadata) for files
        matching the query string. Case-insensitive partial match.

        Use this instead of list_zim_files when you know part of the file name.
        For example, searching "nginx" returns only nginx-related archives
        instead of listing all 200 ZIM files.

        Args:
            query: Search keyword to match against ZIM file names
            limit: Maximum number of results to return (default: 10)

        Returns:
            JSON string containing matching ZIM file names and paths
        """
        try:
            all_files = server.zim_operations.list_zim_files_data()
            query_lower = query.lower()

            matches = [
                {"name": f["name"], "path": f["path"]}
                for f in all_files
                if query_lower in f["name"].lower()
            ][:limit]

            if not matches:
                return f"No ZIM files found matching '{query}'."

            return json.dumps(matches, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error searching ZIM files: {e}")
            return f"Error searching ZIM files: {e}"

    @server.mcp.tool()
    async def list_zim_files(
        directory: Optional[str] = None,
        include_details: bool = False,
    ) -> str:
        """List all ZIM files in allowed directories.

        Use this tool as a last resort — prefer search_zim_files when you
        know part of the file name.

        Args:
            directory: Optional filter to list files from a specific directory
                path (e.g., "/home/user/zim"). If not provided, lists all
                directories.
            include_details: If true, includes size and modification date.
                Default false — only returns name and path to save tokens.

        Returns:
            JSON string containing ZIM file names (and optionally full metadata)
        """
        try:
            all_files = server.zim_operations.list_zim_files_data()

            if not all_files:
                return "No ZIM files found in allowed directories."

            # Filter by directory if provided
            if directory:
                all_files = [f for f in all_files if f["directory"] == directory]

            if not all_files:
                return f"No ZIM files found in directory: {directory}"

            if include_details:
                return json.dumps(all_files, indent=2, ensure_ascii=False)

            compact = [{"name": f["name"], "path": f["path"]} for f in all_files]
            return json.dumps(compact, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error listing ZIM files: {e}")
            return f"Error listing ZIM files: {e}"

