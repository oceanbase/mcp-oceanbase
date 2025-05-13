from ocp_mcp_server import server


def main():
    """Main entry point for the package."""
    server.mcp.run(transport="sse")


# Expose important items at package level

__all__ = ["main", "server"]
