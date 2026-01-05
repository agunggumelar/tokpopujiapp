import streamlit as st
import pandas as pd
from datetime import date
from gsheet import read_sheet, append_sheet

def generate_next_id(df, col, prefix, pad):
    if df.empty or col not in df.columns:
        return f"{prefix}{'1'.zfill(pad)}"

    last_num = (
        df[col]
        .dropna()
        .astype(str)
        .str.replace(prefix, "", regex=False)
        .astype(int)
        .max()
    )

    return f"{prefix}{str(last_num + 1).zfill(pad)}"

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Master Produk",
    layout="wide"
)

st.title("🧱 Master Produk & Harga")

# =========================
# LOAD DATA
# =========================
df_produk = read_sheet("produk_master")
df_varian = read_sheet("produk_varian")
df_harga  = read_sheet("harga_produk")
df_kategori = read_sheet("Kategori")

list_kategori = (
    df_kategori["Nama"]
    .dropna()
    .unique()
    .tolist()
)

# =========================
# NORMALISASI TIPE DATA
# =========================
if not df_harga.empty:
    df_harga["harga"] = (
        df_harga["harga"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .astype(int)
    )
    df_harga["tanggal"] = pd.to_datetime(df_harga["tanggal"])

# =========================
# FORM INPUT (OPTIONAL)
# =========================
with st.expander("➕ Input Data (Opsional)", expanded=False):

    tab1, tab2, tab3 = st.tabs([
        "Produk",
        "Varian",
        "Harga"
    ])

    # ========= PRODUK =========
    with tab1:
        with st.form("form_produk"):
            st.subheader("Input Produk")
            produk_id = generate_next_id(
                df_produk,
                "produk_id",
                "P",
                5
            )

            st.text_input("Produk ID", value=produk_id, disabled=True)
            nama = st.text_input("Nama Produk")
            kategori = st.selectbox(
                "Kategori",
                list_kategori
            )
            detail = st.text_area("Detail")

            submit = st.form_submit_button("Simpan Produk")

            if submit:
                append_sheet("produk_master", [
                    produk_id,
                    nama,
                    kategori,
                    detail
                ])
                st.success("Produk tersimpan")
                st.rerun()

    # ========= VARIAN =========
    with tab2:
        produk_map = dict(
            zip(df_produk["produk_id"], df_produk["nama_produk"])
        )
        produk_option = (
            df_produk["produk_id"] + " | " + df_produk["nama_produk"]
        )

        with st.form("form_varian"):
            st.subheader("Input Varian Produk")

            varian_id = generate_next_id(df_varian, "varian_id", "V", 6)
            st.text_input("Varian ID", value=varian_id, disabled=True)

            selected_produk = st.selectbox(
                "Produk",
                produk_option
            )

            produk_id = selected_produk.split(" | ")[0]
            nama_produk = produk_map.get(produk_id, "")

            varian = st.text_input("Varian (100gr / 1kg / 1500ml)")

            submit = st.form_submit_button("Simpan Varian")

            if submit:
                append_sheet("produk_varian", [
                    varian_id,
                    produk_id,
                    nama_produk,
                    varian
                ])
                st.success("Varian berhasil ditambahkan")
                st.rerun()


    # ========= HARGA =========
    with tab3:
        df_varian["label"] = (
            df_varian["varian_id"] + " | " +
            df_varian["nama_produk"] + " (" +
            df_varian["varian"] + ")"
        )

        with st.form("form_harga"):
            st.subheader("Input Harga Produk")

            harga_id = generate_next_id(df_harga, "harga_id", "H", 6)
            st.text_input("Harga ID", value=harga_id, disabled=True)

            selected_varian = st.selectbox(
                "Produk & Varian",
                df_varian["label"]
            )

            varian_id = selected_varian.split(" | ")[0]

            row = df_varian[df_varian["varian_id"] == varian_id].iloc[0]


            # tipe_harga = st.selectbox(
            #     "Tipe Harga",
            #     ["ecer", "pack", "dus"]
            # )
            tipe_harga = st.text_input("Tipe Harga")

            harga = st.number_input(
                "Harga",
                min_value=0,
                step=1000
            )

            tanggal = st.date_input("Tanggal", value=date.today())

            submit = st.form_submit_button("Simpan Harga")

            if submit:
                append_sheet("harga_produk", [
                    harga_id,
                    varian_id,
                    tipe_harga,
                    harga,
                    tanggal.strftime("%Y-%m-%d")
                ])
                st.success("Harga berhasil ditambahkan")
                st.rerun()

                
    # =========================
    # NORMALISASI NAMA KOLOM
    # =========================
    df_produk = df_produk.rename(columns={
        "Nama Produk": "nama_produk",
        "nama produk": "nama_produk"
    })

# =========================
# MERGE VIEW (PENTING)
# =========================
st.divider()
st.subheader("📊 View Gabungan (Produk + Varian + Harga)")

if not df_produk.empty and not df_varian.empty and not df_harga.empty:
    df_merge = (
        df_produk
        .merge(
            df_varian[["varian_id", "produk_id", "varian"]],
            on="produk_id",
            how="left"
        )
        .merge(
            df_harga[["varian_id", "tipe_harga", "harga", "tanggal"]],
            on="varian_id",
            how="left"
        )
        .sort_values("tanggal", ascending=False)
        .reset_index(drop=True)
    )

    st.metric(
        "Total Produk",
        df_merge["produk_id"].nunique()
    )

    st.dataframe(
        df_merge[[
            "produk_id",
            "nama_produk",
            "kategori",
            "varian",
            "tipe_harga",
            "harga",
            "tanggal"
        ]],
        use_container_width=True
    )

else:
    st.warning("⚠️ Data belum lengkap (produk / varian / harga).")
