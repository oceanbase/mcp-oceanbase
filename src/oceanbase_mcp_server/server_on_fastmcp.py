import logging
import os
from typing import Literal, Optional, Dict

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mysql.connector import connect, Error

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
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
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
        config["port"],
        config["user"],
        config["database"],
    )
    global_config = config

    return global_config


@app.tool(
    name="execute_sql", description="Execute an SQL query on the OceanBase server"
)
def call_tool(query: str) -> str:
    """Execute SQL commands."""
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

                # Non-SELECT queries
                else:
                    conn.commit()
                    return (
                        f"Query executed successfully. Rows affected: {cursor.rowcount}"
                    )

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        return f"Error executing query: {str(e)}"


def main(transport: Literal["stdio", "sse"] = "stdio"):
    """Main entry point to run the MCP server."""
    logger.info(f"Starting OceanBase MCP server with {transport} mode...")
    app.run(transport=transport)


if __name__ == "__main__":
    app.run()
