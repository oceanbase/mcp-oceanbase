from oceanbase_install import ob_install
import asyncio


def main():
    """Main entry point for the package."""
    asyncio.run(ob_install.main())


# Expose important items at package level
__all__ = ["main", "ob_install"]
