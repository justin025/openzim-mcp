"""Main entry point for OpenZIM MCP server."""

import argparse
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

Environment Variables:
  OPENZIM_MCP_CACHE__ENABLED - Enable/disable caching (true/false)
  OPENZIM_MCP_CACHE__MAX_SIZE - Maximum cache entries
  OPENZIM_MCP_LOGGING__LEVEL - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """,
    )
    parser.add_argument(
        "directories",
        nargs="+",
        help="One or more directories containing ZIM files",
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
        server = OpenZimMcpServer(config)

        print(
            "OpenZIM MCP server started",
            file=sys.stderr,
        )
        print(
            f"Allowed directories: {', '.join(args.directories)}",
            file=sys.stderr,
        )

        server.run(transport="stdio")

    except Exception as e:
        print(f"Server startup error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()