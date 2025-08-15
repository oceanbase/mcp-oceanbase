import logging
import os
import time
from typing import Dict, Optional
from urllib import request, error
import json
import argparse
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mysql.connector import Error, connect
from bs4 import BeautifulSoup
import certifi
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("oceanbase_mcp_server")

load_dotenv()
global_config = None


# 为了解决 OceanBase MCP Server 在打成 Wheel 包 install 后，按 CTRL + C 程序不结束的问题
# ---------- 补丁开始 ----------
def _patched_run_sse_async(self, mount_path=None):
    from uvicorn import Config, Server

    starlette_app = self.sse_app(mount_path)
    config = Config(
        starlette_app,
        host=self.settings.host,
        port=self.settings.port,
        log_level=self.settings.log_level.lower(),
        timeout_graceful_shutdown=0,  # 设置立即强制退出
    )
    server = Server(config)
    return server.serve()


# 把 FastMCP 原来的 run_sse_async 替换成自己的
FastMCP.run_sse_async = _patched_run_sse_async
# ---------- 补丁结束 ----------

# Initialize server
app = FastMCP("oceanbase_mcp_server")


@app.resource("oceanbase://sample/{table}", description="table sample")
def table_sample(table: str) -> str:
    config = configure_db_connection()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM `%s` LIMIT 100", params=(table,))
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)

    except Error:
        return f"Failed to sample table: {table}"


@app.resource("oceanbase://tables", description="list all tables")
def list_tables() -> str:
    """List OceanBase tables as resources."""
    config = configure_db_connection()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")
                resp_header = "Tables of this table: \n"
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return resp_header + ("\n".join([",".join(columns)] + result))
    except Error as e:
        logger.error(f"Failed to list tables: {str(e)}")
        return "Failed to list tables"


def configure_db_connection(
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
) -> Dict[str, str | int]:
    """
    Retrieve OceanBase database connection information.
    If no parameters are provided, the configuration is loaded from environment variables.
    Otherwise, user-defined connection parameters will be used.

    :param host: Database host address. Defaults to environment variable OB_HOST or "localhost".
    :param port: Database port number. Defaults to environment variable OB_PORT or "2881".
    :param user: Database username. Required. Defaults to user input or environment variable OB_USER.
    :param password: Database password. Required. Defaults to user input or environment variable OB_PASSWORD.
    :param database: Database name. Required. Defaults to user input or environment variable OB_DATABASE.
    :return: A dictionary containing the database connection configuration.
    :raises ValueError: Raised if any of the required parameters (user, password, database) are missing.
    """
    global global_config
    if global_config:
        return global_config

    # Use user-provided values or fallback to environment variables
    config = {
        "host": host or os.getenv("OB_HOST", "localhost"),
        "port": port or os.getenv("OB_PORT", 2881),
        "user": user or os.getenv("OB_USER"),
        "password": password or os.getenv("OB_PASSWORD"),
        "database": database or os.getenv("OB_DATABASE"),
    }

    # Check if all required parameters are provided
    missing_params = [key for key in ["user", "database"] if not config.get(key)]
    if missing_params:
        logger.error(
            "Missing required database configuration. Please check the following parameters: %s",
            ", ".join(missing_params),
        )
        raise ValueError(
            "Unable to obtain database connection configuration information from environment variables. "
            "Please provide database connection configuration information."
        )

    # Log successfully loaded configuration (but hide sensitive information like the password)
    logger.info(
        "Database configuration loaded successfully: host=%s, port=%d, user=%s, database=%s",
        config["host"],
        int(config["port"]),
        config["user"],
        config["database"],
    )
    global_config = config

    return global_config


@app.tool()
def execute_sql(sql: str) -> str:
    """Execute an SQL on the OceanBase server."""
    config = configure_db_connection()
    logger.info(f"Calling tool: execute_sql  with arguments: {sql}")

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

                # Special handling for SHOW TABLES
                if sql.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = [f"Tables in {config['database']}: "]  # Header
                    result.extend([table[0] for table in tables])
                    return "\n".join(result)

                elif sql.strip().upper().startswith("SHOW COLUMNS"):
                    resp_header = "Columns info of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                elif sql.strip().upper().startswith("DESCRIBE"):
                    resp_header = "Description of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                # Regular SELECT queries
                elif sql.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return "\n".join([",".join(columns)] + result)

                # Regular SHOW queries
                elif sql.strip().upper().startswith("SHOW"):
                    rows = cursor.fetchall()
                    return str(rows)
                # process procedural invoke
                elif sql.strip().upper().startswith("CALL"):
                    rows = cursor.fetchall()
                    if not rows:
                        return "No result return."
                    # the first column contains the report text
                    return str(rows[0])
                # Non-SELECT queries
                else:
                    conn.commit()
                    return (
                        f"Sql executed successfully. Rows affected: {cursor.rowcount}"
                    )

    except Error as e:
        logger.error(f"Error executing SQL '{sql}': {e}")
        return f"Error executing sql: {str(e)}"


