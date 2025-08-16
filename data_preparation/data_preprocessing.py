import streamlit as st
import pandas as pd
import calendar


@st.cache_data
def load_data(file):
    data = pd.read_csv(file, on_bad_lines="skip")
    data["Timestamp"] = pd.to_datetime(data["Timestamp"])
    return data


def load_and_filter_data():
    with st.sidebar:
        st.logo("image.png")
        st.markdown(
            f"""
            <div style="padding-top:0;" id="header">
            <div id='title'>AI Solutions</div>
            <div id="greetings">Hello, {st.session_state.username}!</div>
            </div>""",
            unsafe_allow_html=True,
        )

    file = st.sidebar.file_uploader("Choose a dataset")
    if file is None:
        st.warning("Please upload a dataset to continue")
        st.stop()

    df = load_data(file)
    st.sidebar.header("Filters")

    min_date = df["Timestamp"].min()
    max_date = df["Timestamp"].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )

    if len(date_range) != 2:
        st.warning("Please select both a start and end date to filter the dashboard.")
        return None, None, None

    start_date, end_date = date_range
    filtered_df = df[
        (df["Timestamp"] >= pd.to_datetime(start_date))
        & (df["Timestamp"] <= pd.to_datetime(end_date))
    ]

    country_filter = st.sidebar.selectbox(
        "**Country**", options=["All"] + list(df["Country"].unique()), index=0
    )
    product_filter = st.sidebar.selectbox(
        "**Product Category**",
        options=["All"] + list(df["Product"].dropna().unique()),
        index=0,
    )
    unique_months = sorted(df["month"].dropna().unique())
    month_names = [calendar.month_name[m] for m in unique_months]
    month_name_to_num = {calendar.month_name[m]: m for m in unique_months}
    month_filter = st.sidebar.selectbox(
        "**Month**", options=["All"] + month_names, index=0
    )
    year_filter = st.sidebar.selectbox(
        "**Year**", options=["All"] + list(df["year"].unique()), index=0
    )

    if country_filter != "All":
        filtered_df = filtered_df[filtered_df["Country"] == country_filter]
    if product_filter != "All":
        filtered_df = filtered_df[
            filtered_df["Product"].notna() & (filtered_df["Product"] == product_filter)
        ]
    if month_filter != "All":
        selected_month_num = month_name_to_num[month_filter]
        filtered_df = filtered_df[filtered_df["month"] == selected_month_num]
    if year_filter != "All":
        filtered_df = filtered_df[filtered_df["year"] == year_filter]

    filters = {
        "product_sales": filtered_df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values(by="Revenue", ascending=False),
        "sales_by_country": filtered_df.groupby("Country")["Revenue"]
        .sum()
        .reset_index()
        .sort_values(by="Revenue", ascending=False),
        "product_sales_by_agent": filtered_df.groupby("Sales Agent")["Revenue"]
        .sum()
        .reset_index(),
        "conversion_by_referrer": filtered_df.groupby("Referrer").agg(
            {"Session ID": "nunique", "Product": lambda x: x.notnull().sum()}
        ),
        "monthly_sessions": filtered_df.groupby("month")["Session ID"].nunique(),
        "total_sales": filtered_df[
            filtered_df["Request Type"] == "Product Purchase"
        ].shape[0],
        "total_sales_revenue": filtered_df["Revenue"].sum(),
        "total_visitors": filtered_df["IP Address"].nunique(),
        "conversion_by_IP": filtered_df[filtered_df["Product"].notna()][
            "IP Address"
        ].nunique(),
        "month_filter": month_filter,
        "start_date": start_date,
        "end_date": end_date,
        "df": df,
    }
    filters["conversion_rate"] = (
        filters["conversion_by_IP"] / filters["total_visitors"]
    ) * 100

    return df, filtered_df, filters
