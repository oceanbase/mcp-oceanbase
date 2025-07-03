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

from fastmcp import FastMCP
from pathlib import Path
import importlib
import subprocess
import os
import sys


sys.path.insert(0, str(Path(__file__).parent.parent.parent))
mcp = FastMCP("OBDiag MCP Server")

# 动态加载tools目录下的所有模块
for tool_file in Path(__file__).parent.glob("tools/*.py"):
    if tool_file.name == "__init__.py":
        continue
    module = importlib.import_module(f"src.obdiag_mcp_server.tools.{tool_file.stem}")
    if hasattr(module, "register_tools"):
        module.register_tools(mcp)

# 启动 MCP 服务
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")
