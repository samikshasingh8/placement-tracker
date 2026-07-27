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

def get_student_roster(conn):
    """
    One row per student (including students with zero applications),
    with placement status derived from their applications.
    Uses LEFT JOIN so students aren't dropped when they have no applications yet.
    """
    query = """
        SELECT
            s.student_id,
            s.roll_number,
            s.name,
            s.branch,
            s.cgpa,
            COUNT(a.application_id) AS total_applications,
            SUM(CASE WHEN a.current_status = 'Selected' THEN 1 ELSE 0 END) AS times_selected,
            MAX(CASE WHEN a.current_status = 'Selected' THEN a.final_package_lpa END) AS best_package_lpa
        FROM students s
        LEFT JOIN applications a ON s.student_id = a.student_id
        GROUP BY s.student_id
    """
    df = pd.read_sql_query(query, conn)
    df["placement_status"] = df["times_selected"].apply(lambda x: "Placed" if x > 0 else "Not placed")
    return df