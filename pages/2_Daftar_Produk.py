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

def generate_kode_barang(df_produk, kategori):
    prefix = kategori.strip().upper()[:3]

    # ambil kode yg sudah ada dengan prefix sama
    existing = df_produk[
        df_produk["Kode Barang"].str.startswith(prefix, na=False)
    ]

    if existing.empty:
        return f"{prefix}001"

    # ambil nomor terbesar
    last_number = (
        existing["Kode Barang"]
        .str[-3:]
        .astype(int)
        .max()
    )

    return f"{prefix}{last_number + 1:03d}"

def normalize_text(x):
    return x.strip().lower()

st.set_page_config(page_title="TokoPuji App", layout="wide")

st.title("📦 Data Produk")
    # Tab untuk input berbeda
tab1, tab2 = st.tabs(["Data Table", "Form Produk"])
with tab1:
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

    st.dataframe(
        df_view,
        use_container_width=True,
        height=600
    )
with tab2:
    can_edit = st.session_state["role"] in ["admin"]

    if not can_edit:
        st.info("🔒 Hanya admin yang dapat menambahkan produk")
        
    df_produk = read_sheet("Daftar_Produk")

    kategori_raw = df_produk["Kategori"].dropna().astype(str)

    kategori_map = {
        normalize_text(k): k.strip().title()
        for k in kategori_raw
    }

    kategori_list = sorted(set(kategori_map.values()))
    

    with st.form("form_produk"):
        nama = st.text_input("Nama Barang")
        kategori = st.selectbox(
            "Kategori",
            kategori_list
        )
        harga_jual = st.number_input("Harga Jual", 0)
        harga_beli = st.number_input("Harga Beli", 0)
        harga_jual_kembali = st.number_input("Harga utk Jual Kembali", 0)
        satuan = st.text_input("Satuan")
        keterangan = st.text_input("Keterangan")
        supplier = st.text_input("Supplier")
        kategori_clean = normalize_text(kategori).title()
        submit = st.form_submit_button(
            "Simpan",
            disabled=not can_edit
        )

        if submit:
            kode_barang = generate_kode_barang(df_produk, kategori)
            
            append_sheet("Daftar_Produk", [
                "",
                kode_barang,
                nama, 
                kategori_clean, 
                harga_jual, 
                harga_beli, 
                harga_jual_kembali, 
                satuan, 
                keterangan, 
                supplier, 
                kode_barang,
                st.session_state["user"] 
            ])
            st.success("Produk berhasil ditambahkan")
            st.rerun()