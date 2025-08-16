import streamlit as st


def render_raw_dataset(filtered_df):
    st.header("Data Set")
    st.dataframe(filtered_df.head(500))
