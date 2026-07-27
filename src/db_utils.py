import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "placement_tracker.db"

def get_connection(db_path=None):
    """Returns a sqlite3 connection. Pass db_path=':memory:' for tests."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
