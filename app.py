import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Makroekonomi BBM", layout="wide")

st.title("📊 Analisis Kebijakan Substitusi Impor BBM & Elektrifikasi")

# --- PENGATURAN GLOBAL (Di Sidebar / Melayang) ---
with st.sidebar:
    st.header("⚙️ Parameter Global")
    st.markdown("Atur variabel simulasi di sini:")
    target_ev_motor = st.slider("Target EV Motor (%)", 0, 100, 25, step=5)
    target_ev_mobil = st.slider("Target EV Mobil <1400cc (%)", 0, 100, 25, step=5)
    target_fame = st.slider("Komposisi FAME (Biosolar) (%)", 30, 80, 50, step=5)
    st.divider()
    harga_minyak = st.slider("Harga Minyak Dunia ($/bbl)", 50, 150, 90, step=5)
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
    
    # Grafik Historis
    df_solar_hist = pd.DataFrame({
        "Tahun": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
        "Konsumsi (Juta kL)": [33.5, 33.4, 36.2, 37.8, 39.2, 39.5, 39.84]
    })
    fig_solar = px.line(df_solar_hist, x="Tahun", y="Konsumsi (Juta kL)", markers=True, title="Historis & Proyeksi Konsumsi Solar Nasional ($y = 32.41 + 3.82 \ln(x)$)")
    fig_solar.add_vline(x=2025, line_dash="dash", line_color="red", annotation_text="Proyeksi 2026 ->")
    fig_solar.update_traces(line_color="#e63946", marker=dict(size=10))
    st.plotly_chart(fig_solar, use_container_width=True, config={'staticPlot': True})
    
    # Kalkulasi Dinamis Solar
    konsumsi_2026 = 39.84
    produksi_fosil_lokal = 20.1
    impor_baseline = 4.9
    
    vol_fame = konsumsi_2026 * (target_fame / 100)
    vol_fosil_dibutuhkan = konsumsi_2026 - vol_fame
    vol_impor = max(0, vol_fosil_dibutuhkan - produksi_fosil_lokal)
    
    impor_dihemat_solar = max(0, impor_baseline - vol_impor)
    hemat_kotor_solar = (impor_dihemat_solar * 5150) / 1000 # Triliun
    beban_fame = (impor_dihemat_solar * 3000) / 1000 # Triliun
    hemat_bersih_solar = hemat_kotor_solar - beban_fame
    
    # HTML CARDS UNTUK SOLAR
    html_cards_1a = f"""<div style="background-color:#f8fafc;padding:25px;border-radius:12px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;gap:20px;flex-wrap:wrap;"><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #f59e0b;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#b45309;margin-top:0;font-size:17px;">🛢️ Neraca Pasokan Solar 2026</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Proyeksi Konsumsi: <b>{konsumsi_2026:.2f} Jt KL</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Kebutuhan FAME ({target_fame}%): <b>{vol_fame:.2f} Jt KL</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#16a34a;font-size:16px;">✅ Fosil Tersedia: <b>{produksi_fosil_lokal:.2f} Jt KL</b></p><p style="margin:8px 0;color:#dc2626;font-size:16px;">⚠️ Sisa Impor Solar: <b>{vol_impor:.2f} Jt KL</b></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #3b82f6;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#1d4ed8;margin-top:0;font-size:17px;">💰 Dampak Keuangan Negara</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Hemat Subsidi Impor: <span style="color:#16a34a;">Rp {hemat_kotor_solar:.2f} T</span></p><p style="margin:8px 0;color:#334155;font-size:15px;">Biaya Selisih FAME: <span style="color:#dc2626;">- Rp {beban_fame:.2f} T</span></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:20px 0 8px 0;color:#334155;font-size:17px;">🛡️ Penghematan Bersih: <span style="color:#16a34a;"><b>Rp {hemat_bersih_solar:.2f} T</b></span></p></div></div>"""
    st.markdown(html_cards_1a, unsafe_allow_html=True)

    with st.expander("💡 Buka Penjelasan & Rumus Perhitungan Solar (B50)"):
        st.markdown("""
        **Dari mana angka ini berasal?**
        - **Proyeksi Konsumsi (39,84 Jt kL):** Didapat dari rumus tren regresi logaritmik konsumsi solar tahun 2020-2025.
        - **Kapasitas Fosil (20,1 Jt kL):** Kapasitas kilang eksisting ditambah *upgrade* kilang RDMP Balikpapan (1,8 Jt kL).
        - **Penghematan Bersih:** Volume impor yang tidak jadi dilakukan dikali nilai subsidi (Rp 5.150/liter), kemudian dikurangi kewajiban BPDPKS membayar selisih harga Biosolar vs Fosil (Rp 3.000/liter).
        """)
        st.latex(r"I_{baru} = \max(0, V_k(1 - \%F) - V_{lokal})")
        st.latex(r"H_{bersih} = (\Delta I \times \text{Rp } 5.150) - (\Delta I \times \text{Rp } 3.000)")

