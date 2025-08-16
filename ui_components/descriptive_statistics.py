import streamlit as st
import plotly.express as px


def render_descriptive_statistics(filtered_df):
    st.header("Summary Statistics")
    request_counts = filtered_df["Request Type"].value_counts().reset_index()
    request_counts.columns = ["Request Type", "Count"]
    total_revenue = filtered_df["Revenue"].sum()
    revenue_non_zero_count = filtered_df[filtered_df["Revenue"] > 0]["Revenue"].count()
    avg_revenue = (
        total_revenue / revenue_non_zero_count if revenue_non_zero_count > 0 else 0
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean Revenue", f"P {avg_revenue:.2f}")
    col2.metric(
        "Median Revenue",
        f"P {filtered_df['Revenue'][filtered_df['Revenue'] > 0].median():.2f}",
    )
    col3.metric(
        "Std Dev", f"P {filtered_df['Revenue'][filtered_df['Revenue'] > 0].std():.2f}"
    )
    fig_requests = px.bar(
        request_counts,
        x="Request Type",
        y="Count",
        title="Distribution of Request Types",
        color="Request Type",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    st.plotly_chart(fig_requests, use_container_width=True)
