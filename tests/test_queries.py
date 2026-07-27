from src.crud import add_student, add_company, add_drive, add_application
from src.queries import get_applications_full, get_branches, get_company_names, get_drive_statuses


def _seed(conn):
    student_id = add_student(conn, "22CSAI099", "Test Student", "CSE-AI", 2027, cgpa=8.0)
    company_id = add_company(conn, "TestCo", sector="IT")
    drive_id = add_drive(conn, company_id, "2026-08-01", role_offered="SDE", package_lpa=10)
    add_application(conn, student_id, drive_id, current_status="Applied")
    return student_id, company_id, drive_id


def test_get_applications_full_joins_correctly(conn):
    _seed(conn)
    df = get_applications_full(conn)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["student_name"] == "Test Student"
    assert row["company_name"] == "TestCo"
    assert row["current_status"] == "Applied"


def test_get_branches_and_companies_and_statuses(conn):
    _seed(conn)
    assert get_branches(conn) == ["CSE-AI"]
    assert get_company_names(conn) == ["TestCo"]
    assert get_drive_statuses(conn) == ["Upcoming"]