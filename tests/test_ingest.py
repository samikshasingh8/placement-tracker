from src.ingest import clean_students_df, ingest_students_csv, ingest_drive_applications_csv
import pandas as pd


def test_clean_students_df_dedupes_and_fixes_case():
    raw = pd.DataFrame([
        {"roll_number": "22csai001", "name": " Riya ", "branch": "cse-ai", "batch_year": 2027, "cgpa": 8.7},
        {"roll_number": "22CSAI001", "name": " Riya ", "branch": "cse-ai", "batch_year": 2027, "cgpa": 8.7},
    ])
    cleaned = clean_students_df(raw)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["branch"] == "CSE-AI"


def test_ingest_students_csv(conn, tmp_path):
    csv_path = tmp_path / "students.csv"
    csv_path.write_text(
        "roll_number,name,branch,batch_year,cgpa\n"
        "22csai001,Riya Sharma,cse-ai,2027,8.7\n"
        "22CSAI001,Riya Sharma,CSE-AI,2027,8.7\n"  # duplicate, different case
        "22it021,Dev Patel,it,2027,7.9\n"
    )
    result = ingest_students_csv(conn, csv_path)
    assert result["inserted"] == 2
    assert result["skipped"] == 0  # dedup happens before insert, in Pandas


def test_ingest_drive_applications_csv_creates_company_and_drive_once(conn, tmp_path):
    students_csv = tmp_path / "students.csv"
    students_csv.write_text(
        "roll_number,name,branch,batch_year,cgpa\n"
        "22CSAI001,Riya Sharma,CSE-AI,2027,8.7\n"
        "22CSE015,Kabir Singh,CSE,2027,7.5\n"
    )
    ingest_students_csv(conn, students_csv)

    drives_csv = tmp_path / "drives.csv"
    drives_csv.write_text(
        "company_name,sector,drive_date,role_offered,package_lpa,eligible_branches,min_cgpa,"
        "roll_number,current_status,applied_date,final_package_lpa\n"
        "Google,Product,2026-08-15,SDE-1,28,\"CSE,CSE-AI\",7.5,22CSAI001,Selected,2026-07-20,28\n"
        " tcs ,IT Services,2026-08-01,Ninja,3.6,\"CSE\",6.0,22CSE015,Applied,2026-07-18,\n"
        "TCS,IT Services,2026-08-01,Ninja,3.6,\"CSE\",6.0,22CSAI001,Rejected,2026-07-18,\n"
    )
    result = ingest_drive_applications_csv(conn, drives_csv)

    assert result["companies_created"] == 2       # Google + TCS (tcs/TCS merged)
    assert result["drives_created"] == 2           # Google's drive + TCS's drive
    assert result["applications_created"] == 3
    assert result["unknown_students_skipped"] == 0


def test_ingest_skips_unknown_student(conn, tmp_path):
    drives_csv = tmp_path / "drives.csv"
    drives_csv.write_text(
        "company_name,sector,drive_date,role_offered,package_lpa,eligible_branches,min_cgpa,"
        "roll_number,current_status,applied_date,final_package_lpa\n"
        "Amazon,Product,2026-08-20,SDE-1,32,\"CSE\",7.0,99UNKNOWN,Applied,2026-07-25,\n"
    )
    result = ingest_drive_applications_csv(conn, drives_csv)
    assert result["unknown_students_skipped"] == 1
    assert result["applications_created"] == 0