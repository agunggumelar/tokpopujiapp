import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def connect_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPE
    )

    client = gspread.authorize(creds)
    return client.open(st.secrets["spreadsheet_name"])



def read_sheet(sheet_name):
    ws = connect_sheet().worksheet(sheet_name)
    return pd.DataFrame(ws.get_all_records())


def append_sheet(sheet_name, row):
    ws = connect_sheet().worksheet(sheet_name)
    ws.append_row(row, value_input_option="USER_ENTERED")
