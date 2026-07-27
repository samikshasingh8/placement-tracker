import streamlit as st
import plotly.express as px
from src.db_utils import get_connection
from src.queries import get_placement_rate_by_branch, get_package_trends, get_drive_conversion_rates

st.set_page_config(page_title="Visualizations", layout="wide")
st.title("Placement Analytics")

conn = get_connection()

# ---------- Chart 1: Placement rate by branch ----------
st.subheader("Placement rate by branch")
rate_df = get_placement_rate_by_branch(conn)
if rate_df.empty:
    st.info("No student data yet.")
else:
    fig1 = px.bar(
        rate_df, x="branch", y="placement_rate_pct", text="placement_rate_pct",
        labels={"branch": "Branch", "placement_rate_pct": "Placement rate (%)"},
    )
    fig1.update_traces(texttemplate="%{text}%", textposition="outside")
    fig1.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig1, use_container_width=True)

# ---------- Chart 2: Package trend over time ----------
st.subheader("Average package trend over time")
trend_df = get_package_trends(conn)
if trend_df.empty:
    st.info("No selected offers with package data yet.")
else:
    fig2 = px.line(
        trend_df, x="month", y="avg_package_lpa", markers=True,
        labels={"month": "Month", "avg_package_lpa": "Avg package (LPA)"},
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Chart 3: Drive-wise conversion rate ----------
st.subheader("Drive-wise conversion rate")
conv_df = get_drive_conversion_rates(conn)
if conv_df.empty:
    st.info("No drives yet.")
else:
    conv_df = conv_df.sort_values("conversion_rate_pct", ascending=True)
    fig3 = px.bar(
        conv_df, x="conversion_rate_pct", y="drive_label", orientation="h",
        text="conversion_rate_pct",
        labels={"conversion_rate_pct": "Conversion rate (%)", "drive_label": "Drive"},
        hover_data=["total_applied", "total_selected"],
    )
    fig3.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

conn.close()