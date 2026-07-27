from src.crud import add_student, add_company, add_drive, add_application
from src.queries import get_applications_full, get_branches, get_company_names, get_drive_statuses

from src.crud import update_application_status
from src.queries import get_student_roster


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
    



def test_roster_includes_students_with_zero_applications(conn):
    add_student(conn, "22CSAI077", "No Applications Yet", "CSE-AI", 2027, cgpa=7.0)
    roster = get_student_roster(conn)
    row = roster[roster["roll_number"] == "22CSAI077"].iloc[0]
    assert row["total_applications"] == 0
    assert row["placement_status"] == "Not placed"


def test_roster_shows_placed_student_with_best_package(conn):
    student_id, company_id, drive_id = _seed(conn)
    app_id = None
    from src.crud import get_applications_by_student
    app_id = get_applications_by_student(conn, student_id)[0][0]
    update_application_status(conn, app_id, "Selected", final_package_lpa=15.5)

    roster = get_student_roster(conn)
    row = roster[roster["roll_number"] == "22CSAI099"].iloc[0]
    assert row["placement_status"] == "Placed"
    assert row["best_package_lpa"] == 15.5