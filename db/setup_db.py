import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "placement_tracker.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")

if __name__ == "__main__":
    create_database()