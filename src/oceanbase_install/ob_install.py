import asyncio
import logging
from typing import Any

from mcp import GetPromptResult
from mcp.server import Server
import mcp.types as types
from pydantic import AnyUrl
from . import ob_install_function
from mcp.server.sse import SseServerTransport

import uvicorn

# Configure logging
logging.basicConfig(
    filename="ob_install.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("oceanbase_mcp_server")

OCEANBASE_INSTALL_ODB = "OceanBase-Install-Via_OBD"
OCEANBASE_INSTALL_DOCKER = "使用docker安装oceanbase"

# Initialize server
app = Server("oceanbase_mcp_server")

PROMPT_TEMPLATE = """
哦，嘿！👋我看到你选择了 OceanBase 的安装部署作为主题。太棒了！让我们开始吧！🚀

今天我们将进行一场精彩的演示，为您展示如何基于 **OceanBase MCP Server** 使用两种方式来安装并部署 OceanBase 数据库。这两种方式分别是：

1. **基于 OBD 工具安装 OceanBase 数据库**  
2. **基于 Docker 容器安装 OceanBase 数据库**

整个演示过程中，我会向您解释每一步的操作，并尽量让它互动且具有实际意义。我们还将探讨如何利用 MCP(Server 的核心功能：Prompts, Tools, Resources)帮助您完成高效的安装与部署。让我们开始探索吧！😊

---

### **第一步：创建场景叙述**

假设您是一名系统管理员，正在为您的公司进行 **OceanBase 数据库环境准备**。您的公司正在筹备一个**大规模数据分析项目**，计划将所有业务数据集中到一个高效的分布式数据库中，以提高查询性能和数据处理速度。

一切看起来很顺利，但偏偏供应商的文件配置错乱了，以至于到现在您手里没有完备的部署说明。🙃而且问题出在……有人自作聪明地将安装指南标记成了 "重要假期文档"，藏到了公司的节假日文件夹里。现在公司业务决策层要求您在**一天之内搭建并验证 OceanBase 数据库环境**，任务紧急！🌟

---

### **第二步：选择安装部署方式**

我们有两种方式可以安装 OceanBase 数据库：  
1. **基于 OBD 工具**：OBD 是 OceanBase 官方提供的自动化部署工具，简单快速，适合初学者。  
2. **基于 Docker 容器**：Docker 提供了轻量化部署的能力，尤其适合容器化场景。  

请选择您喜欢的方式，我们将基于您选择的场景完成部署任务。😊

请选择方式：
- [1] 基于 OBD 工具安装 OceanBase 数据库  
- [2] 基于 Docker 容器安装 OceanBase 数据库  

---

### **第三步：基于用户选项引导安装部署**

#### 如果用户选择 [1]: 基于 OBD 工具安装
- **解释：** 我们将使用 OBD 工具快速安装 OceanBase 数据库。OBD 的全称是 OceanBase Deployer，它是 OceanBase 官方提供的一款自动化部署工具。
  
- **安装步骤：**
  1. **安装 OBD 工具**：  

  2. **初始化 OceanBase 集群**：  

  3. **验证部署成功**：  


#### 如果用户选择 [2]: 基于 Docker 容器安装
- **解释：** 使用 Docker 容器安装 OceanBase 数据库。

---

### **最后一步：总结与下一步提示**

不论您选择哪种方式，您已经完成了 OceanBase 数据库的基础部署！🎉接下来，您可以进一步探索数据库的监控、数据表创建以及性能优化。

---

嘿！这只是 MCP Server 与 OceanBase 的演示起点！🌟接下来，您还可以尝试扩展更多业务场景，例如设置分布式集群、多租户支持，或者探索 OceanBase 的性能优化工具。如果需要更多帮助，请随时召唤我！😊

  
"""

PROMPT_OCEANBASE_INSTALL = types.Prompt(
    name="oceanbase_install",
    description="A prompt to deploy and install oceanbase",
    arguments=[],
)

PROMPT_OCEANBASE_INSTALL_OBD = types.Prompt(
    name=OCEANBASE_INSTALL_ODB,
    description="基于OBD安装OceanBase数据库的工作流：",
    arguments=[],
)

PROMPT_OCEANBASE_INSTALL_DOCKER = types.Prompt(
    name=OCEANBASE_INSTALL_DOCKER,
    description="基于docker安装OceanBase数据库工作流（1、检测是否有docker环境 → 2、安装）",
    arguments=[
        types.PromptArgument(
            name="使用docker安装的oceanbase的版本",
            description="指定需要安装的OB版本",
            required=False,
        ),
    ],
)


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """List basic Hologres resources."""
    return [
        types.Resource(
            uri="oceanbase:///install",
            name="安装部署OceanBase方式方法",
            description="例举出安装部署OceanBase方式方法",
            mimeType="text/plain",
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read resource content based on URI."""
    uri_str = str(uri)
    if not uri_str.startswith("oceanbase:///"):
        raise ValueError(f"Invalid URI scheme: {uri_str}")

    if uri_str.endswith("install"):
        return "\n".join(
            ["请用户从以下方式中选择一种安装：", "基于Docker安装", "基于OBD安装"]
        )


@app.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    logger.info("List prompts...")
    return [
        PROMPT_OCEANBASE_INSTALL,
        PROMPT_OCEANBASE_INSTALL_OBD,
        PROMPT_OCEANBASE_INSTALL_DOCKER,
    ]


oceanbase_install_select = "你想用哪种方式安装ob?docker方式还是obd方式"


@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult | None:
    logger.info("Get prompts...")
    if name == "oceanbase_install":
        return types.GetPromptResult(
            description="prompt for oceanbase install",
            messages=[
                types.PromptMessage(
                    role="user", content=types.TextContent(text=PROMPT_TEMPLATE.strip())
                )
            ],
        )

    elif name == OCEANBASE_INSTALL_DOCKER:
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
                            3、docker启动的时间较长,请告诉用户耐心等待
                            """
                        ),
                    )
                ]
            )
        except Exception as e:
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="assistant",
                        content=types.TextContent(text=f"执行失败: {str(e)}"),
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
                        ),
                    )
                ]
            )
        except Exception as e:
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="assistant",
                        content=types.TextContent(text=f"执行失败: {str(e)}"),
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
            description="使用docker方式安装oceanbase(简称ob)时需要用到,检测是否有docker环境,这是docker方式安装oceanbase的第一个需要调用的工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "host": {
                        "type": {
                            "type": "string",
                            "description": "Name of the table to describe",
                        },
                        "description": "The SQL query to execute",
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="start_docker_ob",
            description="使用docker方式安装oceanbase(简称ob)时需要用到,通过Docker启动OceanBase数据库,这是第二个需要调用的工具",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="check_internet_connection",
            description="使用OBD的方式安装oceanbase(简称ob)时需要用到,这是使用OBD的方式安装oceanbase的第一个需要调用的工具",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="install_obd_online",
            description="使用OBD的方式安装oceanbase(简称ob)时需要用到,安装OBD,这是使用OBD的方式安装oceanbase的第二个需要调用的工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "password": {
                        "type": "string",
                        "description": "安装OBD需要服务器用户密码，以正确在线安装OBD",
                    }
                },
                "required": ["password"],
            },
        ),
        types.Tool(  # https://www.oceanbase.com/docs/community-obd-cn-1000000002023460
            name="deploy_oceanbase_via_obd",
            description="""使用OBD的方式安装oceanbase(简称ob)时需要用到,通过OBD部署 OceanBase 数据库,这是使用OBD的方式安装oceanbase的第三个需要调用的工具
            在执行该工具之前,请用户输入下一步需要的参数,等用户输入信息后再执行。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {"type": "string", "description": "部署集群名"},
                    "servers": {
                        "type": "array",
                        "description": """通过询问用户，进行构造，比如: [
                                                                        ["172.19.33.2", "zone1"],
                                                                        ["172.19.33.3", "zone2"], 
                                                                        ["172.19.33.4", "zone3"]
                                                                    ]
                        """,
                    },
                    "global_config": {
                        "type": "object",
                        "description": """通过询问用户，进行构造，比如: {
                                                                        "memory_limit": "4G",
                                                                        "system_memory": "1G",
                                                                        "datafile_size": "2G",
                                                                        "datafile_next": "2G",
                                                                        "datafile_maxsize": "20G",
                                                                        "log_disk_size": "14G",
                                                                        "cpu_count": 4,
                                                                        "production_mode": False,
                                                                        "enable_syslog_wf": False,
                                                                        "max_syslog_file_count": 4,
                                                                    }
                        """,
                    },
                    "server_common_config": {
                        "type": "object",
                        "description": """通过询问用户，进行构造，比如: {
                                                                        "mysql_port": 2881,
                                                                        "rpc_port": 2882,
                                                                        "obshell_port": 2886,
                                                                        "home_path": "/root/observer",
                                                                    }
                                                                    """,
                    },
                    "user_config": {
                        "type": "object",
                        "description": """通过询问用户，进行构造，比如: {
                                                                        "username": "jackson",
                                                                        "password": "123456",
                                                                        "port": 22,
                                                                        "timeout": 30,
                                                                    }
                                                    """,
                    },
                },
                "required": ["cluster_name", "servers"],
            },
        ),
        types.Tool(  # https://www.oceanbase.com/docs/community-obd-cn-1000000002023460
            name="start_oceanbase_via_obd",
            description="使用OBD的方式安装oceanbase(简称ob)时需要用到,启动oceanbase集群,这是使用OBD的方式安装oceanbase的第四个需要调用的工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "从第三步拿到的cluster_name",
                    }
                },
                "required": [],
            },
        ),
        types.Tool(  # https://www.oceanbase.com/docs/community-obd-cn-1000000002023460
            name="check_oceanbase_cluster_status",
            description="使用OBD的方式安装oceanbase(简称ob)时需要用到,检查oceanbase集群状态,这是使用OBD的方式安装oceanbase的第五个需要调用的工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "从第三步拿到的cluster_name",
                    }
                },
                "required": [],
            },
        ),
        types.Tool(  # https://www.oceanbase.com/docs/community-obd-cn-1000000002023439
            name="create_tenant_via_obd",
            description="使用OBD的方式安装oceanbase(简称ob)时需要用到,创建租户,这是使用OBD的方式安装oceanbase的第六个需要调用的工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "从第三步拿到的cluster_name",
                    },
                    "tenant_name": {
                        "type": "string",
                        "description": "租户名。",
                    },
                    "max_cpu": {
                        "type": "string",
                        "description": "租户可用最大 CPU 数。为 0 时使用集群剩余全部可用 CPU。",
                    },
                    "memory_size": {
                        "type": "string",
                        "description": "租户可用内存单元大小，仅支持 OceanBase 数据库 V4.0.0.0 及以上版本。",
                    },
                    "log_disk_size": {
                        "type": "string",
                        "description": "指定租户的 Unit 日志盘大小。默认值为 3 倍的内存规格值。最小值为 2G。",
                    },
                    "optimize": {
                        "type": "string",
                        "description": """
                                        设置租户负载类型，未设置的情况下，会提供交互式选项供用户选择负载类型。可选值如下：
                                        express_oltp：适用于贸易、支付核心系统、互联网高吞吐量应用程序等工作负载。没有外键等限制、没有存储过程、没有长交易、没有大交易、没有复杂的连接、没有复杂的子查询。
                                        complex_oltp：适用于银行、保险系统等工作负载。他们通常具有复杂的联接、复杂的相关子查询、用 PL 编写的批处理作业，以及长事务和大事务。有时对短时间运行的查询使用并行执行。
                                        olap：适用于实时数据仓库分析场景。
                                        htap：适用于混合 OLAP 和 OLTP 工作负载。通常用于从活动运营数据、欺诈检测和个性化建议中获取即时见解。
                                        kv：适用于键值工作负载和类似 Hbase 的宽列工作负载，这些工作负载通常具有非常高的吞吐量并且对延迟敏感。
                                      """,
                    },
                },
                "required": ["tenant_name"],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""
    logger.info("Call tools...")
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
            cluster_name = arguments.get("cluster_name")
            if not cluster_name:
                raise ValueError("cluster_name is required")
            servers = arguments.get("servers")
            if not servers:
                raise ValueError("servers is required")

            config = ob_install_function.generate_ob_config(servers=servers)
            result = ob_install_function.deploy_oceanbase(
                cluster_name=cluster_name, config=config
            )
            return [types.TextContent(type="text", text=str(result))]

        elif name == "start_oceanbase_via_obd":
            cluster_name = arguments.get("cluster_name")
            if not cluster_name:
                raise ValueError("cluster_name is required")
            result = ob_install_function.start_oceanbase_cluster(
                cluster_name=cluster_name
            )
            return [types.TextContent(type="text", text=str(result))]

        elif name == "check_oceanbase_cluster_status":
            cluster_name = arguments.get("cluster_name")
            if not cluster_name:
                raise ValueError("cluster_name is required")
            result = ob_install_function.check_oceanbase_cluster_status(
                cluster_name=cluster_name
            )
            return [types.TextContent(type="text", text=str(result))]

        elif name == "create_tenant_via_obd":
            cluster_name = arguments.get("cluster_name")
            if not cluster_name:
                raise ValueError("cluster_name is required")
            tenant_name = arguments.get("tenant_name")
            if not tenant_name:
                raise ValueError("tenant_name is required")
            result = ob_install_function.create_tenant_via_obd(
                deploy_name=cluster_name,
                tenant_name=tenant_name,
                max_cpu=arguments.get("max_cpu"),
                memory_size=arguments.get("memory_size"),
                log_disk_size=arguments.get("log_disk_size"),
                optimize=arguments.get("optimize"),
            )
            return [types.TextContent(type="text", text=str(result))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def run_stdio_async() -> None:
    from mcp.server.stdio import stdio_server

    logger.info("Starting OceanBase Install MCP stdio server...")
    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise


async def run_sse_async(args) -> None:
    logger.info("Starting OceanBase Install MCP SSE server...")
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.requests import Request

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            # 请求的作用域,包含请求的上下文信息
            request.scope,
            # 用于接收请求数据的异步函数
            request.receive,
            # 用于向客户端发送消息的异步函数
            request._send,
            # 连接后,会返回两个流,read_stream 用于读取来自客户端的数据,write_stream用于发送数据到客户端
        ) as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )

    starlette_app = Starlette(
        debug=args.debug,
        routes=[
            # 当客户端请求/sse时,调用handle_sse处理
            Route("/sse", endpoint=handle_sse),
            # 当客户端请求/message时,调用sse的handle_post_message处理
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    config = uvicorn.Config(
        starlette_app,
        host=args.host,
        port=args.port,
        log_level=args.loglevel,
        timeout_keep_alive=5,  # 5秒后超时
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    logger.info("Starting OceanBase install MCP server...")
    """Main entry point to run the MCP server."""
    # argparse是一个标准库,用于解析命令行参数
    import argparse

    # description的作用是提供帮助信息,当用户输入--help时会显示
    parser = argparse.ArgumentParser(description="Run Oceanbase MCP server parameters")
    # --host 绑定的主机,0.0.0.0表示将在所有可用的网络接口上监听
    parser.add_argument(
        "--transport",
        default="stdio",
        help="Transports use in the Model Context Protocol",
    )
    parser.add_argument("--host", default="0.0.0.0", help="SSE Host to bind to")
    parser.add_argument("--port", type=int, default=8020, help="SSE Port to listen on")
    parser.add_argument(
        "--debug", type=bool, default=False, help="wether enable the debugg mode of SSE"
    )
    parser.add_argument(
        "--loglevel",
        default="info",
        choices=["debug", "info", "warn", "error"],
        help="Log level of SSE",
    )
    # 调用parse_args()方法,程序将解析命令行传入的参数
    args = parser.parse_args()
    transport = args.transport
    if transport not in ["stdio", "sse"]:
        raise ValueError(f"Unknown transport: {transport}")
    if transport == "stdio":
        await run_stdio_async()
    else:
        await run_sse_async(args)


if __name__ == "__main__":
    asyncio.run(main())
