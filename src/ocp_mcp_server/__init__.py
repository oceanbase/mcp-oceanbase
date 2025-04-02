from .server import mcp


def main():
    """Main entry point for the package."""
    mcp.run(transport="stdio")


# Expose important items at package level
__all__ = ['main']
