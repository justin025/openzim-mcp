"""Main entry point for OpenZIM MCP server."""

import argparse
import os
import sys

from .config import OpenZimMcpConfig
from .server import OpenZimMcpServer


def main() -> None:
    """Run the OpenZIM MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="OpenZIM MCP Server - Access ZIM files through MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m openzim_mcp /path/to/zim/files
  openzim-mcp /path/to/zim/files

  # HTTP transport (SSE or streamable-http)
  openzim-mcp --transport streamable-http --host 0.0.0.0 --port 8000 /path/to/zim/files
  openzim-mcp --transport sse --host 0.0.0.0 --port 8000 /path/to/zim/files

Environment Variables:
  OPENZIM_MCP_CACHE__ENABLED - Enable/disable caching (true/false)
  OPENZIM_MCP_CACHE__MAX_SIZE - Maximum cache entries
  OPENZIM_MCP_LOGGING__LEVEL - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  OPENZIM_MCP_TRANSPORT - Transport type (stdio, sse, streamable-http)
  OPENZIM_MCP_HOST - Host to bind for HTTP transports (default: 127.0.0.1)
  OPENZIM_MCP_PORT - Port to bind for HTTP transports (default: 8000)
        """,
    )
    parser.add_argument(
        "directories",
        nargs="+",
        help="One or more directories containing ZIM files",
    )
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio", "streamable-http"],
        default=os.environ.get("OPENZIM_MCP_TRANSPORT", "stdio"),
        help=(
            "Transport type: stdio, sse, or streamable-http "
            "(default: stdio, or from OPENZIM_MCP_TRANSPORT env var)"
        ),
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("OPENZIM_MCP_HOST", "127.0.0.1"),
        help="Host to bind for HTTP transports (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("OPENZIM_MCP_PORT", "8000")),
        help="Port to bind for HTTP transports (default: 8000)",
    )

    # Handle case where no arguments provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    try:
        # Create configuration
        config = OpenZimMcpConfig(allowed_directories=args.directories)

        # Create and run server
        server = OpenZimMcpServer(
            config,
            host=args.host,
            port=args.port,
        )

        print(
            "OpenZIM MCP server started",
            file=sys.stderr,
        )
        print(
            f"Allowed directories: {', '.join(args.directories)}",
            file=sys.stderr,
        )
        print(
            f"Transport: {args.transport} ({args.host}:{args.port})",
            file=sys.stderr,
        )

        server.run(transport=args.transport)

    except Exception as e:
        print(f"Server startup error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()