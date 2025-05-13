# tests/conftest.py
import os

import mysql.connector
import pytest
from mysql.connector import Error


@pytest.fixture(scope="session")
def oceanbase_connection():
    """Create a test database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("OB_HOST", "127.0.0.1"),
            port=os.getenv("OB_PORT", "2881"),
            user=os.getenv("OB_USER", "root"),
            password=os.getenv("OB_PASSWORD", "testpassword"),
            database=os.getenv("OB_DATABASE", "test_db"),
        )

        if connection.is_connected():
            # Create a test table
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    value INT
                )
            """)
            connection.commit()

            yield connection

            # Cleanup
            cursor.execute("DROP TABLE IF EXISTS test_table")
            connection.commit()
            cursor.close()
            connection.close()

    except Error as e:
        pytest.fail(f"Failed to connect to OceanBase: {e}")


@pytest.fixture(scope="session")
def oceanbase_cursor(oceanbase_connection):
    """Create a test cursor."""
    cursor = oceanbase_connection.cursor()
    yield cursor
    cursor.close()
