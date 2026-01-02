import streamlit as st

def init_session():
    defaults = {
        "login": False,
        "user": None,
        "role": None
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
