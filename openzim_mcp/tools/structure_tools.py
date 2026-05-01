"""Article structure and content analysis tools for OpenZIM MCP server."""

import logging
from typing import TYPE_CHECKING, Optional

from ..constants import INPUT_LIMIT_ENTRY_PATH, INPUT_LIMIT_FILE_PATH
from ..exceptions import OpenZimMcpRateLimitError
from ..security import sanitize_input

if TYPE_CHECKING:
    from ..server import OpenZimMcpServer

logger = logging.getLogger(__name__)


def register_structure_tools(server: "OpenZimMcpServer") -> None:
    """Register article structure and content analysis tools.

    Args:
        server: The OpenZimMcpServer instance to register tools on
    """

    @server.mcp.tool()
    async def extract_article_links(zim_file_path: str, entry_path: str) -> str:
        """Extract internal and external links from an article.

        Args:
            zim_file_path: Path to the ZIM file
            entry_path: Entry path, e.g., 'C/Some_Article'

        Returns:
            JSON string containing extracted links
        """
        try:
            # Check rate limit
            try:
                server.rate_limiter.check_rate_limit("get_structure")
            except OpenZimMcpRateLimitError as e:
                return server._create_enhanced_error_message(
                    operation="extract article links",
                    error=e,
                    context=f"Entry: {entry_path}",
                )

            # Sanitize inputs
            zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)
            entry_path = sanitize_input(entry_path, INPUT_LIMIT_ENTRY_PATH)

            # Use async operations
            return await server.async_zim_operations.extract_article_links(
                zim_file_path, entry_path
            )

        except Exception as e:
            logger.error(f"Error extracting article links: {e}")
            return server._create_enhanced_error_message(
                operation="extract article links",
                error=e,
                context=f"File: {zim_file_path}, Entry: {entry_path}",
            )

    @server.mcp.tool()
    async def get_entry_summary(
        zim_file_path: str,
        entry_path: str,
        max_words: int = 200,
    ) -> str:
        """Get a concise summary of an article without returning the full content.

        This tool extracts the opening paragraph(s) or introduction section,
        providing a quick overview of the article content. Useful for getting
        context without loading full articles.

        Args:
            zim_file_path: Path to the ZIM file
            entry_path: Entry path, e.g., 'C/Some_Article'
            max_words: Maximum number of words in the summary (default: 200, max: 1000)

        Returns:
            JSON string containing summary, title, word count, and truncation status.
        """
        try:
            # Check rate limit
            try:
                server.rate_limiter.check_rate_limit("get_entry")
            except OpenZimMcpRateLimitError as e:
                return server._create_enhanced_error_message(
                    operation="get entry summary",
                    error=e,
                    context=f"Entry: {entry_path}",
                )

            # Sanitize inputs
            zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)
            entry_path = sanitize_input(entry_path, INPUT_LIMIT_ENTRY_PATH)

            # Validate parameters
            if max_words < 1 or max_words > 1000:
                return (
                    "**Parameter Validation Error**\n\n"
                    f"**Issue**: max_words must be between 1 and 1000 "
                    f"(provided: {max_words})\n\n"
                    "**Troubleshooting**: Adjust max_words to a value within the "
                    "valid range.\n"
                    "**Example**: Use `max_words=200` for a typical summary."
                )

            # Use async operations
            return await server.async_zim_operations.get_entry_summary(
                zim_file_path, entry_path, max_words
            )

        except Exception as e:
            logger.error(f"Error getting entry summary: {e}")
            return server._create_enhanced_error_message(
                operation="get entry summary",
                error=e,
                context=f"File: {zim_file_path}, Entry: {entry_path}",
            )

    @server.mcp.tool()
    async def get_table_of_contents(
        zim_file_path: str,
        entry_path: str,
    ) -> str:
        """Extract a hierarchical table of contents from an article.

        Returns a structured TOC tree based on heading levels (h1-h6),
        suitable for navigation and content overview.

        Args:
            zim_file_path: Path to the ZIM file
            entry_path: Entry path, e.g., 'C/Some_Article'

        Returns:
            JSON string containing hierarchical TOC, heading count, and max depth.
        """
        try:
            # Check rate limit
            try:
                server.rate_limiter.check_rate_limit("get_structure")
            except OpenZimMcpRateLimitError as e:
                return server._create_enhanced_error_message(
                    operation="get table of contents",
                    error=e,
                    context=f"Entry: {entry_path}",
                )

            # Sanitize inputs
            zim_file_path = sanitize_input(zim_file_path, INPUT_LIMIT_FILE_PATH)
            entry_path = sanitize_input(entry_path, INPUT_LIMIT_ENTRY_PATH)

            # Use async operations
            return await server.async_zim_operations.get_table_of_contents(
                zim_file_path, entry_path
            )

        except Exception as e:
            logger.error(f"Error getting table of contents: {e}")
            return server._create_enhanced_error_message(
                operation="get table of contents",
                error=e,
                context=f"File: {zim_file_path}, Entry: {entry_path}",
            )