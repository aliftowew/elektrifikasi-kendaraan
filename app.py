import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Analisis Makroekonomi BBM", layout="wide")

st.title("📊 Analisis Kebijakan Substitusi Impor BBM & Elektrifikasi")
st.markdown("Dashboard ini menyajikan poin utama analisis dampak ekonomi dari kebijakan substitusi BBM berdasarkan data historis dan proyeksi.")

st.divider()

# ==========================================
# 1. PENGHEMATAN PEMERINTAH (SOLAR & BENSIN)
# ==========================================
st.header("1️⃣ Penghematan Pemerintah (Subsidi BBM)")

# --- Sub-Poin Solar ---
st.subheader("a. Substitusi Impor Solar & Dinamika FAME")

st.markdown("""
Berdasarkan regresi logaritmik $y = 32.41 + 3.82 \ln(x)$, **konsumsi solar 2026 diprediksi sebesar 39,84 Juta kL**. 
Berikut adalah tren historis pasokan solar di Indonesia dari tahun 2020 hingga proyeksi 2026:
""")

# Grafik Historis Konsumsi Solar
df_solar_hist = pd.DataFrame({
    "Tahun": ["2020", "2021", "2022", "2023", "2024", "2025", "2026 (Prediksi)"],
    "Konsumsi (Juta kL)": [33.5, 33.4, 36.2, 37.8, 39.2, 39.5, 39.84]
})
fig_solar_hist = px.line(df_solar_hist, x="Tahun", y="Konsumsi (Juta kL)", markers=True, 
                         title="Historis & Proyeksi Konsumsi Solar Nasional (2020 - 2026)")
fig_solar_hist.add_vline(x=5.5, line_dash="dash", line_color="red", annotation_text="Proyeksi ->")
fig_solar_hist.update_traces(line_color="#e63946", marker=dict(size=10))
st.plotly_chart(fig_solar_hist, use_container_width=True)

st.markdown("---")

# Slider Komposisi FAME
st.markdown("### 🎛️ Simulasi Komposisi FAME (Biosolar)")
st.markdown("Geser *slider* di bawah ini untuk melihat dampak komposisi FAME terhadap volume impor dan penghematan anggaran negara.")
target_fame = st.slider("Komposisi FAME (%)", min_value=30, max_value=80, value=50, step=5, 
                        help="Persentase campuran FAME (sawit) di dalam Biosolar.")

# Kalkulasi Solar Berdasarkan Slider
konsumsi_2026 = 39.84
produksi_fosil_lokal = 20.1 # Eksisting + RDMP (1.8)
impor_baseline = 4.9 # Juta kL (Target impor yang ingin dinolkan)

vol_fame = konsumsi_2026 * (target_fame / 100)
vol_fosil_dibutuhkan = konsumsi_2026 - vol_fame
vol_impor = max(0, vol_fosil_dibutuhkan - produksi_fosil_lokal)

# Kalkulasi Keuangan
impor_dihemat = max(0, impor_baseline - vol_impor)
subsidi_solar = 5150 # Rp/liter
gap_fame = 3000 # Rp/liter

hemat_subsidi_kotor = (impor_dihemat * subsidi_solar) / 1000 # Triliun
beban_bpdpks = (impor_dihemat * gap_fame) / 1000 # Triliun
hemat_bersih = hemat_subsidi_kotor - beban_bpdpks

# Menampilkan Rumus
st.markdown("**Rumus Perhitungan Penghematan:**")
st.latex(r"\text{Penghematan Subsidi} = \text{Volume Impor Dihemat} \times \text{Rp } 5.150")
st.latex(r"\text{Biaya Kompensasi FAME} = \text{Volume Impor Dihemat} \times \text{Rp } 3.000")
st.latex(r"\text{Penghematan Bersih} = \text{Penghematan Subsidi} - \text{Biaya Kompensasi FAME}")

# Layout Hasil Simulasi
col1_a, col1_b, col1_c = st.columns(3)
with col1_a:
    st.info(f"**Volume FAME Dibutuhkan:**\n\n{vol_fame:.2f} Juta kL")
    st.warning(f"**Volume Impor Solar:**\n\n{vol_impor:.2f} Juta kL")
with col1_b:
    st.success(f"**Penghematan Subsidi (Kotor):**\n\nRp {hemat_subsidi_kotor:.2f} Triliun")
    st.error(f"**Biaya FAME (BPDPKS):**\n\n- Rp {beban_bpdpks:.2f} Triliun")
with col1_c:
    st.success(f"### 💰 Hemat Bersih\n\n### Rp {hemat_bersih:.2f} T")

if target_fame == 50:
    st.caption("✅ **Kondisi B50:** Pada komposisi 50%, impor mencapai titik 0, penghematan subsidi kotor Rp 25,23 T dipotong biaya FAME Rp 14,7 T, menghasilkan penghematan bersih **Rp 10,53 T**.")
elif target_fame < 50:
    st.caption(f"⚠️ **Defisit Pasokan:** Pada komposisi B{target_fame}, produksi kilang lokal tidak cukup menutupi porsi fosil, sehingga negara masih harus mengimpor **{vol_impor:.2f} Juta kL** solar.")
else:
    st.caption(f"📈 **Surplus Solar:** Pada komposisi B{target_fame}, terjadi surplus solar fosil karena kebutuhan fosil domestik berada di bawah kapasitas kilang lokal.")

st.markdown("---")

# --- Sub-Poin Bensin ---
st.subheader("b. Substitusi Impor Bensin (Pertalite)")
target_ev = st.slider("Target Elektrifikasi (%)", 0, 100, 100, step=5, help="Persentase Motor & Mobil <1400cc yang beralih ke listrik")

st.markdown("Konsumsi Pertalite mencapai 29 juta kL. Jika kita elektrifikasi segmen terbesar yaitu Motor dan Mobil <1400cc:")

col1_d, col1_e = st.columns([1, 2])
with col1_d:
    df_bensin = pd.DataFrame({
        "Kategori": ["Motor", "Mobil <1400cc", "Lainnya"],
        "Porsi": [28.6, 31.4, 40.0]
    })
    fig_pie = px.pie(df_bensin, values='Porsi', names='Kategori', hole=0.4, title="Profil Konsumsi Pertalite")
    st.plotly_chart(fig_pie, use_container_width=True)

with col1_e:
    vol_target = 17.4 # (8.3 + 9.1) jt kL
    vol_hemat = vol_target * (target_ev / 100)
    subsidi_bensin = 1700 # Rp/liter
    hemat_bensin_t = (vol_hemat * subsidi_bensin) / 1000
    
    st.info(f"Volume Bensin Dihemat: **{vol_hemat:.2f} Juta kL**")
    st.success(f"Potensi Hemat Subsidi Bensin: **Rp {hemat_bensin_t:.2f} Triliun**")
    st.latex(r"\text{Hemat Bensin} = \text{Volume Dihemat} \times \text{Rp } 1.700")

st.divider()

# CATATAN: Poin 2 (Multiplier Effect PDB), Poin 3 (Listrik), dll diletakkan di bawah sini mengikuti kode sebelumnya.