# --- Sub-Poin Bensin ---
st.subheader("b. Substitusi Impor Bensin (Pertalite)")

col_b1, col_b2 = st.columns([1, 2])
with col_b1:
    df_bensin = pd.DataFrame({"Kategori": ["Motor", "Mobil <1400cc", "Lainnya (>1400cc)"], "Porsi (%)": [28.6, 31.4, 40.0]})
    fig_pie = px.pie(df_bensin, values='Porsi (%)', names='Kategori', hole=0.4, title="Profil Pengguna Pertalite")
    st.plotly_chart(fig_pie, use_container_width=True, config={'staticPlot': True})

with col_b2:
    # Kalkulasi Dinamis Bensin
    vol_total_pertalite = 29.00
    import_awal = 14.92
    
    vol_motor_hemat = 8.3 * (target_ev_motor / 100)
    vol_mobil_hemat = 9.1 * (target_ev_mobil / 100)
    vol_hemat_bensin = vol_motor_hemat + vol_mobil_hemat
    
    sisa_import_bensin = max(0, import_awal - vol_hemat_bensin)
    sisa_konsumsi = vol_total_pertalite - vol_hemat_bensin

    # Ekonomi
    hemat_kas_negara = (vol_hemat_bensin * 1700) / 1000
    
    # Perhitungan Hemat Rakyat Asli (Ev 5x lebih hemat / 80% cut)
    biaya_bensin_awal = vol_hemat_bensin * 10 # Jt KL * Rp 10.000 = Triliun Rp
    biaya_listrik = biaya_bensin_awal / 5
    hemat_rakyat = biaya_bensin_awal - biaya_listrik 
    
    k_multiplier = 1.934
    efek_pengganda = hemat_rakyat * k_multiplier
    pdb_nominal = 23821.10
    persen_pdb_bensin = (efek_pengganda / pdb_nominal) * 100

    # Lahan
    keb_etanol = sisa_konsumsi * 0.10
    opsi_tebu = keb_etanol / 4.9
    opsi_singkong = keb_etanol / 4.07

# HTML CARDS UNTUK BENSIN
html_cards_1b = f"""<div style="background-color:#f8fafc;padding:25px;border-radius:12px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;gap:20px;flex-wrap:wrap;"><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #f59e0b;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#b45309;margin-top:0;font-size:17px;">⛽ Neraca Pertalite Nasional</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Total Konsumsi: <b>{vol_total_pertalite:.2f} Jt KL</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Import Awal: <b>{import_awal:.2f} Jt KL</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#16a34a;font-size:16px;">✅ Bensin Dihemat: <b>{vol_hemat_bensin:.2f} Jt KL</b></p><p style="margin:8px 0;color:#dc2626;font-size:16px;">⚠️ Sisa Import: <b>{sisa_import_bensin:.2f} Jt KL</b></p><p style="margin:20px 0 5px 0;color:#475569;font-size:15px;">Sisa Konsumsi: <b>{sisa_konsumsi:.2f} Jt KL</b></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #3b82f6;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#1d4ed8;margin-top:0;font-size:17px;">💰 Dampak Ekonomi Nasional</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Hemat Kas Negara: <span style="color:#16a34a;">Rp {hemat_kas_negara:.2f} T</span></p><p style="margin:8px 0;color:#334155;font-size:15px;">Hemat Rakyat: <span style="color:#16a34a;">Rp {hemat_rakyat:.2f} T</span></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#334155;font-size:15px;">Efek Pengganda (K): <span style="color:#2563eb;">+Rp {efek_pengganda:.2f} T</span></p><p style="margin:2px 0;color:#64748b;font-size:13px;">(porsi +{persen_pdb_bensin:.2f}% terhadap PDB Nominal)</p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #10b981;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#047857;margin-top:0;font-size:17px;">🌾 Kebutuhan Lahan E10</h4><p style="margin:8px 0;color:#64748b;font-size:13px;">(Untuk mem-backup 10% dari sisa konsumsi)</p><p style="margin:15px 0 8px 0;color:#334155;font-size:15px;">Kebutuhan Etanol: <b>{keb_etanol:.2f} Jt KL</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#334155;font-size:15px;">Opsi Tebu: <b>{opsi_tebu:.2f} Jt Ha</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Opsi Singkong: <b>{opsi_singkong:.2f} Jt Ha</b></p></div></div>"""
st.markdown(html_cards_1b, unsafe_allow_html=True)

