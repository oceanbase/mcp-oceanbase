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
    rfc1123_time = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return rfc1123_time


def generate_signature(SK, string_to_sign):
    """
    :param access_key_secret: Access Key Secret (SK)
    :param string_to_sign: string to sign
    :return: Base64 signature
    """
    key_bytes = SK.encode("utf-8")
    string_bytes = string_to_sign.encode("utf-8")
    hmac_sha1 = hmac.new(key_bytes, string_bytes, hashlib.sha1)
    signature = base64.b64encode(hmac_sha1.digest()).decode("utf-8")

    return signature


@mcp.prompt()
def system_prompt():
    """Basic Introduction"""
    return """OCP stands for OceanBase Cloud Platform, which is the management and control platform for the OceanBase database. It supports rich API access and controls OceanBase database clusters.
You are an OCP API assistant. You can reasonably infer the order of API calls based on user input, but the API addresses and parameters must strictly follow the Prompt references. Do not assume parameters arbitrarily.
    """


def _gen_prompt(doc_path: str):
    descriptions = []

    if not os.path.exists(doc_path):
        raise Exception("Doc path do not exists:" + str(doc_path))

    if os.path.isfile(doc_path):
        with open(doc_path, "r", encoding="utf-8") as f:
            return f.read()

    for filename in os.listdir(doc_path):
        if filename.endswith(".md"):
            file_path = os.path.join(doc_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                descriptions.append(f.read())

    return "\n".join(descriptions)


@mcp.prompt()
def ocp_api_all_description():
    """Get the abbreviated version of all OCP API documentation."""

    return _gen_prompt(DOC_DIR)


@mcp.prompt()
def ocp_api_cluster_description():
    """Get the OCP cluster api documentation."""
    return _gen_prompt(DOC_DIR + "/3.cluster-information.md")


@mcp.prompt()
def ocp_api_monitor_description():
    """Get the OCP monitoring api documentation."""
    extra_prompt = """
    ## Important rules:
- [!MUST] You should first obtain the list of monitoring metrics via metricGroups, and then retrieve the monitoring data via metricsWithLabel.
- [!MUST] The labels and groupBy parameters in the query_param of metricsWithLabel must be filled based on the return results of metricGroups.
- [!MUST] If the metric requested by the user has multiple similar metric items, you should list these metrics and ask the user to further specify the desired metric.
    """
    return _gen_prompt(DOC_DIR + "/8.monitoring.md") + "\n" + extra_prompt


@mcp.prompt()
def ocp_api_tenant_description():
    """Get the OCP tenant api documentation."""
    return _gen_prompt(DOC_DIR + "/4.tenant-information.md")


@mcp.prompt()
def ocp_api_sql_performance_description():
    """Get the OCP sql performance api documentation."""
    return _gen_prompt(DOC_DIR + "/14.sql-performance.md")


@mcp.prompt()
def ocp_api_user_description():
    """Get the OCP user api documentation."""
    return _gen_prompt(DOC_DIR + "/12.ob-user-and-permission-management.md")


@mcp.prompt()
def ocp_api_backup_restore_description():
    """Get the OCP backup and restore API documentation."""
    return _gen_prompt(DOC_DIR + "/15.backup-and-restore.md")


@mcp.tool()
def query_ocp_api(
    method: str,
    request_path: str,
    md5payload: str = "",
    query_param: dict | None = None,
    protocal: str = "application/json",
    ocp_header: str = "from-mcp",
):
    """

    Args:
        method (str): HTTP request method, such as 'GET', 'POST', etc.
        md5payload (str): The MD5 value of the request body, usually an empty string
        request_path (str): API request path, starting with '/'
        query_param (dict): Request parameters in key/value dictionary format, can be None
        protocal (str, optional): Content type. Defaults to 'application/json'
        ocp_header (str, optional): OCP source identifier. Defaults to 'from-mcp'

    Returns:
        str: The JSON string of the API response
    """
    request_time = gen_rfc_time()

    param_str = ""
    if query_param:
        flat_params = {}
        for key, value in query_param.items():
            if isinstance(value, (list, tuple)):
                flat_params[key] = ",".join(map(str, value))
            else:
                flat_params[key] = str(value)

        sorted_params = []
        for key in sorted(flat_params.keys()):
            encoded_key = requests.utils.quote(key, safe="")
            encoded_value = requests.utils.quote(flat_params[key], safe="")
            sorted_params.append(f"{encoded_key}={encoded_value}")

        param_str = "?" + "&".join(sorted_params)

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
