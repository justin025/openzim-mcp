"""Main OpenZIM MCP server implementation."""

import logging
from typing import Dict, List, Literal

from mcp.server.fastmcp import FastMCP

from .async_operations import AsyncZimOperations
from .cache import OpenZimMcpCache
from .config import OpenZimMcpConfig
from .constants import VALID_TRANSPORT_TYPES
from .content_processor import ContentProcessor
from .error_messages import (
    format_error_message,
    format_generic_error,
    get_error_config,
)
from .exceptions import OpenZimMcpConfigurationError
from .instance_tracker import InstanceTracker
from .rate_limiter import RateLimitConfig, RateLimiter
from .security import PathValidator, sanitize_context_for_error
from .tools import register_all_tools
from .zim_operations import ZimOperations

logger = logging.getLogger(__name__)


class OpenZimMcpServer:
    """Main OpenZIM MCP server class with dependency injection."""

    def __init__(
        self,
        config: OpenZimMcpConfig,
        instance_tracker: InstanceTracker = None,
    ):
        """Initialize OpenZIM MCP server.

        Args:
            config: Server configuration
            instance_tracker: Optional instance tracker for multi-server management
        """
        self.config = config
        self.instance_tracker = instance_tracker

        # Setup logging
        config.setup_logging()
        logger.info(f"Initializing OpenZIM MCP server v{config.server_name}")

        # Initialize components
        self.path_validator = PathValidator(config.allowed_directories)
        self.cache = OpenZimMcpCache(config.cache)
        self.content_processor = ContentProcessor(config.content.snippet_length)
        self.rate_limiter = RateLimiter(
            RateLimitConfig(
                enabled=config.rate_limit.enabled,
                requests_per_second=config.rate_limit.requests_per_second,
                burst_size=config.rate_limit.burst_size,
            )
        )
        self.zim_operations = ZimOperations(
            config, self.path_validator, self.cache, self.content_processor
        )
        self.async_zim_operations = AsyncZimOperations(self.zim_operations)

        # Initialize MCP server and register tools
        self.mcp = FastMCP(config.server_name)
        register_all_tools(self)
        logger.info("MCP tools registered successfully")

        # Minimal server startup logging
        logger.info(
            f"Server: {self.config.server_name}, "
            f"Directories: {len(self.config.allowed_directories)}, "
            f"Cache: {self.config.cache.enabled}"
        )

    def _create_enhanced_error_message(
        self, operation: str, error: Exception, context: str = ""
    ) -> str:
        """Create educational, actionable error messages for LLM users.

        Uses externalized error message templates from error_messages module.

        Args:
            operation: The operation that failed
            error: The exception that occurred
            context: Additional context (e.g., file path, query)

        Returns:
            Enhanced error message with troubleshooting guidance
        """
        error_type = type(error).__name__
        base_message = str(error)
        sanitized_context = sanitize_context_for_error(context)

        # Check for known error types using externalized config
        config = get_error_config(error)
        if config:
            return format_error_message(
                config, operation, sanitized_context, base_message
            )

        # Generic error using externalized template
        return format_generic_error(
            operation=operation,
            error_type=error_type,
            context=sanitized_context,
            details=base_message,
        )

    def _format_conflict_warnings(self, conflicts: List[Dict]) -> str:
        """Format conflict detection warnings for appending to results."""
        if not conflicts:
            return ""

        warning = "\n\n**Server Conflict Detected**\n"
        for conflict in conflicts:
            if conflict["type"] == "configuration_mismatch":
                warning += (
                    f"WARNING: Configuration mismatch with server "
                    f"PID {conflict['instance']['pid']}. "
                    f"Results may be inconsistent.\n"
                )
            elif conflict["type"] == "multiple_instances":
                warning += (
                    f"WARNING: Multiple servers detected "
                    f"(PID {conflict['instance']['pid']}). "
                    f"Results may come from different server instances.\n"
                )
        warning += "\nTIP: Use 'resolve_server_conflicts()' to fix these issues.\n"
        return warning

    def _check_and_append_conflict_warnings(self, result: str) -> str:
        """Check for conflicts and append warnings to result if found."""
        if not self.instance_tracker:
            return result
        try:
            conflicts = self.instance_tracker.detect_conflicts(
                self.config.get_config_hash()
            )
            conflict_warning = self._format_conflict_warnings(conflicts)
            if conflict_warning:
                return result + conflict_warning
        except Exception as e:
            logger.debug(f"Failed to check for conflicts: {e}")
        return result

    def run(
        self, transport: Literal["stdio", "sse", "streamable-http"] = "stdio"
    ) -> None:
        """
        Run the OpenZIM MCP server.

        Args:
            transport: Transport protocol to use ("stdio", "sse", or "streamable-http")

        Raises:
            OpenZimMcpConfigurationError: If transport type is invalid
        """
        if transport not in VALID_TRANSPORT_TYPES:
            raise OpenZimMcpConfigurationError(
                f"Invalid transport type: '{transport}'. "
                f"Must be one of: {', '.join(sorted(VALID_TRANSPORT_TYPES))}"
            )

        logger.info(f"Starting OpenZIM MCP server with transport: {transport}")
        try:
            self.mcp.run(transport=transport)
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            logger.info("OpenZIM MCP server stopped")