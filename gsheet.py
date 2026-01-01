import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "service_account.json", scope
    )
    client = gspread.authorize(creds)

    sheet = client.open("DaftarProductTokoPuji")
    return sheet


def read_sheet(sheet_name):
    sheet = connect_sheet().worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)


def append_sheet(sheet_name, row):
    sheet = connect_sheet().worksheet(sheet_name)
    sheet.append_row(row)
