-- students: master list of eligible students
CREATE TABLE students (
    student_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_number     TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    branch          TEXT NOT NULL,
    batch_year      INTEGER NOT NULL,
    cgpa            REAL,
    email           TEXT,
    phone           TEXT,
    active_backlogs INTEGER DEFAULT 0
);

-- companies: one row per recruiter, reused across years/drives
CREATE TABLE companies (
    company_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name    TEXT NOT NULL UNIQUE,
    sector          TEXT,
    website         TEXT
);

-- drives: one row per hiring round/visit a company runs
CREATE TABLE drives (
    drive_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id        INTEGER NOT NULL,
    drive_date        DATE NOT NULL,
    role_offered      TEXT,
    package_lpa       REAL,
    eligible_branches TEXT,     -- comma-separated, e.g. "CSE,CSE-AI,IT"
    min_cgpa          REAL DEFAULT 0,
    drive_status      TEXT CHECK(drive_status IN
                       ('Upcoming','Ongoing','Completed','Cancelled')) DEFAULT 'Upcoming',
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- applications: junction table — one row per (student, drive) pair
CREATE TABLE applications (
    application_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id         INTEGER NOT NULL,
    drive_id           INTEGER NOT NULL,
    current_status     TEXT CHECK(current_status IN
                        ('Applied','Shortlisted','Interview Scheduled','Selected','Rejected','Withdrawn'))
                        DEFAULT 'Applied',
    applied_date       DATE DEFAULT CURRENT_DATE,
    final_package_lpa  REAL,    -- filled only once current_status = 'Selected'
    last_updated       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (drive_id) REFERENCES drives(drive_id),
    UNIQUE (student_id, drive_id)
);