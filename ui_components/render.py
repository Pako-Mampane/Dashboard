import streamlit as st  # type: ignore
from .sales_overview import render_sales_overview
from .sales_performance import render_sales_performance
from .traffic_analytics import render_traffic_analytics
from .descriptive_statistics import render_descriptive_statistics
from .raw_dataset import render_raw_dataset


def render_dashboard(filtered_df, filters, df):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "💰 Sales Overview",
            "🏆 Sales Performance",
            "🌐 Traffic Analytics",
            "📊 Descriptive Statistics",
            "Raw Dataset",
        ]
    )

    with tab1:
        render_sales_overview(filtered_df, filters)

    with tab2:
        render_sales_performance(filtered_df, df)

    with tab3:
        render_traffic_analytics(filtered_df)

    with tab4:
        render_descriptive_statistics(filtered_df)

    with tab5:
        render_raw_dataset(filtered_df)
