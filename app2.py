import streamlit as st  # type: ignore
from data_preparation.data_preprocessing import load_and_filter_data
from ui_components.render import render_dashboard
from ui_components.styles import apply_styles

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")
apply_styles()

print("Setting up auth")
USER_CREDENTIALS = {
    "manager": {"password": "manager123"},
    "member": {"password": "member123"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


def login_form():
    with st.container():
        st.subheader("🔐 Login")
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if (
                    username in USER_CREDENTIALS
                    and USER_CREDENTIALS[username]["password"] == password
                ):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username} 👋")
                else:
                    st.error("Invalid username or password")
        st.markdown("</div>", unsafe_allow_html=True)


print("Loading data")
df, filtered_df, filters = load_and_filter_data()

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns(3)
    with c2:
        login_form()
        st.stop()
else:
    print("Rendering dashboard")
    render_dashboard(filtered_df, filters, df)
