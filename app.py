import streamlit as st
import pandas as pd
from datetime import datetime
from gsheet import read_sheet, append_sheet
from session import init_session

init_session()
    
st.set_page_config(page_title="TokoPuji App", layout="wide")

if st.session_state["login"]:
    st.sidebar.write(
        f"👤 {st.session_state['user']} ({st.session_state['role']})"
    )

if st.session_state["login"]:
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.switch_page("pages/1_Login.py")

def normalize_text(x):
    if pd.isna(x):
        return ""
    return (
        str(x)
        .lower()
        .strip()
        .replace(" ", "")
    )
    
st.title("📦 Data Produk")
df_produk = read_sheet("Daftar_Produk")

cols = [
    "Kode Barang",
    "Nama Barang",
    "Kategori",
    "Stock Gudang",
    "Stock Toko",
    "Stock Akhir",
    "Harga Jual",
    "Harga Beli",
    "Harga utk Jual Kembali",
    "Satuan",
    "Keterangan",
    "Supplier"
]

df_view = df_produk[cols].copy()

# pastikan stok numeric
stok_cols = ["Stock Gudang", "Stock Toko", "Stock Akhir"]
df_view[stok_cols] = df_view[stok_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

# kolom indikator stok rendah
df_view["⚠️ Stok Rendah"] = (
    (df_view["Stock Akhir"] < 5)
)

# 🔁 atur ulang urutan kolom (sisipkan setelah Stock Akhir)
new_order = [
    "Kode Barang",
    "Nama Barang",
    "Kategori",
    "Stock Gudang",
    "Stock Toko",
    "Stock Akhir",
    "⚠️ Stok Rendah",   # ← DI SINI
    "Harga Jual",
    "Harga Beli",
    "Harga utk Jual Kembali",
    "Satuan",
    "Keterangan",
    "Supplier"
]

df_view = df_view[new_order]

# sort stok bermasalah ke atas
df_view = df_view.sort_values("⚠️ Stok Rendah", ascending=False)
df_view["Kategori_norm"] = df_view["Kategori"].apply(normalize_text)

# mapping norm → display (ambil versi pertama yang ketemu)
kategori_map = (
    df_view
    .dropna(subset=["Kategori_norm"])
    .drop_duplicates("Kategori_norm")
    .set_index("Kategori_norm")["Kategori"]
    .to_dict()
)

kategori_options = ["Semua"] + list(kategori_map.values())

kategori_filter = st.selectbox(
    "Filter Kategori",
    kategori_options
)

if kategori_filter != "Semua":
    # cari key norm dari value display
    selected_norm = next(
        k for k, v in kategori_map.items()
        if v == kategori_filter
    )
    
    df_view = df_view[
        df_view["Kategori_norm"] == selected_norm
    ]
    
df_view["Kategori"] = (
    df_view["Kategori"]
    .str.strip()
    .str.title()
)
st.metric(
    label="📦 Total Produk",
    value=len(df_view)
)
st.dataframe(
    df_view,
    use_container_width=True
)