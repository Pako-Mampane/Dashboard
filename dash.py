# Create a basic Streamlit dashboard script for analyzing the synthetic server log
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv("synthetic_server_logs.csv", parse_dates=["timestamp"])
    df["date"] = df["timestamp"].dt.date
    return df


df = load_data()
st.title("AI Company Sales Performance Dashboard")
st.markdown(
    "This dashboard analyzes synthetic web server logs to assess sales and AI tool engagement."
)

# Sidebar filters
country_filter = st.sidebar.multiselect(
    "Select Country", options=df["country"].unique(), default=df["country"].unique()
)
job_type_filter = st.sidebar.multiselect(
    "Select Job Type", options=df["job_type"].unique(), default=df["job_type"].unique()
)

filtered_df = df[
    (df["country"].isin(country_filter)) & (df["job_type"].isin(job_type_filter))
]

# KPIs
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)
col1.metric("Total Requests", len(filtered_df))
col2.metric("Demo Requests", filtered_df["demo_request"].sum())
col3.metric("Promotional Events", filtered_df["event_type"].notna().sum())

# Job Requests by Country
st.subheader("Job Requests by Country")
country_counts = filtered_df["country"].value_counts()
st.bar_chart(country_counts)

# Job Type Popularity
st.subheader("AI Tool Usage Breakdown")
job_counts = filtered_df["job_type"].value_counts()
st.bar_chart(job_counts)

# Demo Requests Over Time
st.subheader("Demo Requests Over Time")
demo_time = filtered_df[filtered_df["demo_request"] == True].groupby("date").size()
st.line_chart(demo_time)

# Referrer Analysis
st.subheader("Top Referrer Sources")
referrer_counts = filtered_df["referrer"].value_counts()
st.bar_chart(referrer_counts)
