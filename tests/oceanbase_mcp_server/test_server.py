import pytest

from oceanbase_mcp_server.server_on_fastmcp import app


def test_server_initialization():
    """Test that the server initializes correctly."""
    assert app.name == "oceanbase_mcp_server"
