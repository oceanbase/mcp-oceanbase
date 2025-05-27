from . import server_on_fastmcp
import argparse


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        help="Specify the MCP server transport type as stdio or sse.",
    )
    parser.add_argument("--port", type=int, default=8000, help="SSE Port to listen on")
    args = parser.parse_args()
    if args.transport == "stdio":
        server_on_fastmcp.main()
    else:
        server_on_fastmcp.main(transport="sse", port=args.port)


# Expose important items at package level
__all__ = ["main", "server_on_fastmcp"]
