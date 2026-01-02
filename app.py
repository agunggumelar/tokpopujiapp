import streamlit as st
import pandas as pd
from datetime import datetime
from gsheet import read_sheet, append_sheet

st.set_page_config(page_title="TokoPuji App", layout="wide")

menu = st.sidebar.selectbox(
    "Menu",
    ["Daftar_Produk", "Stok_Masuk", "Stok_Keluar"]
)

# ================= PRODUK =================
if menu == "Daftar_Produk":
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
        with st.form("form_produk"):
            nama = st.text_input("Nama Barang")
            kategori = st.text_input("Kategori")
            harga_jual = st.number_input("Harga Jual", 0)
            harga_beli = st.number_input("Harga Beli", 0)
            harga_jual_kembali = st.number_input("Harga utk Jual Kembali", 0)
            satuan = st.text_input("Satuan")
            keterangan = st.text_input("Keterangan")
            supplier = st.text_input("Supplier")

            submit = st.form_submit_button("Simpan")

            if submit:
                append_sheet("Daftar_Produk", [
                    "","",nama, kategori, harga_jual, harga_beli, harga_jual_kembali, satuan, keterangan, supplier, ""
                ])
                st.success("Produk berhasil ditambahkan")
                st.rerun()

# ================= STOK MASUK =================
elif menu == "Stok_Masuk":
    st.title("➕ Stok Masuk")

    df_produk = read_sheet("Daftar_Produk")

    with st.form("form_masuk"):
        produk = st.selectbox(
            "Pilih Produk",
            df_produk["Nama Barang"]
        )

        qty = st.number_input("Jumlah", 1)
        lokasi = st.selectbox(
            "Lokasi",
            ["Toko", "Gudang"]
        )
        supplier = st.text_input("Supplier")

        submit = st.form_submit_button("Simpan")

        if submit:
            row_produk = df_produk[df_produk["Nama Barang"] == produk].iloc[0]

            append_sheet("Stok_Masuk", [
                datetime.now().strftime("%Y-%m-%d"),
                row_produk["Kode Barang"],
                produk,
                qty,
                lokasi,
                supplier
            ])
            st.success("Stok masuk dicatat")
            st.rerun()

# ================= STOK KELUAR =================
elif menu == "Stok_Keluar":
    st.title("➖ Stok Keluar")

    df_produk = read_sheet("Daftar_Produk")

    with st.form("form_keluar"):
        produk = st.selectbox(
            "Pilih Produk",
            df_produk["Nama Barang"]
        )

        qty = st.number_input("Jumlah", 1)
        lokasi = st.selectbox(
            "Lokasi",
            ["Toko", "Gudang"]
        )
        ket = st.text_input("Keterangan")

        submit = st.form_submit_button("Simpan")

        if submit:
            row_produk = df_produk[df_produk["Nama Barang"] == produk].iloc[0]

            append_sheet("Stok_Keluar", [
                datetime.now().strftime("%Y-%m-%d"),
                row_produk["Kode Barang"],
                produk,
                qty,
                lokasi,
                ket
            ])
            st.success("Stok keluar dicatat")
            st.rerun()
