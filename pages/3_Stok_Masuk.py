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

if st.session_state["role"] not in ["admin", "staff"]:
    st.error("Akses ditolak")
    st.stop()
    
st.title("➕ Stok Masuk")

df_produk = read_sheet("Daftar_Produk")

# ✅ checkbox stock opname
is_opname = st.checkbox("Stock Opname / Inisialisasi")

with st.form("form_masuk"):
    produk = st.selectbox(
        "Pilih Produk",
        df_produk["Nama Barang"]
    )

    qty = st.number_input("Jumlah", 1)
    lokasi = st.selectbox(
        "Lokasi",
        ["Toko", "Gudang","Rumah"]
    )

    
    # supplier disable kalau opname
    supplier = st.text_input(
        "Supplier",
        disabled=is_opname
    )

    submit = st.form_submit_button("Simpan")

    if submit:
        row_produk = df_produk[df_produk["Nama Barang"] == produk].iloc[0]
        
        # logic keterangan
        keterangan = "Stock Opname / Inisialisasi" if is_opname else ""

        append_sheet("Stok_Masuk", [
            datetime.now().strftime("%Y-%m-%d"),
            row_produk["Kode Barang"],
            produk,
            qty,
            lokasi,
            supplier if not is_opname else "",
            keterangan
        ])
        st.success("Stok masuk dicatat")
        st.rerun()