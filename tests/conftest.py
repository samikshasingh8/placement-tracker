import sqlite3
import pytest
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"


@pytest.fixture
def conn():
    """A fresh in-memory database, rebuilt from schema.sql, for every test."""
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    with open(SCHEMA_PATH) as f:
        connection.executescript(f.read())
    yield connection
    connection.close()