@app.tool()
def get_ob_ash_report(
    start_time: str,
    end_time: str,
    tenant_id: Optional[str] = None,
) -> str:
    """
    Get OceanBase Active Session History report.
    ASH can sample the status of all Active Sessions in the system at 1-second intervals, including:
        Current executing SQL ID
        Current wait events (if any)
        Wait time and wait parameters
        The module where the SESSION is located during sampling (PARSE, EXECUTE, PL, etc.)
        SESSION status records, such as SESSION MODULE, ACTION, CLIENT ID
    This will be very useful when you perform performance analysis.RetryClaude can make mistakes. Please double-check responses.
    """
    logger.info(
        f"Calling tool: get_ob_ash_report  with arguments: {start_time}, {end_time}, {tenant_id}"
    )
    if tenant_id is None:
        tenant_id = "NULL"
    # Construct the SQL query
    sql_query = f"""
        CALL DBMS_WORKLOAD_REPOSITORY.ASH_REPORT('{start_time}','{end_time}', NULL, NULL, NULL, 'TEXT', NULL, NULL, {tenant_id});
    """
    try:
        result = execute_sql(sql_query)
        logger.info(f"ASH report result: {result}")
        return result
    except Error as e:
        logger.error(f"Error get ASH report,executing SQL '{sql_query}': {e}")
        return f"Error get ASH report,{str(e)}"


@app.tool(name="get_current_time", description="Get current time")
def get_current_time() -> str:
    local_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    logger.info(f"Current time: {formatted_time}")
    return formatted_time


@app.tool()
def get_current_tenant() -> str:
    """
    Get the current tenant name from oceanbase.
    """
    logger.info("Calling tool: get_current_tenant")
    sql_query = "show tenant"
    try:
        result = execute_sql(sql_query)
        logger.info(f"Current tenant: {result}")
        return result[0][0]
    except Error as e:
        logger.error(f"Error executing SQL '{sql_query}': {e}")
        return f"Error executing query: {str(e)}"


@app.tool()
def get_all_server_nodes():
    """
    Get all server nodes from oceanbase.
    You need to be sys tenant to get all server nodes.
    """
    tenant = get_current_tenant()
    if tenant != "sys":
        raise ValueError("Only sys tenant can get all server nodes")

    logger.info("Calling tool: get_all_server_nodes")
    sql_query = "select * from DBA_OB_SERVERS"
    try:
        return execute_sql(sql_query)
    except Error as e:
        logger.error(f"Error executing SQL '{sql_query}': {e}")
        return f"Error executing query: {str(e)}"


@app.tool()
def get_resource_capacity():
    """
    Get resource capacity from oceanbase.
    You need to be sys tenant to get resource capacity.
    """
    tenant = get_current_tenant()
    if tenant != "sys":
        raise ValueError("Only sys tenant can get resource capacity")
    logger.info("Calling tool: get_resource_capacity")
    sql_query = "select * from oceanbase.GV$OB_SERVERS"
    try:
        return execute_sql(sql_query)
    except Error as e:
        logger.error(f"Error executing SQL '{sql_query}': {e}")
        return f"Error executing query: {str(e)}"


