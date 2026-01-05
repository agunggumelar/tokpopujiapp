import streamlit as st
import pandas as pd
from datetime import datetime
from gsheet import read_sheet, append_sheet

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="POS Penjualan",
    layout="wide"
)

st.title("🛍️ POS - Penjualan Produk")

# =========================
# HELPER
# =========================
def rupiah(x):
    try:
        return f"Rp {int(x):,}".replace(",", ".")
    except:
        return "-"

# =========================
# LOAD DATA DARI GOOGLE SHEET
# =========================
@st.cache_data
def load_data():
    # Pastikan kamu punya fungsi read_sheet
    # yang mengambil data Google Sheet per nama sheet
    df_produk = read_sheet("produk_master")
    df_varian = read_sheet("produk_varian")
    df_harga = read_sheet("harga_produk")

    # Pastikan harga jadi numeric
    df_harga["harga"] = (
        df_harga["harga"]
        .replace({r"[^\d]": ""}, regex=True)
        .astype(float)
    )

    # convert tanggal
    df_harga["tanggal"] = pd.to_datetime(df_harga["tanggal"])

    return df_produk, df_varian, df_harga

df_produk, df_varian, df_harga = load_data()

# =========================
# AMBIL HARGA TERAKHIR PER VARIAN
# =========================
df_harga_last = (
    df_harga.sort_values("tanggal", ascending=False)
            .drop_duplicates(subset=["varian_id", "tipe_harga"])
)

# =========================
# GABUNG DATA POS
# =========================
df_pos = (
    df_varian
    .merge(df_produk, on=["produk_id", "nama_produk"], how="left")
    .merge(df_harga_last, on="varian_id", how="left")
)

# =========================
# FILTER
# =========================
st.subheader("🔎 Cari Produk")

c1, c2 = st.columns([3, 1])

with c1:
    search = st.text_input("Cari nama produk...")

with c2:
    kategori_list = ["Semua"] + sorted(df_pos["kategori"].dropna().unique())
    kategori = st.selectbox("Kategori", kategori_list)

df_view = df_pos.copy()

if search:
    df_view = df_view[
        df_view["nama_produk"].str.contains(search, case=False)
    ]

if kategori != "Semua":
    df_view = df_view[df_view["kategori"] == kategori]

# =========================
# KERANJANG
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# GRID PRODUK (FIX DUPLICATE KEY)
# =========================
produk_group = df_view.groupby("produk_id")

cols = st.columns(4)

for i, (produk_id, g) in enumerate(produk_group):
    row = g.iloc[0]  # data produk utama

    with cols[i % 4]:
        st.markdown(f"### {row['nama_produk']}")
        st.caption(row["kategori"])

        # ===== VARIAN =====
        varian_list = g["varian"].unique().tolist()
        selected_varian = st.selectbox(
            "Varian",
            varian_list,
            key=f"var_{produk_id}"
        )

        df_var = g[g["varian"] == selected_varian]

        # ===== TIPE HARGA =====
        tipe_list = df_var["tipe_harga"].unique().tolist()
        selected_tipe = st.selectbox(
            "Tipe Harga",
            tipe_list,
            key=f"tipe_{produk_id}"
        )

        harga = df_var[
            df_var["tipe_harga"] == selected_tipe
        ]["harga"].iloc[0]

        st.write(rupiah(harga))

        qty = st.number_input(
            "Qty",
            min_value=1,
            value=1,
            key=f"qty_{produk_id}"
        )

        if st.button(
            "🛒 Tambah",
            key=f"add_{produk_id}"
        ):
            st.session_state.cart.append({
                "produk_id": produk_id,
                "nama_produk": row["nama_produk"],
                "varian": selected_varian,
                "tipe_harga": selected_tipe,
                "harga": harga,
                "qty": qty
            })


# =========================
# SIDEBAR KERANJANG
# =========================
st.sidebar.header("🛍️ Keranjang Belanja")

total = 0
for item in st.session_state.cart:
    subtotal = item["harga"] * item["qty"]
    total += subtotal

    st.sidebar.write(
        f"{item['produk']} ({item['varian']} {item['tipe']}) x{item['qty']}"
    )
    st.sidebar.caption(rupiah(subtotal))

st.sidebar.markdown("---")
st.sidebar.metric("TOTAL", rupiah(total))

if st.sidebar.button("💳 BAYAR"):
    st.success("🎉 Transaksi berhasil!")
    st.session_state.cart = []
