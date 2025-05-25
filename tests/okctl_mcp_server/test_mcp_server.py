import pytest
from fastmcp.client import Client
from mcp.types import Tool

from okctl_mcp_server import mcp

# Register all tools
from okctl_mcp_server.tools import (
    backup_policy,
    clusters,
    components,
    tenants,
)


def test_server_init():
    """Test if the server is initialized correctly"""
    assert mcp is not None
    assert mcp.name == "okctl-mcp-server"


@pytest.mark.asyncio
async def test_list_tools():
    """Test if the server can list all tools"""
    async with Client(mcp) as client:
        tools = await client.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check tool format
        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")


@pytest.mark.asyncio
async def test_call_tool_invalid_name():
    """Test if the server can call a tool with invalid name"""
    with pytest.raises(Exception, match="Unknown tool: invalid_tool"):
        async with Client(mcp) as client:
            await client.call_tool("invalid_tool", {})


@pytest.mark.asyncio
async def test_call_tool_missing_args():
    """Test if the server can call a tool without required arguments"""
    with pytest.raises(Exception) as exc_info:
        async with Client(mcp) as client:
            await client.call_tool("create_cluster", {})

    error_msg = str(exc_info.value)
    assert any(
        expected in error_msg for expected in ["Missing required argument", "Field required"]
    ), f"Unexpected error message: {error_msg}"
