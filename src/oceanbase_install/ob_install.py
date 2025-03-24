import asyncio
import logging
from typing import Any

from mcp import GetPromptResult
from mcp.server import Server
import mcp.types as types
from oceanbase_install import ob_install_function

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("oceanbase_mcp_server")

OCEANBASE_INSTALL_ODB = "OceanBase-Install-Via_OBD"
OCEANBASE_INSTALL_DOCKER = "使用docker安装oceanbase"

# Initialize server
app = Server("oceanbase_mcp_server")

PROMPT_OCEANBASE_INSTALL_OBD = types.Prompt(
    name=OCEANBASE_INSTALL_ODB,
    description="OceanBase数据库安装工作流（1、环境校验 → 2、安装准备 → 3、安装）",
    arguments=[
        types.PromptArgument(name="ob_version_install", description="指定需要安装的OB版本", required=True),
        types.PromptArgument(name="ob_version", description="安装的OB版本", required=True),
        types.PromptArgument(name="query", description="SQL 查询语句", required=False)
    ]
)

PROMPT_OCEANBASE_INSTALL_DOCKER = types.Prompt(
    name=OCEANBASE_INSTALL_DOCKER,
    description="基于docker安装OceanBase数据库工作流（1、检测是否有docker环境 → 2、安装）",
    arguments=[
        types.PromptArgument(name="使用docker安装的oceanbase的版本", description="指定需要安装的OB版本",
                             required=False),
    ]
)


@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [PROMPT_OCEANBASE_INSTALL_OBD, PROMPT_OCEANBASE_INSTALL_DOCKER]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult | None:
    if name == OCEANBASE_INSTALL_DOCKER:
        try:
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            text=f"""
                            使用Docker快速安装OceanBase,需按照以下步骤进行：
                            1、检测是否有docker环境
                            2、调用start_docker_ob mcp tool启动oceanbase
                            """
                        )
                    )
                ]
            )
        except Exception as e:
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="assistant",
                        content=types.TextContent(
                            text=f"执行失败: {str(e)}"
                        )
                    )
                ]
            )

    elif name == OCEANBASE_INSTALL_ODB:
        try:
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            text=f"""
                            使用OBD安装OceanBase,需按照以下步骤进行：
                            1、检测服务端是否能连接到公网，因为仅支持在线安装OBD。
                            2、在线安装OBD。注意仅支持在线安装，不支持离线安装。
                            3、通过OBD部署OceanBase集群。
                            4、启动通过OBD部署的 OceanBase 数据库
                            5、检查 OceanBase 集群状态
                            """
                        )
                    )
                ]
            )
        except Exception as e:
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="assistant",
                        content=types.TextContent(
                            text=f"执行失败: {str(e)}"
                        )
                    )
                ]
            )

    else:
        raise ValueError(f"Unknown prompt: {name}")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available OceanBase tools."""
    logger.info("Listing tools...")
    return [
        types.Tool(
            name="docker_env_check",
            description="检测是否有docker环境，基于docker安装OceanBase，必须要有docker环境",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": {"type": "string", "description": "Name of the table to describe"},
                        "description": "The SQL query to execute"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="start_docker_ob",
            description="通过Docker启动OceanBase数据库",
            inputSchema={
                "type": "object",
                "properties": {
                },
                "required": []
            }
        ),
        types.Tool(
            name="check_internet_connection",
            description="检测当前环境是否具有公网连接能力",
            inputSchema={
                "type": "object",
                "properties": {
                },
                "required": []
            }
        ),
        types.Tool(
            name="install_obd_online",
            description="在线安装OBD",
            inputSchema={
                "type": "object",
                "properties": {
                    "password": {
                        "type": "string",
                        "description": "密码"
                    }
                },
                "required": ["password"]
            }
        ),
        types.Tool(  # https://www.oceanbase.com/docs/community-obd-cn-1000000002023460
            name="deploy_oceanbase_via_obd",
            description="通过OBD部署 OceanBase 数据库",
            inputSchema={
                "type": "object",
                "properties": {
                },
                "required": []
            }
        ),
        types.Tool(  # https://www.oceanbase.com/docs/community-obd-cn-1000000002023460
            name="start_oceanbase_via_obd",
            description="启动通过OBD部署的 OceanBase 数据库",
            inputSchema={
                "type": "object",
                "properties": {
                },
                "required": []
            }
        ),
        types.Tool(  # https://www.oceanbase.com/docs/community-obd-cn-1000000002023460
            name="check_oceanbase_cluster_status",
            description="检查 OceanBase 集群状态",
            inputSchema={
                "type": "object",
                "properties": {
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""
    try:
        # Docker
        if name == "docker_env_check":
            result = ob_install_function.is_docker_available()
            if result:
                msg = "存在可执行的Docker环境。 "
            else:
                msg = "不存在可执行的Docker环境。"
            return [types.TextContent(type="text", text=str(msg))]

        elif name == "start_docker_ob":
            result = ob_install_function.start_oceanbase_with_log_check()
            return [types.TextContent(type="text", text=str(result))]

        # OBD
        elif name == "check_internet_connection":
            result = ob_install_function.check_internet_connection()
            return [types.TextContent(type="text", text=str(result))]

        elif name == "install_obd_online":
            password = arguments.get("password")
            if not password:
                raise ValueError("password is required")
            result = ob_install_function.install_obd(password=password)
            return [types.TextContent(type="text", text=str(result))]

        elif name == "deploy_oceanbase_via_obd":
            password = arguments.get("password")
            if not password:
                raise ValueError("password is required")
            result = ob_install_function.install_obd(password=password)
            return [types.TextContent(type="text", text=str(result))]

        elif name == "start_oceanbase_via_obd":
            password = arguments.get("password")
            if not password:
                raise ValueError("password is required")
            result = ob_install_function.install_obd(password=password)
            return [types.TextContent(type="text", text=str(result))]

        elif name == "check_oceanbase_cluster_status":
            password = arguments.get("password")
            if not password:
                raise ValueError("password is required")
            result = ob_install_function.install_obd(password=password)
            return [types.TextContent(type="text", text=str(result))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point to run the MCP server."""
    from mcp.server.stdio import stdio_server
    logger.info("Starting OceanBase Install MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(main())
