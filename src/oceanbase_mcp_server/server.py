import asyncio
import logging
import os

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from mysql.connector import connect, Error
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("oceanbase_mcp_server")

load_dotenv()


def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("OB_HOST", "localhost"),
        "port": int(os.getenv("OB_PORT", "2881")),
        "user": os.getenv("OB_USER"),
        "password": os.getenv("OB_PASSWORD"),
        "database": os.getenv("OB_DATABASE"),
    }

    if not all([config["user"], config["password"], config["database"]]):
        logger.error(
            "Missing required database configuration. Please check environment variables:"
        )
        logger.error("OB_USER, OB_PASSWORD, and OB_DATABASE are required")
        raise ValueError("Missing required database configuration")

    return config


# Initialize server
app = Server("oceanbase_mcp_server")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List OceanBase tables as resources."""
    config = get_db_config()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")

                resources = []
                for table in tables:
                    resources.append(
                        Resource(
                            uri=f"oceanbase://{table[0]}/data",
                            name=f"Table: {table[0]}",
                            mimeType="text/plain",
                            description=f"Data in table: {table[0]}",
                        )
                    )
                return resources
    except Error as e:
        logger.error(f"Failed to list resources: {str(e)}")
        return []


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read table contents."""
    config = get_db_config()
    uri_str = str(uri)
    logger.info(f"Reading resource: {uri_str}")

    if not uri_str.startswith("oceanbase://"):
        raise ValueError(f"Invalid URI scheme: {uri_str}")

    parts = uri_str[8:].split("/")
    table = parts[0]

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)

    except Error as e:
        logger.error(f"Database error reading resource {uri}: {str(e)}")
        raise RuntimeError(f"Database error: {str(e)}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available OceanBase tools."""
    logger.info("Listing tools...")
    return [
        Tool(
            name="execute_sql",
            description="Execute a SQL query on the OceanBase server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute",
                    }
                },
                "required": ["query"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute SQL commands."""
    config = get_db_config()
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    if name != "execute_sql":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query")
    if not query:
        raise ValueError("Query is required")

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Special handling for SHOW TABLES
                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = ["Tables_in_" + config["database"]]  # Header
                    result.extend([table[0] for table in tables])
                    return [TextContent(type="text", text="\n".join(result))]

                elif query.strip().upper().startswith("SHOW COLUMNS"):
                    resp_header = "Columns info of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return [
                        TextContent(
                            type="text",
                            text=resp_header
                            + ("\n".join([",".join(columns)] + result)),
                        )
                    ]

                elif query.strip().upper().startswith("DESCRIBE"):
                    resp_header = "Description of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return [
                        TextContent(
                            type="text",
                            text=resp_header
                            + ("\n".join([",".join(columns)] + result)),
                        )
                    ]

                # Regular SELECT queries
                elif query.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return [
                        TextContent(
                            type="text", text="\n".join([",".join(columns)] + result)
                        )
                    ]

                # Non-SELECT queries
                else:
                    conn.commit()
                    return [
                        TextContent(
                            type="text",
                            text=f"Query executed successfully. Rows affected: {cursor.rowcount}",
                        )
                    ]

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        return [TextContent(type="text", text=f"Error executing query: {str(e)}")]


async def main():
    """Main entry point to run the MCP server."""
    logger.info("Starting OceanBase MCP server...")
    config = get_db_config()
    logger.info(
        f"Database config: {config['host']}/{config['database']} as {config['user']}"
    )

    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(main())
