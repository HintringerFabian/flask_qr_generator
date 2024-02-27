import sqlite3
import threading
from contextlib import contextmanager

# Create a global lock
lock = threading.Lock()


@contextmanager
def get_cursor(connection: sqlite3.Connection):
    cursor: sqlite3.Cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()


def get_database_connection(name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(name)
    return conn


def init_db_if_not_exists(db_name: str):
    # Connect to the SQLite database (this will create the database file if it does not exist)

    with get_database_connection(db_name) as conn, get_cursor(conn) as cursor:

        # SQL statement to create a table if it does not exist
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS uuid_mappings (
                UUID TEXT,
                URL_DATA TEXT,
                COUNT INTEGER
            );
        """

        # Execute the SQL statement to create the table
        cursor.execute(create_table_sql)

        # Commit the changes and close the connection
        conn.commit()


def save_to_db(uuid, url_data, db_name):
    with get_database_connection(db_name) as conn, get_cursor(conn) as cursor:

        # SQL statement to insert a new row into the table
        insert_sql = """
            INSERT INTO uuid_mappings (UUID, URL_DATA, COUNT)
            VALUES (?, ?, ?);
        """

        # Execute the SQL statement to insert a new row
        cursor.execute(insert_sql, (uuid, url_data, 0))

        # Commit the changes and close the connection
        conn.commit()


def find_data_by_uuid(uuid, db_name) -> str | None:
    with get_database_connection(db_name) as conn, get_cursor(conn) as cursor:

        # SQL statement to select a row from the table by UUID
        select_sql = """
            SELECT URL_DATA
            FROM uuid_mappings
            WHERE UUID = ?;
        """

        # Execute the SQL statement to select a row by UUID
        cursor.execute(select_sql, (uuid,))

        # Fetch the result of the SQL query
        result = cursor.fetchone()

        # Check if the result is not None, and return the first element of the tuple
        return result[0] if result else None


def increase_count(uuid, db_name):
    with lock:
        # The code inside this block is now thread-safe and ensures that the SQL
        # operation is executed only once at a time across threads.
        with get_database_connection(db_name) as conn, get_cursor(conn) as cursor:
            update_sql = """
                UPDATE uuid_mappings
                SET COUNT = COUNT + 1
                WHERE UUID = ?;
            """

            cursor.execute(update_sql, (uuid,))
            conn.commit()
