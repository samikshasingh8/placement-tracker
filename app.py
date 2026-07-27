import streamlit as st
from src.db_utils import get_connection
from src.queries import get_applications_full, get_branches, get_company_names, get_drive_statuses, get_student_roster

st.set_page_config(page_title="Placement Tracker", layout="wide")
st.title("Placement Tracker Dashboard")

conn = get_connection()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

branches = st.sidebar.multiselect("Branch", options=get_branches(conn))
companies = st.sidebar.multiselect("Company", options=get_company_names(conn))
statuses = st.sidebar.multiselect("Drive status", options=get_drive_statuses(conn))

# ---------- Load and filter data ----------
df = get_applications_full(conn)

filtered = df.copy()
if branches:
    filtered = filtered[filtered["branch"].isin(branches)]
if companies:
    filtered = filtered[filtered["company_name"].isin(companies)]
if statuses:
    filtered = filtered[filtered["drive_status"].isin(statuses)]

# ---------- Summary metrics ----------
col1, col2, col3 = st.columns(3)
col1.metric("Total applications", len(filtered))
col2.metric("Selected", (filtered["current_status"] == "Selected").sum())
col3.metric("Unique students", filtered["roll_number"].nunique())

# ---------- Main tables ----------
tab_apps, tab_roster = st.tabs(["Applications", "All students"])

with tab_apps:
    st.dataframe(filtered, use_container_width=True)

with tab_roster:
    roster = get_student_roster(conn)
    if branches:
        roster = roster[roster["branch"].isin(branches)]
    st.dataframe(roster, use_container_width=True)

conn.close()