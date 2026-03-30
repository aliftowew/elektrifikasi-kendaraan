import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Makroekonomi BBM", layout="wide")

st.title("📊 Analisis Kebijakan Substitusi Impor BBM & Elektrifikasi")

# --- PENGATURAN GLOBAL (Di Main Page) ---
with st.container(border=True):
    st.subheader("⚙️ Pengaturan Parameter Global")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        target_ev = st.slider("Target Elektrifikasi Motor & Mobil (%)", 0, 100, 100, step=5)
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
with st.container(border=True):
    st.subheader("a. Substitusi Impor Solar & Dinamika FAME")
    st.markdown("Berdasarkan regresi logaritmik, **konsumsi solar 2026 diprediksi sebesar 39,84 Juta kL**.")
    
    st.info("💡 **Rumus Proyeksi Konsumsi Solar:**")
    st.latex(r"y_i = a + b \ln(x_i) \quad \Rightarrow \quad y = 32.41 + 3.82 \ln(x)")
    
    # Grafik Historis
    df_solar_hist = pd.DataFrame({
        "Tahun": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
        "Konsumsi (Juta kL)": [33.5, 33.4, 36.2, 37.8, 39.2, 39.5, 39.84]
    })
    fig_solar = px.line(df_solar_hist, x="Tahun", y="Konsumsi (Juta kL)", markers=True, 
                        title="Historis & Proyeksi Konsumsi Solar Nasional")
    fig_solar.add_vline(x=2025, line_dash="dash", line_color="red", annotation_text="Proyeksi 2026 ->")
    fig_solar.update_traces(line_color="#e63946", marker=dict(size=10))
    st.plotly_chart(fig_solar, use_container_width=True, config={'staticPlot': True})
    
    st.markdown("### 🎛️ Simulasi Komposisi FAME (Biosolar)")
    
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        st.info("""
        **Keterangan Simbol:**
        * $V_k$: Proyeksi konsumsi solar (39,84 Jt kL)
        * $V_{lokal}$: Kapasitas kilang lokal (20,1 Jt kL)
        * $\%F$: Persentase campuran FAME
        * $I_{base}$: Baseline impor eksisting (4,9 Jt kL)
        * $S$: Subsidi solar per liter (Rp5.150)
        * $G$: Gap harga FAME vs Fosil per liter (Rp3.000)
        """)
    with col_f2:
        st.latex(r"I_{baru} = \max(0, V_k(1 - \%F) - V_{lokal})")
        st.latex(r"H_{kotor} = \max(0, I_{base} - I_{baru}) \times S")
        st.latex(r"B_{fame} = \max(0, I_{base} - I_{baru}) \times G")
        st.latex(r"H_{bersih} = H_{kotor} - B_{fame}")
    
    target_fame = st.slider("Komposisi FAME (%)", min_value=30, max_value=80, value=50, step=5)
    
    # Kalkulasi Dinamis
    konsumsi_2026 = 39.84
    produksi_fosil_lokal = 20.1
    impor_baseline = 4.9
    
    vol_fame = konsumsi_2026 * (target_fame / 100)
    vol_fosil_dibutuhkan = konsumsi_2026 - vol_fame
    vol_impor = max(0, vol_fosil_dibutuhkan - produksi_fosil_lokal)
    
    impor_dihemat = max(0, impor_baseline - vol_impor)
    hemat_kotor = (impor_dihemat * 5150) / 1000 # Triliun
    beban_fame = (impor_dihemat * 3000) / 1000 # Triliun
    hemat_bersih = hemat_kotor - beban_fame
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    c1.warning(f"**Sisa Impor Solar ($I_{{baru}}$):**\n\n{vol_impor:.2f} Juta kL")
    c2.success(f"**Hemat Subsidi Kotor ($H_{{kotor}}$):**\n\nRp {hemat_kotor:.2f} T")
    c3.error(f"**Biaya FAME ($B_{{fame}}$):**\n\n- Rp {beban_fame:.2f} T")
    
    st.success(f"#### 💰 Penghematan Bersih Negara ($H_{{bersih}}$): Rp {hemat_bersih:.2f} Triliun")

# --- Sub-Poin Bensin ---
with st.container(border=True):
    st.subheader("b. Substitusi Impor Bensin (Pertalite)")
    st.markdown("Konsumsi Pertalite mencapai 29 juta kL. Fokus elektrifikasi adalah Motor dan Mobil <1400cc.")
    
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        df_bensin = pd.DataFrame({"Kategori": ["Motor", "Mobil <1400cc", "Lainnya"], "Porsi (%)": [28.6, 31.4, 40.0]})
        fig_pie = px.pie(df_bensin, values='Porsi (%)', names='Kategori', hole=0.4, title="Profil Pengguna Pertalite")
        st.plotly_chart(fig_pie, use_container_width=True, config={'staticPlot': True})
    
    with col_b2:
        vol_target_bensin = 17.4 # 8.3 + 9.1
        vol_hemat_bensin = vol_target_bensin * (target_ev / 100)
        hemat_bensin_rp = (vol_hemat_bensin * 1700) / 1000 # Triliun
        
        st.info("💡 **Rumus Hemat Subsidi Bensin:**")
        st.latex(r"\text{Hemat Bensin} = \text{Volume Dihemat} \times \text{Subsidi (Rp 1.700)}")
        st.warning(f"Volume Bensin Dihemat: **{vol_hemat_bensin:.2f} Juta kL**")
        st.success(f"#### 💰 Potensi Hemat Subsidi Bensin: Rp {hemat_bensin_rp:.2f} Triliun")

st.divider()

