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
    
st.title("➖ Stok Keluar")

df_produk = read_sheet("Daftar_Produk")

# 🔥 checkbox di LUAR form
kirim_ke_toko = st.checkbox("Dikirim ke Toko (dari Gudang)")

with st.form("form_keluar"):
    produk = st.selectbox(
        "Pilih Produk",
        df_produk["Nama Barang"]
    )

    qty = st.number_input(
        "Jumlah",
        min_value=1,
        step=1
    )

    lokasi = st.selectbox(
        "Lokasi",
        ["Gudang", "Toko"]
    )

    ket = st.text_input(
        "Keterangan",
        value="Dikirim ke Toko" if kirim_ke_toko else ""
    )

    submit = st.form_submit_button("Simpan")

    if submit:
        row_produk = df_produk[df_produk["Nama Barang"] == produk].iloc[0]
        tanggal = datetime.now().strftime("%Y-%m-%d")

        # ❌ VALIDASI PENTING
        if kirim_ke_toko and lokasi != "Gudang":
            st.error("Pengiriman ke toko hanya boleh dari Gudang")
            st.stop()
        # 🔍 cek stok
        if lokasi == "Gudang":
            stok_tersedia = int(row_produk["Stock Gudang"])
        elif lokasi == "Toko":
            stok_tersedia = int(row_produk["Stock Toko"])
        else:
            stok_tersedia = int(row_produk["Stock Akhir"])

        if qty > stok_tersedia:
            st.error(
                f"❌ Stok tidak mencukupi\n\n"
                f"Stok tersedia: {stok_tersedia}\n"
                f"Jumlah diminta: {qty}"
            )
            st.stop()

        # ➖ STOK KELUAR
        append_sheet("Stok_Keluar", [
            tanggal,
            row_produk["Kode Barang"],
            produk,
            qty,
            lokasi,
            ket if ket else "Dikirim ke Toko",
            st.session_state["user"] 
        ])

        # ➕ AUTO STOK MASUK KE TOKO
        if kirim_ke_toko:
            append_sheet("Stok_Masuk", [
                tanggal,
                row_produk["Kode Barang"],
                produk,
                qty,
                "Toko",
                "",  # supplier kosong
                "Dikirim dari Gudang",
                st.session_state["user"] 
            ])

        st.success("Stok keluar dicatat")
        if kirim_ke_toko:
            st.info("Stok otomatis ditambahkan ke Toko")

        st.rerun()