# MULTIPLIER EFFECT & RUMUS BENSIN DI 1b
with st.expander("💡 Buka Detail Perhitungan Hemat Rakyat & Multiplier Effect (PDB)", expanded=True):
    st.markdown("""
    **Dari Mana Angka Hemat Rakyat Berasal?**
    * **Biaya Motor Bensin:** Asumsi efisiensi 50 km/liter dengan harga BBM Rp 10.000/liter = **Rp 200 / km**.
    * **Biaya Motor Listrik:** Tarif dasar Rp 1.444,7/kWh. Konversi uji coba (1 kWh untuk 35 km) menghasilkan biaya operasional = **Rp 41,3 / km**.
    * **Biaya Mobil Bensin:** Asumsi efisiensi 16 km/liter (Rp 10.000/liter) = **Rp 625 / km**.
    * **Biaya Mobil Listrik:** Biaya rata-rata EV operasional = **Rp 150 / km**.
    * **Kesimpulan:** Secara rata-rata, menggunakan kendaraan listrik memangkas **biaya operasional (Hemat) sebesar 5x lipat** dari bensin biasa.
    
    **Simulasi Angka:**
    * Total Biaya Bensin Awal: `{vol_hemat_bensin:.2f}` Jt kL $\\times$ Rp 10.000 = Rp {biaya_bensin_awal:.2f} Triliun.
    * Total Biaya Listrik: Rp {biaya_bensin_awal:.2f} Triliun $\div$ 5 = Rp {biaya_listrik:.2f} Triliun.
    * **Hemat Bersih Masyarakat ($E$):** Rp {biaya_bensin_awal:.2f} T $-$ Rp {biaya_listrik:.2f} T = **Rp {hemat_rakyat:.2f} Triliun**.
    """)
    st.divider()
    
    st.markdown("**Kalkulator Multiplier Keynesian ($k$):**")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        c_val = st.number_input("MPC ($c$)", value=0.779, format="%.3f")
        t_val = st.number_input("Tax Rate ($t$)", value=0.118, format="%.3f")
        m_val = st.number_input("Import Prop. ($m$)", value=0.209, format="%.3f")
        k_res = 1 / (1 - c_val * (1 - t_val) + m_val)
        
        st.info(f"**Nilai Multiplier ($k$) = {k_res:.3f}**")
    with c_m2:
        st.latex(r"k = \frac{1}{1 - c(1 - t) + m}")
        st.success(f"#### 📈 Dorongan PDB Nasional:\n#### Rp {(hemat_rakyat * k_res):.2f} Triliun\n\n$\Delta \text{PDB} = E \\times k$")

st.divider()

