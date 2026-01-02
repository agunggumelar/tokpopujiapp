import streamlit as st
import pandas as pd
from datetime import datetime
from gsheet import read_sheet, append_sheet

if not st.session_state.get("login"):
    st.switch_page("pages/1_Login.py")
    
if st.session_state["login"]:
    st.sidebar.write(
        f"👤 {st.session_state['user']} ({st.session_state['role']})"
    )

if st.session_state["login"]:
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.switch_page("pages/1_Login.py")
    
st.title("📦 Histori Stok")

# === LOAD DATA ===
df_masuk = read_sheet("Stok_Masuk")
df_keluar = read_sheet("Stok_Keluar")

# === PASTIKAN FORMAT TANGGAL ===
df_masuk["Tanggal"] = pd.to_datetime(df_masuk["Tanggal"])
df_keluar["Tanggal"] = pd.to_datetime(df_keluar["Tanggal"])

# === FILTER GLOBAL ===
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Tanggal Mulai",
        value=df_masuk["Tanggal"].min().date()
    )

with col2:
    end_date = st.date_input(
        "Tanggal Akhir",
        value=df_masuk["Tanggal"].max().date()
    )

# dropdown nama barang (gabungan masuk + keluar)
all_produk = sorted(
    set(df_masuk["Nama Barang"].dropna())
    | set(df_keluar["Nama Barang"].dropna())
)

produk_filter = st.selectbox(
    "Filter Nama Barang",
    ["Semua"] + all_produk
)

# === APPLY FILTER FUNCTION ===
def apply_filter(df):
    df = df[
        (df["Tanggal"].dt.date >= start_date) &
        (df["Tanggal"].dt.date <= end_date)
    ]
    if produk_filter != "Semua":
        df = df[df["Nama Barang"] == produk_filter]
    return df

df_masuk_f = apply_filter(df_masuk)
df_keluar_f = apply_filter(df_keluar)

# === TABS ===
tab1, tab2 = st.tabs(["📥 Stok Masuk", "📤 Stok Keluar"])

with tab1:
    st.subheader("Histori Stok Masuk")

    st.dataframe(
        df_masuk_f[
            [
                "Tanggal",
                "Kode",
                "Nama Barang",
                "Jumlah",
                "Lokasi",
                "Supplier",
                "Keterangan"
            ]
        ].sort_values("Tanggal", ascending=False),
        use_container_width=True
    )

    st.caption(f"Total transaksi: {len(df_masuk_f)}")

with tab2:
    st.subheader("Histori Stok Keluar")

    st.dataframe(
        df_keluar_f[
            [
                "Tanggal",
                "Kode",
                "Nama Barang",
                "Jumlah",
                "Lokasi",
                "Keterangan Order"
            ]
        ].sort_values("Tanggal", ascending=False),
        use_container_width=True
    )

    st.caption(f"Total transaksi: {len(df_keluar_f)}")