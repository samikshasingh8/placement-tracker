import pandas as pd


def get_applications_full(conn):
    """
    One row per application, joined with student and drive/company info —
    this is the main table the dashboard filters and displays.
    """
    query = """
        SELECT
            a.application_id,
            s.roll_number,
            s.name AS student_name,
            s.branch,
            s.cgpa,
            c.company_name,
            d.drive_id,
            d.role_offered,
            d.drive_date,
            d.package_lpa AS advertised_package_lpa,
            d.drive_status,
            a.current_status,
            a.applied_date,
            a.final_package_lpa
        FROM applications a
        JOIN students s ON a.student_id = s.student_id
        JOIN drives d ON a.drive_id = d.drive_id
        JOIN companies c ON d.company_id = c.company_id
    """
    return pd.read_sql_query(query, conn)


def get_branches(conn):
    return sorted(pd.read_sql_query("SELECT DISTINCT branch FROM students", conn)["branch"].tolist())


def get_company_names(conn):
    return sorted(pd.read_sql_query("SELECT DISTINCT company_name FROM companies", conn)["company_name"].tolist())


def get_drive_statuses(conn):
    return sorted(pd.read_sql_query("SELECT DISTINCT drive_status FROM drives", conn)["drive_status"].tolist())