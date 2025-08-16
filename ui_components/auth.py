import streamlit as st  # type: ignore

USER_CREDENTIALS = {
    "manager": {"password": "manager123"},
    "member": {"password": "member123"},
}


def setup_authentication():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        c1, c2, c3 = st.columns(3)
        with c2:
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
                            return True
                        else:
                            st.error("Invalid username or password")
                            return False
        return False
    return True
