import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Extractor Chat WA", layout="wide")
st.title("📦 Ekstraksi Data Barang dari Chat WhatsApp")

# =========================
# HELPER
# =========================
def format_rupiah(x):
    return f"Rp {x:,.0f}".replace(",", ".")

def extract_nama_produk_log(pesan):
    pesan = pesan.lower()

    # buang kata umum
    pesan = re.sub(
        r'\b(jual|ecer|ds|dus|pk|pcs|isi|uk|per|botol|pack|renteng)\b',
        '',
        pesan
    )

    # potong setelah angka
    pesan = re.sub(r'\d+.*', '', pesan)

    return pesan.strip().title()

# =========================
# UPLOAD FILE
# =========================
uploaded_file = st.file_uploader(
    "Upload file chat WhatsApp (.txt)",
    type=["txt"]
)

# =========================
# MAIN
# =========================
if uploaded_file:
    with st.spinner("⏳ Memproses chat WhatsApp..."):
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        lines = content.splitlines()

        # =========================
        # DATA PRODUK
        # =========================
        data = []

        for line in lines:
            # skip cepat kalau ga ada harga
            if "rb" not in line.lower():
                continue

            # =========================
            # TANGGAL
            # =========================
            date_match = re.search(r'(\d{2}/\d{2}/\d{2})', line)
            if not date_match:
                continue

            tanggal = datetime.strptime(
                date_match.group(1), "%d/%m/%y"
            ).date()

            # =========================
            # PESAN
            # =========================
            if ":" not in line:
                continue
            pesan = line.split(":", 1)[1].lower()

            # =========================
            # NAMA PRODUK (AMAN)
            # =========================
            nama_produk = pesan

            # hapus kata jualan umum
            nama_produk = re.sub(
                r'\b(jual|harga|hrg|ecer|dus|ds|pk|pcs|isi|kalau|dihitung|u jual)\b',
                '',
                nama_produk
            )

            # hapus varian & harga di belakang
            nama_produk = re.sub(
                r'(\d+\s?(g|kg|ml|l)|\d+\s*rb).*',
                '',
                nama_produk
            )

            nama_produk = nama_produk.strip()
            if len(nama_produk) < 2:
                continue

            # =========================
            # VARIAN + HARGA
            # =========================
            pairs = re.findall(
                r'(\d+\s?(?:g|kg|ml|l))\s+(\d+)\s*rb',
                pesan
            )

            # fallback: harga tanpa varian
            if not pairs:
                prices = re.findall(r'(\d+)\s*rb', pesan)
                pairs = [("unknown", p) for p in prices]

            # =========================
            # SIMPAN DATA
            # =========================
            for varian, harga in pairs:
                tipe = "unknown"

                if "ecer" in pesan:
                    tipe = "ecer"
                if any(x in pesan for x in ["ds", "dus", "pk"]):
                    tipe = "dus"

                data.append({
                    "tanggal": tanggal,
                    "nama_produk": nama_produk.title(),
                    "varian": varian.replace(" ", ""),
                    "tipe_harga": tipe,
                    "harga": int(harga) * 1000
                })

        # =========================
        # LOG CHAT UPDATE HARGA
        # =========================
        log_data = []

        for line in lines:
            if "rb" not in line.lower():
                continue

            if " - " not in line or ":" not in line:
                continue

            date_match = re.search(r'(\d{2}/\d{2}/\d{2})', line)
            if not date_match:
                continue

            tanggal = datetime.strptime(
                date_match.group(1), "%d/%m/%y"
            ).date()

            header, pesan = line.split(":", 1)
            pengirim = header.split(" - ")[1].strip()
            pesan_lower = pesan.lower()

            prices = re.findall(r'\d+\s*rb', pesan_lower)
            indikasi_jual = any(
                k in pesan_lower for k in ["jual", "harga", "hrg"]
            )

            if not prices or not indikasi_jual:
                continue

            log_data.append({
                "tanggal": tanggal,
                "pengirim": pengirim,
                "pesan_asli": pesan.strip(),
                "harga_ditemukan": ", ".join(prices),
                "jumlah_harga": len(prices)
            })

    # =========================
    # OUTPUT PRODUK
    # =========================
    if data:
        df = (
            pd.DataFrame(data)
            .drop_duplicates()
            .sort_values("tanggal", ascending=False)
            .reset_index(drop=True)
        )

        df["harga_rupiah"] = df["harga"].apply(format_rupiah)

        st.subheader("📊 Hasil Ekstraksi Produk")
        st.dataframe(
            df[[
                "tanggal",
                "nama_produk",
                "varian",
                "tipe_harga",
                "harga_rupiah",
                "harga"
            ]],
            use_container_width=True
        )

        # =========================
        # EXPORT EXCEL
        # =========================
        def to_excel(df_produk, df_log):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_produk.to_excel(writer, index=False, sheet_name="Produk")
                if df_log is not None:
                    df_log.to_excel(writer, index=False, sheet_name="Log_Chat")
            return output.getvalue()

        df_log_export = pd.DataFrame(log_data) if log_data else None
        excel_data = to_excel(df, df_log_export)

        st.download_button(
            "⬇️ Download Excel",
            excel_data,
            "hasil_ekstraksi_barang.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # =========================
        # AUTO MASTER PRODUK (AMAN)
        # =========================

        df_base = df.copy()   # <<< INI KUNCI NYAWA

        # MASTER PRODUK
        df_produk_master = (
            df_base[["nama_produk"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        df_produk_master["produk_id"] = [
            f"P{str(i+1).zfill(4)}"
            for i in range(len(df_produk_master))
        ]

        # MASTER VARIAN
        df_varian = (
            df_base[["nama_produk", "varian"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        df_varian = df_varian.merge(
            df_produk_master,
            on="nama_produk",
            how="left"
        )

        df_varian["varian_id"] = [
            f"V{str(i+1).zfill(5)}"
            for i in range(len(df_varian))
        ]

        # HISTORI HARGA
        df_harga = df_base.merge(
            df_varian,
            on=["nama_produk", "varian"],
            how="left"
        )

        df_harga = df_harga[[
            "varian_id",
            "tipe_harga",
            "harga",
            "tanggal"
        ]].drop_duplicates()

        df_harga["harga_id"] = [
            f"H{str(i+1).zfill(6)}"
            for i in range(len(df_harga))
        ]


        with st.expander("📦 Master Produk (Auto)"):
            st.dataframe(df_produk_master, use_container_width=True)

        with st.expander("📐 Varian Produk"):
            st.dataframe(df_varian, use_container_width=True)

        with st.expander("💰 Histori Harga"):
            st.dataframe(df_harga, use_container_width=True)
            
        def to_excel(df_produk):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_produk.to_excel(writer, index=False, sheet_name="Produk")
                df_produk_master.to_excel(writer, index=False, sheet_name="Produk_Master")
                df_varian.to_excel(writer, index=False, sheet_name="Produk_Varian")
                df_harga.to_excel(writer, index=False, sheet_name="Harga_Produk")

            return output.getvalue()

        

    # =========================
    # OUTPUT LOG CHAT
    # =========================
    if log_data:
        df_log = (
            pd.DataFrame(log_data)
            .drop_duplicates()
            .sort_values("tanggal", ascending=False)
            .reset_index(drop=True)
        )

        # =========================
        # NAMA PRODUK DARI CHAT
        # =========================
        df_log["nama_produk"] = df_log["pesan_asli"].apply(
            extract_nama_produk_log
        )

        # =========================
        # PRODUK UNIK + TANGGAL TERAKHIR
        # =========================
        df_produk_terakhir = (
            df_log
            .sort_values("tanggal", ascending=False)
            .drop_duplicates(subset=["nama_produk"])
            .reset_index(drop=True)
        )

        # =========================
        # TAMPILKAN
        # =========================
        st.subheader("📌 Produk Unik (Harga Terakhir)")
        st.metric(
            "Total Produk Unik",
            df_produk_terakhir["nama_produk"].nunique()
        )

        st.dataframe(
            df_produk_terakhir[
                ["tanggal", "nama_produk", "pesan_asli", "harga_ditemukan"]
            ],
            use_container_width=True
        )

        # =========================
        # LOG FULL (OPTIONAL)
        # =========================
        st.subheader("🧾 Log Chat Update Harga (Full)")
        st.metric("Total Log Chat", len(df_log))
        st.dataframe(df_log, use_container_width=True)

    
    if not data and not log_data:
        st.warning("⚠️ Tidak ditemukan data harga di chat.")
