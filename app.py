import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Substitusi BBM", layout="wide", page_icon="📈")

st.title("🔋 Analisis Komprehensif: Substitusi Impor BBM & Elektrifikasi")
st.markdown("Dashboard ini merupakan translasi digital dari analisis makroekonomi penghentian impor Solar dan Bensin (Pertalite) melalui kebijakan mandatori B50 dan Elektrifikasi Kendaraan.")

# --- PARAMETER GLOBAL ---
with st.sidebar:
    st.header("⚙️ Parameter Global")
    target_ev = st.slider("Target Elektrifikasi (%)", 0, 100, 100, step=5, help="Target elektrifikasi untuk motor dan mobil <1400cc")
    harga_minyak = st.slider("Harga Minyak Dunia ($/bbl)", 50, 150, 90, step=5)
    kurs_rp = st.slider("Kurs Rupiah (Rp/USD)", 14000, 18000, 16896, step=100)

st.divider()

# ==========================================
# PENDAHULUAN: PROYEKSI KONSUMSI SOLAR & B50
# ==========================================
st.header("A. Proyeksi Konsumsi Solar & Kapasitas B50")
st.markdown("Menggunakan regresi logaritmik dari data 2020-2025, kita memproyeksikan konsumsi solar:")
st.latex(r"y_i = a + b \ln(x_i)")
st.latex(r"y = 32.41 + 3.82 \ln(x)")

col_p1, col_p2 = st.columns([2, 1])
with col_p1:
    # Grafik Proyeksi Konsumsi
    df_solar = pd.DataFrame({
        "Tahun": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
        "Konsumsi (Juta kL)": [33.5, 33.4, 36.2, 37.8, 39.2, 39.5, 39.84]
    })
    fig_solar = px.line(df_solar, x="Tahun", y="Konsumsi (Juta kL)", markers=True, title="Historis & Proyeksi Konsumsi Solar Indonesia")
    fig_solar.add_vline(x=2025, line_dash="dash", line_color="red", annotation_text="Proyeksi 2026 ->")
    st.plotly_chart(fig_solar, use_container_width=True)

with col_p2:
    st.info("""
    **Skenario Mandatori B50 (2026)**
    - Proyeksi Konsumsi: **39,84 jt kL**
    - Kebutuhan FAME (50%): **19,92 jt kL**
    - Kebutuhan Solar Fosil (50%): **19,92 jt kL**
    - Produksi Kilang Lokal (+RDMP 1,8 jt kL): **20,1 jt kL**
    
    **Kesimpulan:** Dengan B50, impor solar menjadi **Nol (0)** dan terdapat surplus produksi fosil sebesar **0,18 jt kL**.
    """)

st.divider()

# ==========================================
# POINT 1: PENGHEMATAN PEMERINTAH
# ==========================================
st.header("① Penghematan Pemerintah (Subsidi BBM)")

st.subheader("a. Penghematan Subsidi Solar")
st.markdown("Jika impor 4,9 juta kL solar dihentikan, subsidi pemerintah hemat, namun BPDPKS harus membayar selisih harga FAME.")
col1_a, col1_b = st.columns(2)
with col1_a:
    subsidi_solar = st.number_input("Subsidi Solar (Rp/Liter)", value=5150)
    gap_fame = st.number_input("Gap Harga FAME vs Solar (Rp/Liter)", value=3000)
with col1_b:
    hemat_solar_kotor = 4.9 * subsidi_solar / 1000 # Triliun
    beban_bpdpks = 9.9 * gap_fame / 1000 # Triliun (mengganti 9.9 jt kl solar)
    hemat_solar_bersih = hemat_solar_kotor - (4.9 * gap_fame / 1000) # Penyesuaian sesuai dokumen
    st.success(f"**Penghematan Bersih Pemerintah:** Rp 10,53 Triliun\n\n*(Hitungan: Hemat subsidi Rp {hemat_solar_kotor:.2f} T dikurangi beban FAME untuk porsi impor)*")

st.subheader("b. Bensin (Pertalite) & Solusi Elektrifikasi")
st.markdown("Konsumsi Pertalite mencapai 29 juta kL. Target elektrifikasi difokuskan pada Motor dan Mobil < 1400cc.")

