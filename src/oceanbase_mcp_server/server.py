import logging
import os
import time
from typing import Dict, Literal, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mysql.connector import Error, connect

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("oceanbase_mcp_server")

load_dotenv()
global_config = None

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


@app.tool(name="configure_db_connection")
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
    missing_params = [
        key for key in ["user", "password", "database"] if not config.get(key)
    ]
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
def execute_sql(query: str) -> str:
    """Execute an SQL query on the OceanBase server."""
    config = configure_db_connection()
    logger.info(f"Calling tool: execute_sql  with arguments: {query}")

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Special handling for SHOW TABLES
                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = [f"Tables in {config['database']}: "]  # Header
                    result.extend([table[0] for table in tables])
                    return "\n".join(result)

                elif query.strip().upper().startswith("SHOW COLUMNS"):
                    resp_header = "Columns info of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                elif query.strip().upper().startswith("DESCRIBE"):
                    resp_header = "Description of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                # Regular SELECT queries
                elif query.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return "\n".join([",".join(columns)] + result)

                # Regular SHOW queries
                elif query.strip().upper().startswith("SHOW"):
                    rows = cursor.fetchall()
                    return rows

                # Non-SELECT queries
                else:
                    conn.commit()
                    return (
                        f"Query executed successfully. Rows affected: {cursor.rowcount}"
                    )

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        return f"Error executing query: {str(e)}"


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
    config = configure_db_connection()
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
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchall()
                logger.info(f"ASH report result: {result}")
                if not result:
                    return "No data found in ASH report."
                # the first column contains the report text
                return str(result[0])
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


def main(transport: Literal["stdio", "sse"] = "stdio", port: int = 8000):
    """Main entry point to run the MCP server."""
    logger.info(f"Starting OceanBase MCP server with {transport} mode...")
    app.settings.port = port
    app.run(transport=transport)


if __name__ == "__main__":
    app.run()