# ==========================================
# 2. PENGHEMATAN MASYARAKAT & PDB
# ==========================================
st.header("2️⃣ Penghematan Masyarakat & Multiplier Effect")
with st.container(border=True):
    st.markdown("Biaya energi EV jauh lebih murah. Penghematan warga ini akan dibelanjakan ke sektor lain, memicu pertumbuhan PDB.")
    
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.info("💡 **Kalkulator Multiplier ($k$):**")
        st.latex(r"k = \frac{1}{1 - c(1 - t) + m}")
        c_val = st.number_input("MPC ($c$)", value=0.779)
        t_val = st.number_input("Tax Rate ($t$)", value=0.118)
        m_val = st.number_input("Import Prop. ($m$)", value=0.209)
        k_res = 1 / (1 - c_val * (1 - t_val) + m_val)
        
    with c_m2:
        hemat_masyarakat = 139.2 * (target_ev / 100)
        pdb_naik = hemat_masyarakat * k_res
        st.warning(f"**Uang Hemat Masyarakat:**\nRp {hemat_masyarakat:.2f} Triliun")
        st.success(f"#### 📈 Potensi Tambahan PDB:\n#### Rp {pdb_naik:.2f} Triliun")

st.divider()

# ==========================================
# 3. KECUKUPAN LISTRIK
# ==========================================
st.header("3️⃣ Skenario Kecukupan Listrik")
with st.container(border=True):
    kebutuhan_twh = vol_hemat_bensin * 1.2
    surplus_twh = 36.31
    
    st.info("💡 **Konversi Energi:** Asumsi 1 Liter BBM setara dengan 1,2 kWh.")
    
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = kebutuhan_twh, title = {'text': "Kebutuhan Listrik Baru (TWh)"},
            gauge = {'axis': {'range': [None, 50]}, 'steps': [{'range': [0, surplus_twh], 'color': "lightgreen"}],
                     'threshold': {'line': {'color': "red", 'width': 4}, 'value': surplus_twh}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True, config={'staticPlot': True})
    with col_l2:
        if kebutuhan_twh <= surplus_twh:
            st.success(f"**Aman!** Beban {kebutuhan_twh:.2f} TWh di bawah surplus PLN ({surplus_twh} TWh).")
        else:
            st.error(f"**Defisit!** Butuh daya melampaui surplus PLN.")

st.divider()

# ==========================================
# 4. PENGHEMATAN DEVISA
# ==========================================
st.header("4️⃣ Penghematan Devisa Negara")
with st.container(border=True):
    barel_bensin = 93.85 * (target_ev / 100)
    barel_solar = 30.82
    tot_barel = barel_bensin + barel_solar
    
    hemat_usd_m = tot_barel * harga_minyak
    hemat_rp_devisa = (hemat_usd_m * kurs_rp) / 1_000_000
    
    c_d1, c_d2 = st.columns(2)
    c_d1.warning(f"Total Impor Dicegah: **{tot_barel:.2f} Juta Barel**")
    c_d2.success(f"#### 💱 Devisa Terselamatkan:\n#### Rp {hemat_rp_devisa:.2f} Triliun")

st.divider()

# ==========================================
# 5 & 6. INFRASTRUKTUR SPBKLU & SPKLU
# ==========================================
st.header("5️⃣ & 6️⃣ Kebutuhan Infrastruktur Pengisian Daya")
col_i1, col_i2 = st.columns(2)

with col_i1:
    with st.container(border=True):
        st.subheader("Swap Baterai Motor (SPBKLU)")
        st.info("💡 **Rumus Baterai Pool:**")
        st.latex(r"B_{pool} = D \times \frac{d}{H} \times 1.2")
        
        porsi_swap = st.slider("Pengguna Swap (%)", 0, 100, 40)
        estimasi_baterai = (182.21 + (258.04 - 182.21) * (porsi_swap/100)) * (target_ev/100)
        st.warning(f"Kebutuhan Pack Baterai:\n**{estimasi_baterai:.2f} Juta Unit**")

with col_i2:
    with st.container(border=True):
        st.subheader("Charging Mobil (SPKLU)")
        rasio_spklu = st.number_input("Rasio Mobil : 1 SPKLU", value=15)
        mobil_ev = 4.46 * (target_ev / 100)
        kebutuhan_spklu = (mobil_ev * 1_000_000) / rasio_spklu
        investasi_spklu = (kebutuhan_spklu * 250) / 1_000_000 # Asumsi 250jt
        
        st.warning(f"Kebutuhan Mesin: **{kebutuhan_spklu:,.0f} Unit**\n\nEstimasi Biaya: **Rp {investasi_spklu:.2f} Triliun**")

st.divider()

# ==========================================
# 7. POTENSI LOSS PAJAK DAERAH
# ==========================================
st.header("7️⃣ Potensi Loss Pajak Daerah")
with st.container(border=True):
    st.markdown("Elektrifikasi menurunkan penerimaan Pajak Bahan Bakar (PBBKB) dan Pajak Kendaraan (PKB) daerah.")
    
    st.info("💡 **Rumus PBBKB:**")
    st.latex(r"L_{PBBKB} = V \times P \times t")
    
    tarif_pbbkb = st.slider("Tarif PBBKB (%)", 5, 10, 10)
    loss_pbbkb = (vol_hemat_bensin * 10000 * (tarif_pbbkb / 100)) / 1000
    loss_pkb = 43.86 * (target_ev / 100)
    
    c_p1, c_p2 = st.columns(2)
    c_p1.error(f"#### 📉 Loss PBBKB:\n#### Rp {loss_pbbkb:.2f} Triliun")
    c_p2.error(f"#### 📉 Loss PKB & SWDKLLJ:\n#### Rp {loss_pkb:.2f} Triliun")
