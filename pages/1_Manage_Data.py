import streamlit as st
import sqlite3
from src.db_utils import get_connection
from src.crud import add_student, add_company, add_drive, get_all_companies, update_application_status
from src.queries import get_applications_full

st.set_page_config(page_title="Manage Data", layout="wide")
st.title("Manage placement data")

conn = get_connection()

tab1, tab2, tab3 = st.tabs(["Add student", "Add company & drive", "Update application status"])

with tab1:
    st.subheader("Add a new student")
    with st.form("add_student_form", clear_on_submit=True):
        roll_number = st.text_input("Roll number")
        name = st.text_input("Name")
        branch = st.text_input("Branch (e.g. CSE-AI)")
        batch_year = st.number_input("Batch year", min_value=2020, max_value=2035, value=2027, step=1)
        cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=8.0, step=0.1)
        email = st.text_input("Email (optional)")
        phone = st.text_input("Phone (optional)")
        submitted = st.form_submit_button("Add student")

        if submitted:
            if not roll_number or not name or not branch:
                st.error("Roll number, name, and branch are required.")
            else:
                try:
                    add_student(
                        conn, roll_number.strip().upper(), name.strip(), branch.strip().upper(),
                        int(batch_year), cgpa=cgpa, email=email or None, phone=phone or None,
                    )
                    st.success(f"Added {name} ({roll_number}).")
                except sqlite3.IntegrityError:
                    st.error(f"A student with roll number {roll_number} already exists.")

with tab2:
    st.subheader("Add a company")
    with st.form("add_company_form", clear_on_submit=True):
        company_name = st.text_input("Company name")
        sector = st.text_input("Sector (optional)")
        website = st.text_input("Website (optional)")
        submitted_company = st.form_submit_button("Add company")

        if submitted_company:
            if not company_name:
                st.error("Company name is required.")
            else:
                try:
                    add_company(conn, company_name.strip(), sector=sector or None, website=website or None)
                    st.success(f"Added {company_name}.")
                except sqlite3.IntegrityError:
                    st.error(f"{company_name} already exists.")

    st.divider()
    st.subheader("Add a drive")
    companies = get_all_companies(conn)
    company_options = {c[1]: c[0] for c in companies}  # name -> id

    if not company_options:
        st.info("Add a company above first.")
    else:
        with st.form("add_drive_form", clear_on_submit=True):
            company_choice = st.selectbox("Company", options=list(company_options.keys()))
            drive_date = st.date_input("Drive date")
            role_offered = st.text_input("Role offered")
            package_lpa = st.number_input("Package (LPA)", min_value=0.0, value=10.0, step=0.5)
            eligible_branches = st.text_input("Eligible branches (comma-separated, e.g. CSE,CSE-AI)")
            min_cgpa = st.number_input("Minimum CGPA", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
            drive_status = st.selectbox("Status", options=["Upcoming", "Ongoing", "Completed", "Cancelled"])
            submitted_drive = st.form_submit_button("Add drive")

            if submitted_drive:
                add_drive(
                    conn, company_options[company_choice], str(drive_date), role_offered=role_offered or None,
                    package_lpa=package_lpa, eligible_branches=eligible_branches or None,
                    min_cgpa=min_cgpa, drive_status=drive_status,
                )
                st.success(f"Added drive for {company_choice} on {drive_date}.")

with tab3:
    st.subheader("Update an application's status")
    apps_df = get_applications_full(conn)

    if apps_df.empty:
        st.info("No applications yet.")
    else:
        apps_df["label"] = (
            apps_df["roll_number"] + " — " + apps_df["company_name"] + " (" +
            apps_df["role_offered"].fillna("—") + ") — currently " + apps_df["current_status"]
        )
        choice = st.selectbox("Select application", options=apps_df["label"])
        selected_row = apps_df[apps_df["label"] == choice].iloc[0]

        status_options = ["Applied", "Shortlisted", "Interview Scheduled", "Selected", "Rejected", "Withdrawn"]
        new_status = st.selectbox("New status", options=status_options, index=status_options.index(selected_row["current_status"]))

        final_package = None
        if new_status == "Selected":
            final_package = st.number_input(
                "Final package (LPA)", min_value=0.0,
                value=float(selected_row["advertised_package_lpa"] or 0), step=0.5,
            )

        if st.button("Update status"):
            update_application_status(conn, int(selected_row["application_id"]), new_status, final_package_lpa=final_package)
            st.success(f"Updated to {new_status}.")
            st.rerun()

conn.close()