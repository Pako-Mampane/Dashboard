import streamlit as st  # type: ignore


def apply_styles():
    st.markdown(
        """
        <style>
            body {
                overflow: hidden;
                margin-bottom: 0px;
            }
            .block-container {
                padding-top: 0 !important;
            }
            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }
            header { visibility: hidden; }
            section[data-testid="stSidebar"] {
                width: 100px;
            }
            div[id="header"] {}
            div[id="title"] {
                font-size: 40px;
            }
            div[id="Sidebar"] {
                font-size: 20px;
            }
            div[data-baseweb="select"] {
                height: 30px;
            }
            div[data-baseweb="select"] div {
                min-height: 30px !important;
                line-height: 30px !important;
                font-size: 0.8rem;
                margin: 0px;
            }
            div[data-testid="stMainBlockContainer"] {
                padding-bottom: 0 !important;
            }
            div[data-testid="data-grid-canvas"] {
                border: 4px black;
            }
            svg {
                border-radius: 0.5rem;
                box-shadow: rgba(100, 100, 111, 0.2) 0px 7px 29px 0px;
            }
            div[role='radiogroup'] {
                display: flex;
                flex-direction: row;
            }
            .login-container {
                background-color: #f9f9f9;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
                width: 100%;
                max-width: 400px;
                margin: auto;
                margin-top: 3rem;
            }
            .login-container h2 {
                text-align: center;
                color: #333333;
                margin-bottom: 1.5rem;
            }
            .stTextInput > div > input, .stPasswordInput > div > input {
                padding: 0.5rem;
                border-radius: 6px;
                border: 1px solid #cccccc;
            }
            .stButton > button {
                background-color: black;
                color: white;
                padding: 0.6rem 1.2rem;
                border-radius: 6px;
                font-weight: 600;
                transition: background-color 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #3e638c;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
