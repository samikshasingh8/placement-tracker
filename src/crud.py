from datetime import date

#------------Students---------------

def add_student(conn, roll_number, name, branch, batch_year, cgpa=None, email=None, phone=None, active_backlogs=0):
    cursor = conn.execute(
        """INSERT INTO students (roll_number, name, branch, batch_year, cgpa, email, phone, active_backlogs)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (roll_number, name, branch, batch_year, cgpa, email, phone, active_backlogs)
    )
    conn.commit()
    return cursor.lastrowid


def get_all_students(conn):
    return conn.execute("SELECT * FROM students").fetchall()


def get_student_by_roll(conn, roll_number):
    return conn.execute(
        "SELECT * FROM students WHERE roll_number = ?", (roll_number,)
    ).fetchone()


def update_student(conn, student_id, **fields):
    if not fields:
        return
    set_clause = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [student_id]
    conn.execute(f"UPDATE students SET {set_clause} WHERE student_id = ?", values)
    conn.commit()


def delete_student(conn, student_id):
    conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    

# ---------- Companies ----------

def add_company(conn, company_name, sector=None, website=None):
    cursor = conn.execute(
        "INSERT INTO companies (company_name, sector, website) VALUES (?, ?, ?)",
        (company_name, sector, website)
    )
    conn.commit()
    return cursor.lastrowid


def get_all_companies(conn):
    return conn.execute("SELECT * FROM companies").fetchall()


def get_company_by_name(conn, company_name):
    return conn.execute(
        "SELECT * FROM companies WHERE company_name = ? COLLATE NOCASE", (company_name,)
    ).fetchone()


def update_company(conn, company_id, **fields):
    if not fields:
        return
    set_clause = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [company_id]
    conn.execute(f"UPDATE companies SET {set_clause} WHERE company_id = ?", values)
    conn.commit()


def delete_company(conn, company_id):
    conn.execute("DELETE FROM companies WHERE company_id = ?", (company_id,))
    conn.commit()


# ---------- Drives ----------

def add_drive(conn, company_id, drive_date, role_offered=None, package_lpa=None,
              eligible_branches=None, min_cgpa=0, drive_status="Upcoming"):
    cursor = conn.execute(
        """INSERT INTO drives (company_id, drive_date, role_offered, package_lpa,
                                eligible_branches, min_cgpa, drive_status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (company_id, drive_date, role_offered, package_lpa, eligible_branches, min_cgpa, drive_status)
    )
    conn.commit()
    return cursor.lastrowid


def get_all_drives(conn):
    return conn.execute("SELECT * FROM drives").fetchall()


def get_drive_by_id(conn, drive_id):
    return conn.execute("SELECT * FROM drives WHERE drive_id = ?", (drive_id,)).fetchone()


def get_drives_by_status(conn, status):
    return conn.execute(
        "SELECT * FROM drives WHERE drive_status = ?", (status,)
    ).fetchall()


def update_drive(conn, drive_id, **fields):
    if not fields:
        return
    set_clause = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [drive_id]
    conn.execute(f"UPDATE drives SET {set_clause} WHERE drive_id = ?", values)
    conn.commit()


def delete_drive(conn, drive_id):
    conn.execute("DELETE FROM drives WHERE drive_id = ?", (drive_id,))
    conn.commit()


# ---------- Applications ----------


def add_application(conn, student_id, drive_id, current_status="Applied", applied_date=None):
    applied_date = applied_date or date.today().isoformat()
    cursor = conn.execute(
        """INSERT INTO applications (student_id, drive_id, current_status, applied_date)
           VALUES (?, ?, ?, ?)""",
        (student_id, drive_id, current_status, applied_date)
    )
    conn.commit()
    return cursor.lastrowid


def get_applications_by_drive(conn, drive_id):
    return conn.execute(
        "SELECT * FROM applications WHERE drive_id = ?", (drive_id,)
    ).fetchall()


def get_applications_by_student(conn, student_id):
    return conn.execute(
        "SELECT * FROM applications WHERE student_id = ?", (student_id,)
    ).fetchall()


def update_application_status(conn, application_id, new_status, final_package_lpa=None):
    conn.execute(
        """UPDATE applications
           SET current_status = ?, final_package_lpa = ?, last_updated = CURRENT_TIMESTAMP
           WHERE application_id = ?""",
        (new_status, final_package_lpa, application_id)
    )
    conn.commit()


def delete_application(conn, application_id):
    conn.execute("DELETE FROM applications WHERE application_id = ?", (application_id,))
    conn.commit()