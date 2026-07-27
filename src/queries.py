import pandas as pd
import numpy as np

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


def get_placement_rate_by_branch(conn):
    """% of students per branch who've been Selected in at least one drive."""
    query = """
        SELECT
            s.branch,
            COUNT(DISTINCT s.student_id) AS total_students,
            COUNT(DISTINCT CASE WHEN a.current_status = 'Selected' THEN s.student_id END) AS placed_students
        FROM students s
        LEFT JOIN applications a ON s.student_id = a.student_id
        GROUP BY s.branch
    """
    df = pd.read_sql_query(query, conn)
    df["placement_rate_pct"] = (df["placed_students"] / df["total_students"] * 100).round(1)
    return df


def get_package_trends(conn):
    """Average final package (LPA) of Selected offers, grouped by month of drive date."""
    query = """
        SELECT d.drive_date, a.final_package_lpa
        FROM applications a
        JOIN drives d ON a.drive_id = d.drive_id
        WHERE a.current_status = 'Selected' AND a.final_package_lpa IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return df
    df["drive_date"] = pd.to_datetime(df["drive_date"])
    df["month"] = df["drive_date"].dt.to_period("M").astype(str)
    trend = df.groupby("month")["final_package_lpa"].mean().round(2).reset_index()
    return trend.rename(columns={"final_package_lpa": "avg_package_lpa"})


def get_drive_conversion_rates(conn):
    """Applied vs Selected count per drive, with conversion rate."""
    query = """
        SELECT
            d.drive_id, c.company_name, d.role_offered,
            COUNT(a.application_id) AS total_applied,
            SUM(CASE WHEN a.current_status = 'Selected' THEN 1 ELSE 0 END) AS total_selected
        FROM drives d
        JOIN companies c ON d.company_id = c.company_id
        LEFT JOIN applications a ON d.drive_id = a.drive_id
        GROUP BY d.drive_id
    """
    df = pd.read_sql_query(query, conn)
    df["conversion_rate_pct"] = (
        df["total_selected"] / df["total_applied"].replace(0, np.nan) * 100
    ).fillna(0).round(1)
    df["drive_label"] = df["company_name"] + " – " + df["role_offered"].fillna("—")
    return df