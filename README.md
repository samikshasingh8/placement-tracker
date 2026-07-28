# Placement Tracker Dashboard

A tool built for my college's Training & Placement Cell to replace manual Excel-based
tracking of campus placement drives — which companies are visiting, which students
applied and to which drives, current application status, and package offered.
Built and used in my role as a TnP student coordinator.

**Live demo:** https://placement-tracker.streamlit.app/

## Features

- **CSV ingestion** — bulk-upload student rosters and drive/application data from
  Excel-exported CSVs, with Pandas-based cleaning (case/whitespace normalization,
  duplicate detection, type coercion) so messy real-world exports import cleanly
- **Full CRUD** against a normalized relational schema (students, companies, drives,
  applications), with data-entry forms in the dashboard itself — no more editing
  a shared Excel file by hand
- **Filterable dashboard** — filter by branch, company, and drive status
- **Visualizations** — placement rate by branch, average package trend over time,
  drive-wise conversion rate (applied → selected), built with Plotly for interactive
  charts
- **100% test coverage** on all core logic (CRUD, CSV ingestion, and query/aggregation
  layers) — 43 tests via pytest, see [Testing](#testing) below

## Tech stack

Python · SQLite · Pandas · Streamlit · Plotly · pytest / pytest-cov

## Screenshots



```markdown
![Dashboard with filters](screenshots/dashboard.png)
![Data entry form](screenshots/manage_data.png)
![Visualizations page](screenshots/visualizations.png)
```

## Database schema

Four tables: `students`, `companies`, `drives`, and `applications` (a junction table
linking students to the drives they've applied to, since it's a many-to-many
relationship). Full schema in [`db/schema.sql`](db/schema.sql).

## Project structure

```
placement-tracker/
├── app.py                      # Main dashboard page
├── pages/
│   ├── 1_Manage_Data.py         # Add/update students, companies, drives, applications
│   └── 2_Visualizations.py      # Placement rate, package trends, conversion rates
├── src/
│   ├── db_utils.py              # Database connection helper
│   ├── crud.py                  # Create/read/update/delete functions for all 4 tables
│   ├── ingest.py                # CSV cleaning (Pandas) + bulk ingestion logic
│   └── queries.py                # Read queries/joins feeding the dashboard and charts
├── db/
│   ├── schema.sql                # Table definitions
│   ├── setup_db.py               # Creates the database from schema.sql
│   ├── load_sample_data.py       # Populates the db from the sample CSVs below
│   └── verify.py                 # Quick sanity check that tables exist
├── data/
│   ├── sample_students.csv
│   └── sample_drives_applications.csv
├── tests/                        # pytest suite (43 tests, 100% coverage on src/)
└── requirements.txt
```

## Setup & installation

1. Clone the repo and enter it:
```bash
   git clone <your-repo-url>
   cd placement-tracker
```
2. Create and activate a virtual environment:
```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\Activate.ps1
   # Mac/Linux:
   source .venv/bin/activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Create the database and load sample data:
```bash
   python db/setup_db.py
   python db/load_sample_data.py
```
5. Run the app:
```bash
   streamlit run app.py
```

## Testing

```bash
pytest --cov --cov-report=term-missing
```

100% coverage on `src/` (database logic, CSV ingestion, and query layer) — 43 tests
covering the happy path plus edge cases like duplicate records, zero-application
drives, empty datasets, and re-uploading a CSV without creating duplicates.

UI code (`app.py`, `pages/`) is intentionally excluded from coverage measurement —
it's mostly thin Streamlit calls with no independent logic, and was verified through
manual testing during development instead.

## Design notes & future enhancements

- Currently uses SQLite for zero-config local development and easy deployment. For
  multi-coordinator concurrent use at scale, migrating to MySQL/Postgres would be
  the natural next step — the schema is written to be portable.
- `eligible_branches` on `drives` is stored as a comma-separated string rather than
  a fully normalized join table — a deliberate simplification given project scope.
- Package offered is tracked per-application (`final_package_lpa`), not per-drive,
  since actual offers can vary by role or negotiation even within the same drive.