import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Analisis Makroekonomi BBM", layout="wide")

st.title("📊 Analisis Kebijakan Substitusi Impor BBM & Elektrifikasi")
st.markdown("Dashboard ini menyajikan 7 poin utama analisis dampak ekonomi dari kebijakan B50 dan Elektrifikasi Kendaraan berdasarkan data historis dan proyeksi 2026.")

# --- PARAMETER INPUT (Main Page) ---
with st.container(border=True):
    st.subheader("⚙️ Pengaturan Variabel Utama")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        target_ev = st.slider("Target Elektrifikasi (%)", 0, 100, 100, step=5, help="Persentase Motor & Mobil <1400cc yang beralih ke listrik")
    with col_g2:
        harga_minyak = st.slider("Harga Minyak Dunia ($/bbl)", 50, 150, 90, step=5)
    with col_g3:
        kurs_rp = st.slider("Kurs Rupiah (Rp/USD)", 14000, 18000, 16896, step=100)

st.divider()

# ==========================================
# 1. PENGHEMATAN PEMERINTAH (SOLAR & BENSIN)
# ==========================================
st.header("1️⃣ Penghematan Pemerintah (Subsidi BBM)")

# --- Sub-Poin Solar ---
st.subheader("a. Substitusi Impor Solar (B50)")
st.markdown("""
Berdasarkan regresi logaritmik $y = 32.41 + 3.82 \ln(x)$, konsumsi solar 2026 diprediksi sebesar **39,84 jt kL**. 
Dengan **B50**, produksi solar fosil (20,1 jt kL) dan FAME (19,92 jt kL) mencukupi kebutuhan domestik tanpa impor.
""")

col1_a, col1_b = st.columns([2, 1])
with col1_a:
    df_solar = pd.DataFrame({
        "Komposisi": ["Produksi Solar Fosil", "FAME (Bio)"],
        "Volume (Juta kL)": [20.1, 19.92]
    })
    fig_solar = px.bar(df_solar, x="Komposisi", y="Volume (Juta kL)", text_auto='.2f', title="Pasokan Solar B50 vs Konsumsi (39.84 jt kL)")
    st.plotly_chart(fig_solar, use_container_width=True, config={'staticPlot': True})

with col1_b:
    subsidi_solar = 5150 # Rp/liter
    hemat_solar_t = (4.9 * subsidi_solar) / 1000 # Triliun
    st.success(f"**Hemat Subsidi Solar:**\nRp {hemat_solar_t:.2f} Triliun")
    st.caption("*(Dihitung dari penghentian impor 4.9 jt kL)*")

# --- Sub-Poin Bensin ---
st.subheader("b. Substitusi Impor Bensin (Pertalite)")
st.markdown("Target elektrifikasi difokuskan pada segmen **Motor** dan **Mobil <1400cc** yang menyumbang porsi terbesar konsumsi bensin.")

col1_c, col1_d = st.columns([1, 2])
with col1_c:
    df_bensin = pd.DataFrame({
        "Kategori": ["Motor", "Mobil <1400cc", "Lainnya"],
        "Porsi": [28.6, 31.4, 40.0]
    })
    fig_pie = px.pie(df_bensin, values='Porsi', names='Kategori', hole=0.4, title="Profil Pengguna Pertalite")
    st.plotly_chart(fig_pie, use_container_width=True)

with col1_d:
    vol_target = 17.4 # (8.3 + 9.1) jt kL
    vol_hemat = vol_target * (target_ev / 100)
    subsidi_bensin = 1700 # Rp/liter
    hemat_bensin_t = (vol_hemat * subsidi_bensin) / 1000
    st.info(f"Volume Bensin Dihemat: **{vol_hemat:.2f} Juta kL**")
    st.success(f"Potensi Hemat Subsidi Bensin: **Rp {hemat_bensin_t:.2f} Triliun**")

st.divider()

# ==========================================
# 2. PENGHEMATAN MASYARAKAT & PDB
# ==========================================
st.header("2️⃣ Penghematan Masyarakat & Multiplier Effect")
st.markdown("Biaya energi EV jauh lebih efisien (~5x lipat). Penghematan ini dialokasikan kembali ke konsumsi rumah tangga.")

col2_a, col2_b = st.columns(2)
with col2_a:
    st.subheader("Kalkulator Multiplier (k)")
    st.latex(r"k = \frac{1}{1 - c(1 - t) + m}")
    c_val = st.number_input("MPC (c)", value=0.779)
    t_val = st.number_input("Tax/GDP (t)", value=0.118)
    m_val = st.number_input("Import/GDP (m)", value=0.209)
    k_res = 1 / (1 - c_val * (1 - t_val) + m_val)
    st.metric("Nilai Multiplier (k)", f"{k_res:.3f}")

with col2_b:
    # 100% elektrifikasi = 139.2 T hemat masyarakat
    hemat_masyarakat = 139.2 * (target_ev / 100)
    pertumbuhan_pdb = hemat_masyarakat * k_res
    st.subheader("Dampak Ekonomi")
    st.metric("Hemat Biaya Energi Rakyat", f"Rp {hemat_masyarakat:.2f} T")
    st.success(f"**Potensi Pertumbuhan PDB: Rp {pertumbuhan_pdb:.2f} Triliun**")