# ==========================================
# 2. PENGHEMATAN DEVISA & KETAHANAN EKONOMI
# ==========================================
st.header("2️⃣ Penghematan Devisa & Ketahanan Ekonomi")
with st.container(border=True):
    st.markdown("Menghentikan impor BBM (Kombinasi **Solar B50** dan **Elektrifikasi Pertalite**) menyelamatkan devisa negara dalam jumlah masif. Devisa ini menjadi bantalan tangguh untuk menekan defisit APBN 2026 dan memperkuat PDB Nominal 2025.")
    
    # Kalkulasi Agregat Devisa
    barel_solar = impor_dihemat_solar * 6.2898
    barel_bensin = vol_hemat_bensin * 6.2898
    tot_barel = barel_solar + barel_bensin
    
    hemat_usd_miliar = (tot_barel * harga_minyak) / 1000 # Dalam Miliar USD
    hemat_rp_devisa = (tot_barel * harga_minyak * kurs_rp) / 1_000_000 # Triliun Rp
    
    defisit_2026 = 689.10
    pdb_2025 = 23821.10
    
    persen_defisit_tot = (hemat_rp_devisa / defisit_2026) * 100
    persen_pdb_tot = (hemat_rp_devisa / pdb_2025) * 100
    
    # HTML CARDS UNTUK DEVISA & MAKROEKONOMI
    html_cards_2 = f"""<div style="background-color:#f8fafc;padding:25px;border-radius:12px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;gap:20px;flex-wrap:wrap;"><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #f59e0b;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#b45309;margin-top:0;font-size:17px;">🛢️ Neraca Volume Impor Dicegah</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Impor Solar: <b>{barel_solar:.2f} Jt Barel</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Impor Bensin: <b>{barel_bensin:.2f} Jt Barel</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#16a34a;font-size:16px;">✅ Total Dicegah: <b>{tot_barel:.2f} Jt Barel</b></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #3b82f6;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#1d4ed8;margin-top:0;font-size:17px;">💵 Total Devisa Terselamatkan</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Setara USD: <span style="color:#16a34a;">$ {hemat_usd_miliar:.2f} Miliar</span></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:20px 0 8px 0;color:#334155;font-size:17px;">🛡️ Total Rupiah: <span style="color:#16a34a;"><b>Rp {hemat_rp_devisa:.2f} T</b></span></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #10b981;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#047857;margin-top:0;font-size:17px;">📈 Bantalan Makroekonomi</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Menutup Defisit APBN 2026: <span style="color:#16a34a;"><b>{persen_defisit_tot:.2f} %</b></span></p><p style="margin:2px 0;color:#64748b;font-size:13px;">(Dari target defisit Rp 689,1 T)</p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#334155;font-size:15px;">Porsi terhadap PDB 2025: <span style="color:#16a34a;"><b>{persen_pdb_tot:.2f} %</b></span></p><p style="margin:2px 0;color:#64748b;font-size:13px;">(Dari PDB Nominal Rp 23.821,1 T)</p></div></div>"""
    st.markdown(html_cards_2, unsafe_allow_html=True)

    with st.expander("💡 Buka Detail Penjelasan & Rumus Ketahanan Devisa"):
        st.markdown("""
        **Bagaimana Nilai Devisa Ini Dihitung?**
        1. **Konversi ke Satuan Barel:** Di pasar global, minyak tidak dihitung dalam liter melainkan Barel. Konstanta konversinya adalah **1 kL = 6,2898 Barel**.
           - **Barel Solar** = Volume Impor Solar Dicegah $\\times$ 6,2898.
           - **Barel Bensin** = Volume Impor Bensin Dicegah $\\times$ 6,2898.
        2. **Perhitungan Devisa (Rp):** Jumlah barel dikalikan harga minyak dunia (USD) di slider, lalu dikalikan kurs Rupiah terhadap Dollar saat ini.
        3. **Rasio terhadap Defisit APBN 2026:** Membandingkan nilai devisa yang terselamatkan dengan proyeksi target defisit APBN 2026 (Rp 689,1 Triliun).
        4. **Rasio terhadap PDB Nominal 2025:** Membandingkan nilai devisa dengan total PDB Nominal 2025 (Rp 23.821,1 Triliun).
        """)
        st.latex(r"\text{Total Barel} = (V_{impor\_solar} + V_{hemat\_bensin}) \times 6,2898")
        st.latex(r"\text{Devisa (Rp)} = \text{Total Barel} \times \text{Harga Minyak (\$)} \times \text{Kurs}")
        st.latex(r"\% \text{ Defisit} = \frac{\text{Devisa (Rp)}}{\text{Defisit APBN 2026 (Rp 689,1 T)}} \times 100")
        st.latex(r"\% \text{ PDB} = \frac{\text{Devisa (Rp)}}{\text{PDB 2025 (Rp 23.821,1 T)}} \times 100")

