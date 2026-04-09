import sqlite3
import os
from config import DATABASE_PATH

def get_db_connection():
    """Returns a database connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database using the schema defined in models."""
    from database.models import create_tables
    conn = get_db_connection()
    create_tables(conn)
    conn.close()