df_kendaraan = pd.DataFrame({
    "Kategori": ["Motor", "Mobil < 1400cc", "Mobil 1400-1600cc", "Mobil > 1600cc"],
    "Persentase": [28.6, 31.4, 31.4, 8.6],
    "Volume (Juta kL)": [8.3, 9.1, 9.1, 2.5]
})
fig_kendaraan = px.pie(df_kendaraan, values='Persentase', names='Kategori', title="Profil Konsumsi Pertalite (Berdasarkan Kategori CC)")
st.plotly_chart(fig_kendaraan, use_container_width=True)

target_bensin = 8.3 + 9.1 # 17.4 jt kL
bensin_dihemat = target_bensin * (target_ev / 100)
subsidi_pertalite = st.number_input("Subsidi Pertalite Aktual (Rp/Liter)", value=1700)
hemat_bensin_rp = bensin_dihemat * subsidi_pertalite / 1000 # Triliun

st.info(f"Dengan elektrifikasi **{target_ev}%**, bensin yang dihemat adalah **{bensin_dihemat:.2f} Juta kL**.\n\nPenghematan Subsidi Pertalite: **Rp {hemat_bensin_rp:.2f} Triliun**.")

st.markdown("**Skenario E10 untuk Sisa Bensin:**")
sisa_bensin = 29 - bensin_dihemat
butuh_etanol = sisa_bensin * 0.10
st.warning(f"Sisa konsumsi bensin: {sisa_bensin:.2f} Juta kL. Jika menggunakan E10, butuh Etanol **{butuh_etanol:.2f} Juta kL**. Jika yield tebu 4,9 kL/ha, dibutuhkan lahan **{(butuh_etanol/4.9)*1000000:,.0f} Hektare**.")

st.divider()

# ==========================================
# POINT 2: PENGHEMATAN MASYARAKAT & PDB
# ==========================================
st.header("② Penghematan Masyarakat & Multiplier Effect")
st.markdown("Biaya operasional EV sangat murah (~Rp 41,3/km untuk motor vs Rp 200/km untuk bensin). Secara total, biaya energi masyarakat turun drastis.")

biaya_bensin_total = bensin_dihemat * 10000 / 1000 # Asumsi Rp 10.000/L
biaya_listrik_total = biaya_bensin_total / 5 # 5x lebih hemat
hemat_masyarakat = biaya_bensin_total - biaya_listrik_total

st.latex(r"\Delta = \text{Biaya Bensin} - \text{Biaya Listrik} = 174 \text{ T} - 34.8 \text{ T} = 139.2 \text{ T}")

st.markdown("**Kalkulator Multiplier Effect Keynesian:**")
st.latex(r"k = \frac{1}{1 - c(1 - t) + m}")

col2_a, col2_b, col2_c = st.columns(3)
with col2_a:
    c_val = st.number_input("MPC (c)", value=0.779, format="%.3f")
with col2_b:
    t_val = st.number_input("Tax Rate (t)", value=0.118, format="%.3f")
with col2_c:
    m_val = st.number_input("Import Prop. (m)", value=0.209, format="%.3f")

k_multiplier = 1 / (1 - c_val * (1 - t_val) + m_val)
tambahan_pdb = hemat_masyarakat * k_multiplier

st.success(f"Nilai Multiplier (k): **{k_multiplier:.3f}**\n\nPotensi Pertumbuhan Ekonomi (PDB): Rp {hemat_masyarakat:.2f} T × {k_multiplier:.3f} = **Rp {tambahan_pdb:.2f} Triliun**.")

st.divider()

# ==========================================
# POINT 3: KECUKUPAN LISTRIK
# ==========================================
st.header("③ Skenario Kecukupan Listrik")
st.markdown("Konversi energi: 1 Liter BBM ≈ 1,2 kWh.")

kebutuhan_listrik_twh = bensin_dihemat * 1.2 * 1_000_000_000 / 1_000_000_000 # TWh
surplus_listrik = st.number_input("Surplus Listrik (TWh)", value=36.31)

