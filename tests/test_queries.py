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
    
from src.crud import add_drive, get_applications_by_student
from src.queries import get_placement_rate_by_branch, get_package_trends, get_drive_conversion_rates


def test_placement_rate_by_branch(conn):
    add_student(conn, "22CSE001", "Placed Student", "CSE", 2027, cgpa=8.0)
    add_student(conn, "22CSE002", "Not Placed Student", "CSE", 2027, cgpa=7.0)
    company_id = add_company(conn, "RateTestCo")
    drive_id = add_drive(conn, company_id, "2026-08-01", role_offered="SDE")
    from src.crud import add_application
    app_id = add_application(conn, 1, drive_id)  # student_id 1 = first student inserted
    update_application_status(conn, app_id, "Selected", final_package_lpa=10)

    rates = get_placement_rate_by_branch(conn)
    row = rates[rates["branch"] == "CSE"].iloc[0]
    assert row["total_students"] == 2
    assert row["placed_students"] == 1
    assert row["placement_rate_pct"] == 50.0


def test_package_trends_groups_by_month(conn):
    company_id = add_company(conn, "TrendCo")
    student_id = add_student(conn, "22CSE010", "Trend Student", "CSE", 2027, cgpa=8.0)
    drive_id = add_drive(conn, company_id, "2026-08-15", role_offered="SDE")
    from src.crud import add_application
    app_id = add_application(conn, student_id, drive_id)
    update_application_status(conn, app_id, "Selected", final_package_lpa=20)

    trends = get_package_trends(conn)
    assert len(trends) == 1
    assert trends.iloc[0]["month"] == "2026-08"
    assert trends.iloc[0]["avg_package_lpa"] == 20.0


def test_drive_conversion_rate(conn):
    company_id = add_company(conn, "ConvCo")
    drive_id = add_drive(conn, company_id, "2026-08-01", role_offered="SDE")
    from src.crud import add_application
    s1 = add_student(conn, "22CSE020", "A", "CSE", 2027, cgpa=8.0)
    s2 = add_student(conn, "22CSE021", "B", "CSE", 2027, cgpa=8.0)
    app1 = add_application(conn, s1, drive_id)
    add_application(conn, s2, drive_id)
    update_application_status(conn, app1, "Selected", final_package_lpa=10)

    conv = get_drive_conversion_rates(conn)
    row = conv[conv["drive_id"] == drive_id].iloc[0]
    assert row["total_applied"] == 2
    assert row["total_selected"] == 1
    assert row["conversion_rate_pct"] == 50.0
    
def test_drive_conversion_rate_handles_zero_applications(conn):
    company_id = add_company(conn, "NoApplicantsCo")
    drive_id = add_drive(conn, company_id, "2026-08-01", role_offered="SDE")
    # deliberately no applications added

    conv = get_drive_conversion_rates(conn)
    row = conv[conv["drive_id"] == drive_id].iloc[0]
    assert row["total_applied"] == 0
    assert row["conversion_rate_pct"] == 0.0