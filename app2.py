import streamlit as st  # type: ignore
from data_preparation.data_preprocessing import load_and_filter_data
from ui_components.render import render_dashboard
from ui_components.styles import apply_styles

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")
apply_styles()

df, filtered_df, filters = load_and_filter_data()

print("Rendering dashboard")
render_dashboard(filtered_df, filters, df)