fig_listrik = go.Figure(go.Indicator(
    mode = "number+gauge",
    value = kebutuhan_listrik_twh,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Kebutuhan Listrik EV (TWh)"},
    gauge = {
        'axis': {'range': [None, 50]},
        'bar': {'color': "green"},
        'steps': [
            {'range': [0, surplus_listrik], 'color': "lightgray"},
            {'range': [surplus_listrik, 50], 'color': "red"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': surplus_listrik
        }
    }
))
st.plotly_chart(fig_listrik, use_container_width=True)
if kebutuhan_listrik_twh <= surplus_listrik:
    st.success("Kapasitas Pembangkit Listrik Nasional MENCUKUPI.")
else:
    st.error("Peringatan: Kebutuhan melebihi surplus listrik!")

st.divider()

# ==========================================
# POINT 4: DEVISA YANG DIHEMAT
# ==========================================
st.header("④ Devisa yang Dihemat")
st.markdown("Menghentikan impor BBM menjaga cadangan devisa dan menstabilkan Rupiah.")

barel_bensin = 93.85 * (target_ev / 100) # Juta barel
barel_solar = 30.82 # Juta barel
total_barel = barel_bensin + barel_solar

hemat_usd_m = total_barel * harga_minyak # Juta USD
hemat_rp_t = hemat_usd_m * kurs_rp / 1_000_000 # Triliun Rp

st.info(f"Total Impor Barel Dicegah: **{total_barel:.2f} Juta Barel**\n\nTotal Devisa Dihemat: **$ {hemat_usd_m/1000:.2f} Miliar** (Setara **Rp {hemat_rp_t:.2f} Triliun**).")

st.divider()

# ==========================================
# POINT 5 & 6: INFRASTRUKTUR SPBKLU & SPKLU
# ==========================================
st.header("⑤ & ⑥ Kebutuhan Infrastruktur Pengisian Daya")

col3_a, col3_b = st.columns(2)
with col3_a:
    st.subheader("⑤ SPBKLU (Motor - Swap Baterai)")
    st.markdown("Kebutuhan baterai untuk sistem *swap* dihitung dengan asumsi *buffer* 20%:")
    st.latex(r"B_{pool} = D \times \frac{d}{H} \times 1.2")
    porsi_2_baterai = st.slider("Porsi Motor 2 Baterai (%)", 0, 100, 20, step=10)
    porsi_swap_first = st.slider("Pengguna Swap-First (%)", 0, 100, 20, step=10)
    st.warning("Estimasi kebutuhan baterai beredar: **182,21 - 258,04 Juta Pack** (Tergantung rasio adopsi).")

with col3_b:
    st.subheader("⑥ SPKLU (Mobil Listrik)")
    st.markdown("Rasio ideal KBLBB per SPKLU diasumsikan turun dari 17:1 menjadi 15:1 pada 2030.")
    rasio_spklu = st.number_input("Rasio Mobil : 1 SPKLU", value=15)
    mobil_listrik = 4458000 * (target_ev / 100)
    kebutuhan_spklu = mobil_listrik / rasio_spklu
    st.warning(f"Kebutuhan Mesin SPKLU: **{kebutuhan_spklu:,.0f} Unit**\n\nEstimasi Biaya Investasi: **Rp 54,8 T s/d 90,2 T**.")

st.divider()

# ==========================================
# POINT 7: POTENSI LOSS PAJAK DAERAH
# ==========================================
st.header("⑦ Potensi Loss Pajak Daerah")
st.markdown("Elektrifikasi menyebabkan Pemerintah Daerah kehilangan Pajak Bahan Bakar Kendaraan Bermotor (PBBKB) dan Pajak Kendaraan Bermotor (PKB) dari kendaraan konvensional.")

st.latex(r"L_{PBBKB} = V \times P \times t")

col4_a, col4_b = st.columns(2)
with col4_a:
    tarif_pbbkb = st.slider("Tarif PBBKB Daerah (%)", 5, 10, 5)
    loss_pbbkb = bensin_dihemat * 10000 * (tarif_pbbkb / 100) / 1000 # Triliun
    st.error(f"**Potensi Loss PBBKB:**\nRp {loss_pbbkb:.2f} Triliun / Tahun\n*(~24.8% dari PBBKB Nasional)*")

with col4_b:
    loss_pkb = 43.86 * (target_ev / 100)
    st.error(f"**Potensi Loss PKB & SWDKLLJ:**\nRp {loss_pkb:.2f} Triliun / Tahun")

st.info("💡 **Rekomendasi Kebijakan:** Diperlukan skema **Pajak Listrik Khusus EV** yang dipungut saat *charging* di SPKLU atau *swap* baterai untuk menggantikan PAD yang hilang.")
