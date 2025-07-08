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
import subprocess


def run_obdiag_command(command: str) -> str:
    """
    运行 obdiag 命令并返回结果
    :param command: 完整的 obdiag 命令
    :return: 指令执行的输出结果
    """
    try:
        # 使用 subprocess 执行命令
        result = subprocess.run(
            f"{command} --inner_config obdiag.logger.silent=Ture",
            shell=True,
            text=True,
            capture_output=True,
        )
        # 返回标准输出或错误输出
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"


def register_tools(mcp: FastMCP):
    @mcp.tool()
    async def obdiag_check_run() -> str:
        """
        巡检集群，并返回巡检报告
        :return: 指令执行的输出结果
        """
        return run_obdiag_command("obdiag check run")

    @mcp.tool()
    async def obdiag_analyze_log() -> str:
        """
        分析集群日志，找出发生过的错误信息并返回
        :return: 指令执行的输出结果
        """
        return run_obdiag_command("obdiag analyze log")

    @mcp.tool()
    async def obdiag_display_list() -> str:
        """
        obdiag 集群信息查询功能功能，返回支持的指令列表
        :return: 支持的指令列表
        """

        return run_obdiag_command("obdiag display scene list")

    @mcp.tool()
    async def obdiag_display_run(scene: str, env_dict: dict = None) -> str:
        """
        obdiag 集群信息查询功能，执行获取的指令列表，需要功能来自obdiag_display_list的返回结果。只需要返回obdiag_display_list结果
        :param scene: 指令名，来自obdiag_display_list的返回结果，如 'obdiag display scene run --scene=observer.all_tenant',则赋值 scene=observer.all_tenant
        :param env_dict: 环境变量，来自obdiag_display_list的返回结果,只有在要求填入env的时候才需要赋值，如 'oobdiag display scene run --scene=observer.index --env database_name=test --env table_name=test',则赋值 env_dict={'database_name':'test','table_name':'test'}
        :return: 洞察结果
        """
        if env_dict is None:
            env_dict = {}
        cmd = "obdiag display scene run --scene={}".format(scene)
        if env_dict:
            for env in env_dict:
                env_name = env
                env_value = env_dict[env]
                cmd += " --env {}={}".format(env_name, env_value)
        return run_obdiag_command(cmd)
