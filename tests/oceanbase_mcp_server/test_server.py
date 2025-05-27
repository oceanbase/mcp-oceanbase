import pytest

from oceanbase_mcp_server.server_on_fastmcp import app, call_tool


def test_server_initialization():
    """Test that the server initializes correctly."""
    assert app.name == "oceanbase_mcp_server"


@pytest.mark.asyncio
async def test_call_tool_invalid_name():
    """Test calling a tool with an invalid name."""
    with pytest.raises(ValueError, match="Unknown tool"):
        await call_tool("invalid_tool", {})


@pytest.mark.asyncio
async def test_call_tool_missing_query():
    """Test calling execute_sql without a query."""
    with pytest.raises(ValueError, match="Query is required"):
        await call_tool("execute_sql", {})


# Skip database-dependent tests if no database connection
@pytest.mark.asyncio
@pytest.mark.skipif(
    not all(
        [
            pytest.importorskip("mysql.connector"),
            pytest.importorskip("oceanbase_mcp_server"),
        ]
    ),
    reason="OceanBase connection not available",
)
