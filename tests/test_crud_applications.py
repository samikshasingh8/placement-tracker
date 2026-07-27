import pytest
from src.crud import (
    add_student, add_company, add_drive, add_application,
    get_applications_by_drive, get_applications_by_student, update_application_status, delete_application
)


def _make_student_and_drive(conn):
    student_id = add_student(conn, "22CSAI010", "Test Student", "CSE-AI", 2027, cgpa=8.0)
    company_id = add_company(conn, "TestCo")
    drive_id = add_drive(conn, company_id, "2026-08-01", role_offered="SDE")
    return student_id, drive_id


def test_add_application(conn):
    student_id, drive_id = _make_student_and_drive(conn)
    app_id = add_application(conn, student_id, drive_id)
    assert app_id is not None
    assert len(get_applications_by_drive(conn, drive_id)) == 1


def test_get_applications_by_student(conn):
    student_id, drive_id = _make_student_and_drive(conn)
    add_application(conn, student_id, drive_id)
    apps = get_applications_by_student(conn, student_id)
    assert len(apps) == 1
    assert apps[0][3] == "Applied"  # current_status column, default value


def test_update_application_status_to_selected(conn):
    student_id, drive_id = _make_student_and_drive(conn)
    app_id = add_application(conn, student_id, drive_id)
    update_application_status(conn, app_id, "Selected", final_package_lpa=12.5)
    apps = get_applications_by_student(conn, student_id)
    assert apps[0][3] == "Selected"
    assert apps[0][5] == 12.5  # final_package_lpa column


def test_delete_application(conn):
    student_id, drive_id = _make_student_and_drive(conn)
    app_id = add_application(conn, student_id, drive_id)
    delete_application(conn, app_id)
    assert get_applications_by_student(conn, student_id) == []


def test_duplicate_application_rejected(conn):
    import sqlite3
    student_id, drive_id = _make_student_and_drive(conn)
    add_application(conn, student_id, drive_id)
    with pytest.raises(sqlite3.IntegrityError):
        add_application(conn, student_id, drive_id)  # same student+drive twice