import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "placement_tracker.db"

def get_connection(db_path=None):
    """Returns a sqlite3 connection. Pass db_path=':memory:' for tests."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_database_ready():
    """
    If the students table doesn't exist yet (fresh or reset container),
    create the schema and reload sample data. Checking for the table itself
    (not just the file) avoids getting stuck if a previous init attempt
    failed partway through.
    """
    conn = get_connection()
    result = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='students'"
    ).fetchall()
    if result:
        conn.close()
        return

    from src.ingest import ingest_students_csv, ingest_drive_applications_csv

    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    ingest_students_csv(conn, DATA_DIR / "sample_students.csv")
    ingest_drive_applications_csv(conn, DATA_DIR / "sample_drives_applications.csv")
    conn.close()