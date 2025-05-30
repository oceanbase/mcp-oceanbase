import argparse
import logging
import importlib
from typing import List
from fastmcp import FastMCP

# 创建全局mcp实例供所有模块使用
mcp = FastMCP("okctl-mcp-server", version="0.1.0", loglevel="ERROR")


@mcp.prompt()
def system_prompt() -> str:
    """基础概念介绍，必须加载"""
    return """okctl是 OceanBase 集群管理工具 okctl 的命令行接口，用于管理 OceanBase 集群，租户，备份策略等资源，并且支持相关组件的安装和更新。
你可以根据用户输入合理推断 API 调用顺序，但 API 地址和传参必须参考 Prompt 严格使用，不能自己臆测参数。
"""


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("okctl_mcp_server")


def load_tools(tool_names: List[str]) -> None:
    """动态加载指定的工具模块。

    Args:
        tool_names: 要加载的工具模块名称列表
    """
    for tool_name in tool_names:
        try:
            logger.info("加载工具模块: %s", tool_name)
            importlib.import_module(f"okctl_mcp_server.tools.{tool_name}")
        except ImportError as e:
            logger.warning("无法加载工具模块 %s: %s", tool_name, e)


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="OceanBase cluster management tool MCP server"
    )
    parser.add_argument(
        "--use-sse", action="store_true", help="Use Server-Sent Events (SSE) transport"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for SSE transport (default: 8000)"
    )
    parser.add_argument(
        "--tools",
        type=str,
        default="all",
        help="指定要启用的工具，用逗号分隔。选项: all, clusters, tenants, backup_policy, components, sql",
    )
    args = parser.parse_args()

    # 根据参数加载相应的工具模块
    if args.tools.lower() == "all":
        # 加载所有工具模块
        logger.info("启用所有工具")
        load_tools(
            ["clusters", "tenants", "backup_policy", "components", "sql", "install"]
        )
    else:
        # 解析工具参数
        tool_modules = [module.strip().lower() for module in args.tools.split(",")]
        load_tools(["install"])
        load_tools(tool_modules)
    if args.use_sse:
        logger.info("Starting server with SSE on port %s", args.port)
        mcp.run(transport="sse", port=args.port)
    else:
        logger.info("Starting server with stdio transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
