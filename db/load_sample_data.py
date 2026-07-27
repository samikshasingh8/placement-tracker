import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.db_utils import get_connection
from src.ingest import ingest_students_csv, ingest_drive_applications_csv

DATA_DIR = Path(__file__).parent.parent / "data"

if __name__ == "__main__":
    conn = get_connection()
    print(ingest_students_csv(conn, DATA_DIR / "sample_students.csv"))
    print(ingest_drive_applications_csv(conn, DATA_DIR / "sample_drives_applications.csv"))
    conn.close()