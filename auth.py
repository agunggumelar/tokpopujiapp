import streamlit as st
from gsheet import read_sheet

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        df = read_sheet("Users")

        user = df[
            (df["username"] == username) &
            (df["password"] == password) &
            (df["aktif"] == 1)
        ]

        if user.empty:
            st.error("Username / password salah")
            return

        st.session_state["login"] = True
        st.session_state["user"] = username
        st.session_state["role"] = user.iloc[0]["role"]

        st.success("Login berhasil")
        st.switch_page("app.py")