st.divider()

# ==========================================
# 3. KECUKUPAN LISTRIK
# ==========================================
st.header("3️⃣ Skenario Kecukupan Listrik")
st.markdown("Asumsi: 1 Liter BBM setara dengan 1,2 kWh listrik.")

kebutuhan_twh = vol_hemat * 1.2
surplus_twh = 36.31

col3_a, col3_b = st.columns([2, 1])
with col3_a:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = kebutuhan_twh,
        title = {'text': "Beban Listrik Baru (TWh)"},
        gauge = {
            'axis': {'range': [None, 50]},
            'steps': [{'range': [0, surplus_twh], 'color': "lightgreen"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': surplus_twh}
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col3_b:
    if kebutuhan_twh <= surplus_twh:
        st.success(f"**Aman!** Beban EV ({kebutuhan_twh:.2f} TWh) di bawah surplus PLN ({surplus_twh} TWh).")
    else:
        st.error("Peringatan: Surplus listrik tidak mencukupi!")

st.divider()

# ==========================================
# 4. PENGHEMATAN DEVISA
# ==========================================
st.header("4️⃣ Penghematan Devisa Negara")
st.markdown("Mencegah aliran modal keluar untuk impor minyak mentah.")

barel_bensin = 93.85 * (target_ev / 100)
barel_solar = 30.82
tot_barel = barel_bensin + barel_solar
hemat_usd = tot_barel * harga_minyak
hemat_rp_devisa = (hemat_usd * kurs_rp) / 1_000_000

st.info(f"Total Impor Dicegah: **{tot_barel:.2f} Juta Barel**")
st.success(f"Total Devisa Terselamatkan: **Rp {hemat_rp_devisa:.2f} Triliun**")

st.divider()

# ==========================================
# 5. INFRASTRUKTUR SPBKLU (SWAP BATERAI)
# ==========================================
st.header("5️⃣ Infrastruktur SPBKLU (Motor Listrik)")
st.markdown("Untuk mendukung mobilitas, diperlukan ekosistem baterai swap yang masif.")

col5_a, col5_b = st.columns(2)
with col5_a:
    porsi_swap = st.slider("Target Pengguna Swap (%)", 0, 100, 40)
    # Estimasi baterai beredar 182-258 jt unit
    estimasi_baterai = (182.21 + (258.04 - 182.21) * (porsi_swap/100)) * (target_ev/100)
    st.warning(f"Kebutuhan Pack Baterai: **{estimasi_baterai:.2f} Juta Unit**")

with col5_b:
    st.info("""
    **Distribusi Lokasi:**
    - Unit KDKMP (Koperasi Desa/Kelurahan)
    - Jaringan Convenience Store (Indomaret/Alfamart)
    - SPBU Eksisting
    """)

st.divider()

# ==========================================
# 6. INFRASTRUKTUR SPKLU (MOBIL LISTRIK)
# ==========================================
st.header("6️⃣ Infrastruktur SPKLU (Mobil Listrik)")

rasio_spklu = st.number_input("Rasio Mobil per Mesin SPKLU", value=15)
mobil_ev = 4.46 * (target_ev / 100) # Juta unit
kebutuhan_spklu = (mobil_ev * 1_000_000) / rasio_spklu

col6_a, col6_b = st.columns(2)
with col6_a:
    st.metric("Jumlah Mesin SPKLU Dibutuhkan", f"{kebutuhan_spklu:,.0f} Unit")
with col6_b:
    investasi_spklu = (kebutuhan_spklu * 250) / 1_000_000 # Asumsi 250jt/unit
    st.warning(f"Estimasi Nilai Investasi: **Rp {investasi_spklu:.2f} Triliun**")

st.divider()

# ==========================================
# 7. POTENSI LOSS PAJAK DAERAH
# ==========================================
st.header("7️⃣ Potensi Loss Pajak Daerah")
st.markdown("Dampak negatif pada Pendapatan Asli Daerah (PAD) yang perlu dimitigasi.")

loss_pbbkb = (vol_hemat * 10000 * 0.10) / 1000 # Asumsi tarif 10%
loss_pkb = 43.86 * (target_ev / 100)

col7_a, col7_b = st.columns(2)
with col7_a:
    st.error(f"Loss PBBKB: **Rp {loss_pbbkb:.2f} T**")
with col7_b:
    st.error(f"Loss PKB: **Rp {loss_pkb:.2f} T**")

with st.container(border=True):
    st.subheader("💡 Rekomendasi Mitigasi")
    st.markdown("""
    1. Penerapan **Pajak Listrik KBLBB** sebagai substitusi PBBKB.
    2. Realokasi dana subsidi yang dihemat (Point 1) untuk pembangunan infrastruktur daerah.
    3. Optimalisasi pajak dari ekosistem industri baterai nasional.
    """)