st.divider()

# ==========================================
# 3. KECUKUPAN LISTRIK
# ==========================================
st.header("3️⃣ Skenario Kecukupan Listrik")
with st.container(border=True):
    kebutuhan_twh = vol_hemat_bensin * 1.2
    surplus_twh = 36.31
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = kebutuhan_twh, title = {'text': "Kebutuhan Listrik Baru (TWh)"},
            gauge = {'axis': {'range': [None, 50]}, 'steps': [{'range': [0, surplus_twh], 'color': "lightgreen"}],
                     'threshold': {'line': {'color': "red", 'width': 4}, 'value': surplus_twh}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True, config={'staticPlot': True})
    with col_l2:
        st.info("💡 **Konversi Energi:**\n$1 \text{ Liter BBM} = 1,2 \text{ kWh}$")
        if kebutuhan_twh <= surplus_twh:
            st.success(f"**Aman!** Beban {kebutuhan_twh:.2f} TWh di bawah surplus PLN ({surplus_twh} TWh).")
        else:
            st.error(f"**Defisit!** Butuh daya melampaui surplus PLN.")

st.divider()

# ==========================================
# 4 & 5. INFRASTRUKTUR SPBKLU & SPKLU
# ==========================================
st.header("4️⃣ & 5️⃣ Kebutuhan Infrastruktur Pengisian Daya")
col_i1, col_i2 = st.columns(2)

with col_i1:
    with st.container(border=True):
        st.subheader("Swap Baterai Motor (SPBKLU)")
        porsi_swap = st.slider("Pengguna Swap (%)", 0, 100, 40)
        # Kalkulasi infrastruktur menggunakan target_ev_motor
        estimasi_baterai = (182.21 + (258.04 - 182.21) * (porsi_swap/100)) * (target_ev_motor/100)
        st.warning(f"**Kebutuhan Pack Baterai:**\n### {estimasi_baterai:.2f} Juta Unit\n\n$B_{{pool}} = D \\times \frac{{d}}{{H}} \\times 1.2$")

with col_i2:
    with st.container(border=True):
        st.subheader("Charging Mobil (SPKLU)")
        # Kalkulasi infrastruktur menggunakan target_ev_mobil
        mobil_ev = 4.46 * (target_ev_mobil / 100)
        rasio_spklu = st.number_input("Rasio Mobil : 1 SPKLU", value=15)
        kebutuhan_spklu = (mobil_ev * 1_000_000) / rasio_spklu
        investasi_spklu = (kebutuhan_spklu * 250) / 1_000_000 # Asumsi 250jt
        st.warning(f"**Kebutuhan Mesin:**\n### {kebutuhan_spklu:,.0f} Unit\n\n**Estimasi Biaya:**\n### Rp {investasi_spklu:.2f} Triliun")

st.divider()

# ==========================================
# 6. POTENSI LOSS PAJAK DAERAH
# ==========================================
st.header("6️⃣ Potensi Loss Pajak Daerah")
with st.container(border=True):
    st.markdown("Elektrifikasi menurunkan penerimaan Pajak Bahan Bakar (PBBKB) dan Pajak Kendaraan (PKB) daerah.")
    tarif_pbbkb = st.slider("Tarif PBBKB (%)", 5, 10, 10)
    loss_pbbkb = (vol_hemat_bensin * 10000 * (tarif_pbbkb / 100)) / 1000
    
    # Loss PKB dihitung proporsional
    rata_rata_ev = (target_ev_motor + target_ev_mobil) / 200
    loss_pkb = 43.86 * rata_rata_ev
    
    c_p1, c_p2 = st.columns(2)
    c_p1.error(f"#### 📉 Loss PBBKB:\n#### Rp {loss_pbbkb:.2f} Triliun\n\n$L_{{PBBKB}} = V \\times P \\times t$")
    c_p2.error(f"#### 📉 Loss PKB & SWDKLLJ:\n#### Rp {loss_pkb:.2f} Triliun")
