import pandas as pd
from src.crud import (
    get_student_by_roll, add_student,
    get_company_by_name, add_company,
    get_all_drives, add_drive,
    get_applications_by_student, add_application, update_application_status,
)


def clean_students_df(df):
    """Standardize a raw students CSV: trim whitespace, fix casing, coerce types, drop dupes."""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    for col in ["roll_number", "name", "branch", "email", "phone"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["roll_number"] = df["roll_number"].str.upper()
    df["branch"] = df["branch"].str.upper()
    df["cgpa"] = pd.to_numeric(df["cgpa"], errors="coerce")
    df["batch_year"] = pd.to_numeric(df["batch_year"], errors="coerce").astype("Int64")
    if "active_backlogs" in df.columns:
        df["active_backlogs"] = pd.to_numeric(df["active_backlogs"], errors="coerce").fillna(0).astype(int)
    else:
        df["active_backlogs"] = 0

    df = df.drop_duplicates(subset="roll_number", keep="first")
    df = df.dropna(subset=["roll_number", "name", "branch", "batch_year"])
    return df


def ingest_students_csv(conn, csv_path):
    """Reads a students CSV, cleans it, and inserts new students. Existing roll numbers are skipped."""
    df = pd.read_csv(csv_path)
    df = clean_students_df(df)

    inserted, skipped = 0, 0
    for _, row in df.iterrows():
        if get_student_by_roll(conn, row["roll_number"]):
            skipped += 1
            continue
        add_student(
            conn, row["roll_number"], row["name"], row["branch"], int(row["batch_year"]),
            cgpa=row.get("cgpa"), email=row.get("email"), phone=row.get("phone"),
            active_backlogs=int(row.get("active_backlogs", 0)),
        )
        inserted += 1

    return {"inserted": inserted, "skipped": skipped}


def clean_drive_applications_df(df):
    """Standardize a raw flat drive+application CSV."""
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    for col in ["company_name", "role_offered", "eligible_branches", "roll_number", "current_status"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["roll_number"] = df["roll_number"].str.upper()
    df["package_lpa"] = pd.to_numeric(df.get("package_lpa"), errors="coerce")
    df["final_package_lpa"] = pd.to_numeric(df.get("final_package_lpa"), errors="coerce")
    df["min_cgpa"] = pd.to_numeric(df.get("min_cgpa", 0), errors="coerce").fillna(0)
    df["drive_date"] = pd.to_datetime(df["drive_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["applied_date"] = pd.to_datetime(df.get("applied_date"), errors="coerce").dt.strftime("%Y-%m-%d")

    df = df.dropna(subset=["company_name", "drive_date", "roll_number"])
    return df


def ingest_drive_applications_csv(conn, csv_path):
    """
    Reads a flat company/drive/application CSV, normalizes it into the three
    relational tables, and links applications to existing students.
    Note: uses simple linear scans for get-or-create lookups, which is fine
    at TnP-cell scale (hundreds of rows) but would want indexing at larger scale.
    """
    df = pd.read_csv(csv_path)
    df = clean_drive_applications_df(df)

    company_cache, drive_cache = {}, {}
    stats = {
        "companies_created": 0, "drives_created": 0,
        "applications_created": 0, "applications_skipped": 0,
        "unknown_students_skipped": 0,
    }

    for _, row in df.iterrows():
        company_name = row["company_name"]
        if company_name not in company_cache:
            existing = get_company_by_name(conn, company_name)
            if existing:
                company_cache[company_name] = existing[0]
            else:
                cid = add_company(conn, company_name, sector=row.get("sector"))
                company_cache[company_name] = cid
                stats["companies_created"] += 1
        company_id = company_cache[company_name]

        drive_key = (company_id, row["drive_date"], row.get("role_offered"))
        if drive_key not in drive_cache:
            match = next(
                (d for d in get_all_drives(conn)
                 if d[1] == company_id and d[2] == row["drive_date"] and d[3] == row.get("role_offered")),
                None,
            )
            if match:
                drive_cache[drive_key] = match[0]
            else:
                did = add_drive(
                    conn, company_id, row["drive_date"], role_offered=row.get("role_offered"),
                    package_lpa=row.get("package_lpa"), eligible_branches=row.get("eligible_branches"),
                    min_cgpa=row.get("min_cgpa", 0),
                )
                drive_cache[drive_key] = did
                stats["drives_created"] += 1
        drive_id = drive_cache[drive_key]

        student = get_student_by_roll(conn, row["roll_number"])
        if not student:
            stats["unknown_students_skipped"] += 1
            continue
        student_id = student[0]

        already_applied = any(a[2] == drive_id for a in get_applications_by_student(conn, student_id))
        if already_applied:
            stats["applications_skipped"] += 1
            continue

        app_id = add_application(
            conn, student_id, drive_id,
            current_status=row.get("current_status", "Applied"),
            applied_date=row.get("applied_date"),
        )
        if row.get("current_status") == "Selected" and pd.notna(row.get("final_package_lpa")):
            update_application_status(conn, app_id, "Selected", final_package_lpa=row.get("final_package_lpa"))
        stats["applications_created"] += 1

    return stats