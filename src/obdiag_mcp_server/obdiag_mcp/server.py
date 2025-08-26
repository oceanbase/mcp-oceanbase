#!/usr/bin/env python
# -*- coding: UTF-8 -*
# Copyright (c) 2022 OceanBase
# OceanBase Diagnostic Tool is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import shutil

from fastmcp import FastMCP
from pathlib import Path
import importlib
import sys


sys.path.insert(0, str(Path(__file__).parent.parent.parent))
mcp = FastMCP("OBDiag MCP Server")

# 动态加载tools目录下的所有模块
for tool_file in Path(__file__).parent.glob("tools/*.py"):
    if tool_file.name == "__init__.py":
        continue
    module = importlib.import_module(f"tools.{tool_file.stem}")
    if hasattr(module, "register_tools"):
        module.register_tools(mcp)


# 确认obdiag是否安装,是否存在 obdiag 命令
def check_obdiag_installed():
    try:
        return shutil.which("obdiag") is not None
    except ImportError:
        return False


def check_config_exist():
    try:
        return Path(os.path.expanduser("~/.obdiag/config.yml")).exists()
    except ImportError:
        return False


# 启动 MCP 服务
if __name__ == "__main__":
    if not check_obdiag_installed():
        print("obdiag is not installed, please install obdiag first")
        sys.exit(1)
    if not check_config_exist():
        print("obdiag config is not exist, please check ~/.obdiag/config.yml is exist")
        sys.exit(1)
    # 根据输入的参数，判别是使用stdio还是sse还是streamable-http,如果是sse还是streamable-http，则需要指定port
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        print("run mcp with stdio")
        mcp.run(transport="stdio")
    elif len(sys.argv) > 1 and sys.argv[1] == "sse":
        print("run mcp with sse")
        if len(sys.argv) > 2:
            mcp.run(transport="sse", host="0.0.0.0", port=int(sys.argv[2]), path="/mcp")
        else:
            mcp.run(transport="sse", host="0.0.0.0", port=8000, path="/mcp")
    else:
        print("run mcp with streamable-http")
        if len(sys.argv) > 1:
            mcp.run(
                transport="streamable-http",
                host="0.0.0.0",
                port=int(sys.argv[2]),
                path="/mcp",
            )
        else:
            mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")
