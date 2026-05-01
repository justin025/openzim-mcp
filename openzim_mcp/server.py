"""Main OpenZIM MCP server implementation."""

import logging
from typing import Literal

from mcp.server.fastmcp import FastMCP

from .async_operations import AsyncZimOperations
from .cache import OpenZimMcpCache
from .config import OpenZimMcpConfig
from .constants import VALID_TRANSPORT_TYPES
from .content_processor import ContentProcessor
from .security import PathValidator
from .tools import register_all_tools
from .zim_operations import ZimOperations

logger = logging.getLogger(__name__)


class OpenZimMcpServer:
    """Main OpenZIM MCP server class with dependency injection."""

    def __init__(
        self,
        config: OpenZimMcpConfig,
        host: str = "127.0.0.1",
        port: int = 8000,
    ):
        """Initialize OpenZIM MCP server.

        Args:
            config: Server configuration
            host: Host to bind to for HTTP transports (sse, streamable-http)
            port: Port to bind to for HTTP transports (sse, streamable-http)
        """
        self.config = config
        self._host = host
        self._port = port

        # Setup logging
        config.setup_logging()
        logger.info(f"Initializing OpenZIM MCP server v{config.server_name}")

        # Initialize components
        self.path_validator = PathValidator(config.allowed_directories)
        self.cache = OpenZimMcpCache(config.cache)
        self.content_processor = ContentProcessor(config.content.snippet_length)
        self.zim_operations = ZimOperations(
            config, self.path_validator, self.cache, self.content_processor
        )
        self.async_zim_operations = AsyncZimOperations(self.zim_operations)

        # Initialize MCP server and register tools
        self.mcp = FastMCP(config.server_name, host=host, port=port)
        register_all_tools(self)
        logger.info("MCP tools registered successfully")

        # Minimal server startup logging
        logger.info(
            f"Server: {self.config.server_name}, "
            f"Directories: {len(self.config.allowed_directories)}, "
            f"Cache: {self.config.cache.enabled}"
        )

    def run(
        self, transport: Literal["stdio", "sse", "streamable-http"] = "stdio"
    ) -> None:
        """
        Run the OpenZIM MCP server.

        Args:
            transport: Transport protocol to use ("stdio", "sse", or "streamable-http")

        Raises:
            ValueError: If transport type is invalid
        """
        if transport not in VALID_TRANSPORT_TYPES:
            raise ValueError(
                f"Invalid transport type: '{transport}'. "
                f"Must be one of: {', '.join(sorted(VALID_TRANSPORT_TYPES))}"
            )

        # For stdio transport, host/port are ignored by MCP; for HTTP transports
        # the host/port were already passed to FastMCP above.
        logger.info(
            f"Starting OpenZIM MCP server with transport: {transport}"
            f" ({self._host}:{self._port})"
        )
        try:
            self.mcp.run(transport=transport)
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            logger.info("OpenZIM MCP server stopped")
