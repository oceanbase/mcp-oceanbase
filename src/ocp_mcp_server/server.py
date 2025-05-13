# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone

import requests
from mcp.server.fastmcp import FastMCP

AK = os.getenv("AK")
SK = os.getenv("SK")
ADDRESS = os.getenv("ADDRESS")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(CURRENT_DIR, "ocp-doc-min")

mcp = FastMCP("ocp_mcp_server")


def gen_rfc_time():
    now = datetime.now(timezone.utc)
    # 格式化为 RFC-1123 格式
    rfc1123_time = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return rfc1123_time


def generate_signature(SK, string_to_sign):
    """
    使用 HMAC-SHA1 算法生成签名，并进行 Base64 编码
    :param access_key_secret: Access Key Secret (SK)
    :param string_to_sign: 待签名字符串
    :return: Base64 编码后的签名
    """
    # 将 Access Key Secret 和待签名字符串转换为字节
    key_bytes = SK.encode("utf-8")
    string_bytes = string_to_sign.encode("utf-8")
    # 使用 HMAC-SHA1 算法生成签名
    hmac_sha1 = hmac.new(key_bytes, string_bytes, hashlib.sha1)
    # 对签名进行 Base64 编码
    signature = base64.b64encode(hmac_sha1.digest()).decode("utf-8")

    return signature


@mcp.prompt()
def system_prompt():
    """基础概念介绍，必须加载"""
    return """OCP 是 OceanBase Cloud Platform 的缩写，是 OceanBase 数据库的管控平台。支持丰富的 API 访问、控制 OceanBase 数据库集群。
        你是 OCP API 助手，你可以根据用户输入合理推断 API 调用顺序，但 API 地址和传参必须参考 Prompt 严格使用，不能自己臆测参数。
    """


def _gen_prompt(doc_path: str):
    descriptions = []

    # 确保 prompt 目录存在
    if not os.path.exists(doc_path):
        raise Exception("Doc path do not exists:" + str(doc_path))

    if os.path.isfile(doc_path):
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()

    # 遍历所有 md 文件
    for filename in os.listdir(doc_path):
        if filename.endswith(".md"):
            file_path = os.path.join(doc_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                descriptions.append(f.read())

    # 用换行符连接所有文件内容
    return "\n".join(descriptions)


@mcp.prompt()
def ocp_api_all_description():
    """获取 OCP 所有 API 描述文档，精简版"""

    return _gen_prompt(DOC_DIR)


@mcp.prompt()
def ocp_api_cluster_description():
    """获取 OCP 集群 API 描述文档"""
    return _gen_prompt(DOC_DIR + "/3.cluster-information.md")


@mcp.prompt()
def ocp_api_monitor_description():
    """获取 OCP 监控 API 描述文档"""
    extra_prompt = """
    ## 重要规则:
    - [!必须]你应当先通过 metricGroups 获取监控指标列表，再通过 metricsWithLabel 获取监控数据。
    - [!必须]metricsWithLabel 的 query_param 参数中的 labels,groupBy 需要根据 metricGroups 的返回结果填写。
    - [!必须]如果用户要求的指标有多个相似的指标项，你应当列出这些指标，让用户进一步明确想要的指标。
    """
    return _gen_prompt(DOC_DIR + "/8.monitoring.md") + "\n" + extra_prompt


@mcp.prompt()
def ocp_api_tenant_description():
    """获取 OCP 租户 API 描述文档"""
    return _gen_prompt(DOC_DIR + "/4.tenant-information.md")


@mcp.prompt()
def ocp_api_sql_performance_description():
    """获取 OCP SQL 性能 API 描述文档"""
    return _gen_prompt(DOC_DIR + "/14.sql-performance.md")


@mcp.prompt()
def ocp_api_user_description():
    """获取 OCP 数据库用户 API 描述文档"""
    return _gen_prompt(DOC_DIR + "/12.ob-user-and-permission-management.md")


@mcp.prompt()
def ocp_api_backup_restore_description():
    """获取 OCP 备份恢复 API 描述文档"""
    return _gen_prompt(DOC_DIR + "/15.backup-and-restore.md")


@mcp.tool()
def query_ocp_api(
    method: str,
    md5payload: str,
    request_path: str,
    query_param: dict = None,
    protocal: str = "application/json",
    ocp_header: str = "from-mcp",
):
    """
    发送 OCP API 请求, 以 JSON 格式返回。

    Args:
        method (str): HTTP 请求方法，如 'GET', 'POST' 等
        md5payload (str): 请求体的 MD5 值，通常为空字符串
        request_path (str): API 请求路径，以 '/' 开头
        query_param (dict): 请求参数 key/value 字典格式，可以为 None
        protocal (str, optional): 内容类型. 默认为 'application/json'
        ocp_header (str, optional): OCP 来源标识. 默认为 'from-mcp'

    Returns:
        str: API 响应的 JSON 字符串
    """
    request_time = gen_rfc_time()

    # 处理查询参数
    param_str = ""
    if query_param:
        # 将嵌套的参数展平并转换为字符串
        flat_params = {}
        for key, value in query_param.items():
            if isinstance(value, (list, tuple)):
                # 将列表转换为逗号分隔的字符串
                flat_params[key] = ",".join(map(str, value))
            else:
                flat_params[key] = str(value)

        # 按键排序并进行 URL 编码
        sorted_params = []
        for key in sorted(flat_params.keys()):
            encoded_key = requests.utils.quote(key, safe="")
            encoded_value = requests.utils.quote(flat_params[key], safe="")
            sorted_params.append(f"{encoded_key}={encoded_value}")

        param_str = "?" + "&".join(sorted_params)

    # 构建签名字符串
    path_with_query = request_path + param_str

    query_body = "\n".join(
        [
            method,
            md5payload,
            protocal,
            request_time,
            ADDRESS,
            "x-ocp-origin:" + ocp_header,
            path_with_query,
        ]
    )

    print(query_body)  # 用于调试
    signature = generate_signature(SK, query_body)

    headers = {
        "Authorization": f"OCP-ACCESS-KEY-HMACSHA1 {AK}:{signature}",
        "Date": request_time,
        "x-ocp-origin": ocp_header,
        "Content-Type": protocal,
    }

    url = "http://" + ADDRESS + path_with_query
    logging.info("request url:" + url)
    logging.info("request headers:" + str(headers))

    response = requests.get(url, headers=headers)
    try:
        result = json.dumps(response.json())
        return result
    except Exception as e:
        logging.error("response error ,maybe api path is incorrect:" + str(e))


if __name__ == "__main__":
    mcp.run(transport="sse")