@app.tool()
def search_oceanbase_document(keyword: str) -> str:
    """
    This tool is designed to provide context-specific information about OceanBase to a large language model (LLM) to enhance the accuracy and relevance of its responses.
    The LLM should automatically extracts relevant search keywords from user queries or LLM's answer for the tool parameter "keyword".
    The main functions of this tool include:
    1.Information Retrieval: The MCP Tool searches through OceanBase-related documentation using the extracted keywords, locating and extracting the most relevant information.
    2.Context Provision: The retrieved information from OceanBase documentation is then fed back to the LLM as contextual reference material. This context is not directly shown to the user but is used to refine and inform the LLM’s responses.
    This tool ensures that when the LLM’s internal documentation is insufficient to generate high-quality responses, it dynamically retrieves necessary OceanBase information, thereby maintaining a high level of response accuracy and expertise.
    """
    logger.info(f"Calling tool: search_oceanbase_document,keyword:{keyword}")
    search_api_url = "https://cn-wan-api.oceanbase.com/wanApi/forum/docCenter/productDocFile/v3/searchDocList"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.oceanbase.com",
        "Referer": "https://www.oceanbase.com/",
    }
    qeury_param = {
        "pageNo": 1,
        "pageSize": 5,  # 一次搜索5条结果
        "query": keyword,
    }
    # 把字典转换为json字符串,然后编码为bytes
    qeury_param = json.dumps(qeury_param).encode("utf-8")
    req = request.Request(
        search_api_url, data=qeury_param, headers=headers, method="POST"
    )
    # 创建一个使用 certifi 的 SSL 上下文,解决https的报错问题
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        with request.urlopen(req, timeout=5, context=context) as response:
            response_body = response.read().decode("utf-8")
            json_data = json.loads(response_body)
            # 返回的结果中主要需要data字段中的内容
            data_array = json_data["data"]  # Parse JSON response
            result_list = []
            for item in data_array:
                doc_url = (
                    "https://www.oceanbase.com/docs/"
                    + item["urlCode"]
                    + "-"
                    + item["id"]
                )
                logger.info(f"doc_url:${doc_url}")
                content = get_ob_doc_content(doc_url, item["id"])
                result_list.append(content)
            return json.dumps(result_list, ensure_ascii=False)
    except error.HTTPError as e:
        logger.error(f"HTTP Error: {e.code} - {e.reason}")
        return "No results were found"
    except error.URLError as e:
        logger.error(f"URL Error: {e.reason}")
        return "No results were found"


def get_ob_doc_content(doc_url: str, doc_id: str) -> dict:
    doc_param = {"id": doc_id, "url": doc_url}
    doc_param = json.dumps(doc_param).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.oceanbase.com",
        "Referer": "https://www.oceanbase.com/",
    }
    doc_api_url = "https://cn-wan-api.oceanbase.com/wanApi/forum/docCenter/productDocFile/v4/docDetails"
    req = request.Request(doc_api_url, data=doc_param, headers=headers, method="POST")
    # 创建一个使用 certifi 的 SSL 上下文,解决https的报错问题
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        with request.urlopen(req, timeout=5, context=context) as response:
            response_body = response.read().decode("utf-8")
            json_data = json.loads(response_body)
            # 返回的结果中主要需要data字段中的数据
            data = json_data["data"]
            # docContent字段中是HTML文本
            soup = BeautifulSoup(data["docContent"], "html.parser")
            # 去除script/style/nav/header/footer这些元素
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()
            # 将HTML的标签去掉,只留文本
            text = soup.get_text()
            # 去除行前后的空格
            lines = (line.strip() for line in text.splitlines())
            # 去除空行
            text = "\n".join(line for line in lines if line)
            logger.info(f"text length:{len(text)}")
            # 如果文本太长了,就只截取前8000的字符
            if len(text) > 8000:
                text = text[:8000] + "... [content truncated]"
            # 重新组织下最后的结果,tdkInfo字段中包含文档的title/description/keyword这些信息
            tdkInfo = data["tdkInfo"]
            final_result = {
                "title": tdkInfo["title"],
                "description": tdkInfo["description"],
                "keyword": tdkInfo["keyword"],
                "content": text,
                "oceanbase_version": data["version"],
                "content_updatetime": data["docGmtModified"],
            }
            return final_result
    except error.HTTPError as e:
        logger.error(f"HTTP Error: {e.code} - {e.reason}")
        return {"result": "No results were found"}
    except error.URLError as e:
        logger.error(f"URL Error: {e.reason}")
        return {"result": "No results were found"}


def main():
    """Main entry point to run the MCP server."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        help="Specify the MCP server transport type as stdio or sse.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="SSE Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="SSE Port to listen on")
    args = parser.parse_args()
    transport = args.transport
    logger.info(f"Starting OceanBase MCP server with {transport} mode...")
    if transport == "sse":
        app.settings.host = args.host
        app.settings.port = args.port
    app.run(transport=transport)


if __name__ == "__main__":
    main()
