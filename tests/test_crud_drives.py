import pytest
from src.crud import add_company, add_drive, get_all_drives, get_drive_by_id, get_drives_by_status, update_drive, delete_drive


def test_add_drive(conn):
    company_id = add_company(conn, "Google")
    drive_id = add_drive(conn, company_id, "2026-08-15", role_offered="SDE-1",
                          package_lpa=28, eligible_branches="CSE,CSE-AI", min_cgpa=7.5)
    assert drive_id is not None
    assert len(get_all_drives(conn)) == 1


def test_get_drive_by_id(conn):
    company_id = add_company(conn, "Microsoft")
    drive_id = add_drive(conn, company_id, "2026-09-01", role_offered="SDE")
    drive = get_drive_by_id(conn, drive_id)
    assert drive[3] == "SDE"  # role_offered column


def test_get_drives_by_status_default_upcoming(conn):
    company_id = add_company(conn, "Adobe")
    add_drive(conn, company_id, "2026-08-20")
    upcoming = get_drives_by_status(conn, "Upcoming")
    assert len(upcoming) == 1


def test_update_drive_status(conn):
    company_id = add_company(conn, "Flipkart")
    drive_id = add_drive(conn, company_id, "2026-08-10")
    update_drive(conn, drive_id, drive_status="Completed")
    drive = get_drive_by_id(conn, drive_id)
    assert drive[7] == "Completed"  # drive_status column


def test_delete_drive(conn):
    company_id = add_company(conn, "Zoho")
    drive_id = add_drive(conn, company_id, "2026-08-05")
    delete_drive(conn, drive_id)
    assert get_drive_by_id(conn, drive_id) is None


def test_drive_requires_valid_company(conn):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        add_drive(conn, 999, "2026-08-15")  # company_id 999 doesn't exist
        
def test_update_drive_with_no_fields_is_a_no_op(conn):
    company_id = add_company(conn, "NoChangeDriveCo")
    drive_id = add_drive(conn, company_id, "2026-08-10", drive_status="Upcoming")
    update_drive(conn, drive_id)  # deliberately no keyword args
    drive = get_drive_by_id(conn, drive_id)
    assert drive[7] == "Upcoming"