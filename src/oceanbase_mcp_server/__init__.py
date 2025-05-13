from . import server, server_on_fastmcp
import asyncio
import argparse


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--legacy", type=bool, default=False, help="Whether to enable legacy mode."
    )
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        help="Specify the MCP server transport type as stdio or sse.",
    )
    args = parser.parse_args()
    if args.legacy:
        asyncio.run(server.main())
    else:
        if args.transport == "stdio":
            server_on_fastmcp.main()
        else:
            server_on_fastmcp.main(transport="sse")


# Expose important items at package level
__all__ = ["main", "server", "server_on_fastmcp"]
