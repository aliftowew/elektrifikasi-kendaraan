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
    target_ev_motor = st.slider("Target EV Motor (%)", 0, 100, 100, step=5)
    target_ev_mobil = st.slider("Target EV Mobil <1400cc (%)", 0, 100, 100, step=5)
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
    fig_solar = px.line(df_solar_hist, x="Tahun", y="Konsumsi (Juta kL)", markers=True, title="Historis & Proyeksi Konsumsi Solar Nasional")
    fig_solar.add_vline(x=2025, line_dash="dash", line_color="red", annotation_text="Proyeksi 2026 ->")
    fig_solar.update_traces(line_color="#e63946", marker=dict(size=10))
    fig_solar.update_layout(xaxis=dict(tickformat="d", dtick=1))
    st.plotly_chart(fig_solar, use_container_width=True, config={'staticPlot': True})
    
    # Kalkulasi Dinamis Solar
    konsumsi_2026 = 39.84
    produksi_fosil_lokal = 20.1
    impor_baseline = 4.9
    
    vol_fame = konsumsi_2026 * (target_fame / 100)
    vol_fosil_dibutuhkan = konsumsi_2026 - vol_fame
    vol_impor = max(0, vol_fosil_dibutuhkan - produksi_fosil_lokal)
    
    impor_dihemat_solar = max(0, impor_baseline - vol_impor)
    hemat_kotor_solar = (impor_dihemat_solar * 5150) / 1000 
    beban_fame = (impor_dihemat_solar * 3000) / 1000 
    hemat_bersih_solar = hemat_kotor_solar - beban_fame
    
    # HTML CARDS UNTUK SOLAR
    html_cards_1a = f"""<div style="background-color:#f8fafc;padding:25px;border-radius:12px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;gap:20px;flex-wrap:wrap;"><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #f59e0b;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#b45309;margin-top:0;font-size:17px;">🛢️ Neraca Pasokan Solar 2026</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Proyeksi Konsumsi: <b>{konsumsi_2026:.2f} Jt KL</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Kebutuhan FAME ({target_fame}%): <b>{vol_fame:.2f} Jt KL</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#16a34a;font-size:16px;">✅ Fosil Tersedia: <b>{produksi_fosil_lokal:.2f} Jt KL</b></p><p style="margin:8px 0;color:#dc2626;font-size:16px;">⚠️ Sisa Impor Solar: <b>{vol_impor:.2f} Jt KL</b></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #3b82f6;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#1d4ed8;margin-top:0;font-size:17px;">💰 Dampak Keuangan Negara</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Hemat Subsidi Impor: <span style="color:#16a34a;">Rp {hemat_kotor_solar:.2f} T</span></p><p style="margin:8px 0;color:#334155;font-size:15px;">Biaya Selisih FAME: <span style="color:#dc2626;">- Rp {beban_fame:.2f} T</span></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:20px 0 8px 0;color:#334155;font-size:17px;">🛡️ Penghematan Bersih: <span style="color:#16a34a;"><b>Rp {hemat_bersih_solar:.2f} T</b></span></p></div></div>"""
    st.markdown(html_cards_1a, unsafe_allow_html=True)

    with st.expander("💡 Dari Mana Angka Penghematan Solar Berasal?", expanded=True):
        st.markdown(f"""
        **Alur Simulasi Angka:**
        * **Kebutuhan Solar Fosil:** Proyeksi Konsumsi (39,84 Jt kL) dikurangi porsi campuran Biosolar (FAME). Pada komposisi {target_fame}%, dibutuhkan Fosil sebanyak {vol_fosil_dibutuhkan:.2f} Jt kL.
        * **Sisa Impor:** Kebutuhan Fosil dikurangi kapasitas kilang lokal (20,1 Jt kL). Defisitnya adalah {vol_impor:.2f} Jt kL.
        * **Volume Impor Dicegah:** Target impor lama (4,9 Jt kL) dikurangi Sisa Impor yang baru = **{impor_dihemat_solar:.2f} Jt kL**.
        * **Hemat Subsidi:** {impor_dihemat_solar:.2f} Jt kL $\\times$ Rp 5.150/liter = **Rp {hemat_kotor_solar:.2f} Triliun**.
        * **Biaya Kompensasi FAME (BPDPKS):** {impor_dihemat_solar:.2f} Jt kL $\\times$ Selisih Harga Rp 3.000/liter = **Rp {beban_fame:.2f} Triliun**.
        * **Kesimpulan Penghematan Bersih:** Rp {hemat_kotor_solar:.2f} T $-$ Rp {beban_fame:.2f} T = **Rp {hemat_bersih_solar:.2f} Triliun**.
        """)

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
    biaya_bensin_awal = vol_hemat_bensin * 10 
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

# MULTIPLIER EFFECT 
with st.expander("💡 Dari Mana Angka Hemat Rakyat & Multiplier (PDB) Berasal?", expanded=True):
    st.markdown(f"""
    **1. Analisis Biaya Kendaraan (Hemat Rakyat):**
    * **Biaya Motor Bensin:** Asumsi efisiensi 50 km/liter dengan harga BBM Rp 10.000/liter = **Rp 200 / km**.
    * **Biaya Motor Listrik:** Tarif dasar Rp 1.444,7/kWh. Penggunaan riil 1 kWh dapat menempuh 35 km, sehingga biaya operasional = **Rp 41,3 / km**.
    * **Biaya Mobil Bensin:** Asumsi efisiensi 16 km/liter (Rp 10.000/liter) = **Rp 625 / km**.
    * **Biaya Mobil Listrik:** Biaya rata-rata operasional EV = **Rp 150 / km**.
    * **Kesimpulan:** Secara rata-rata, menggunakan kendaraan listrik memangkas **biaya operasional (Hemat) sebesar 5x lipat** dari bensin biasa.
    
    **Simulasi Angka Hemat Rakyat:**
    * Total Biaya Bensin Awal: {vol_hemat_bensin:.2f} Juta kL $\\times$ Rp 10.000 = **Rp {biaya_bensin_awal:.2f} Triliun**.
    * Total Biaya Listrik: Rp {biaya_bensin_awal:.2f} Triliun $\\div$ 5 = **Rp {biaya_listrik:.2f} Triliun**.
    * **Hemat Bersih Masyarakat:** Rp {biaya_bensin_awal:.2f} T $-$ Rp {biaya_listrik:.2f} T = **Rp {hemat_rakyat:.2f} Triliun**.
    """)
    st.divider()
    
    st.markdown("**2. Kalkulator Efek Pengganda (Multiplier Keynesian):**")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        c_val = st.number_input("MPC (Kecenderungan Konsumsi)", value=0.779, format="%.3f")
        t_val = st.number_input("Tax Rate (Rasio Pajak)", value=0.118, format="%.3f")
        m_val = st.number_input("Import Propensity (Proporsi Impor)", value=0.209, format="%.3f")
        k_res = 1 / (1 - c_val * (1 - t_val) + m_val)
        
        st.info(f"**Nilai Multiplier (k) yang Dihasilkan = {k_res:.3f}**")
    with c_m2:
        st.markdown(f"""
        **Alur Simulasi PDB:**
        * Uang yang dihemat masyarakat (Rp {hemat_rakyat:.2f} T) tidak diam di tabungan, melainkan dibelanjakan ke sektor riil (makanan, jasa, dll).
        * Belanja ini memicu siklus ekonomi lanjutan yang diukur dengan rumus: `Nilai Hemat Rakyat dikali Konstanta Multiplier`.
        """)
        st.success(f"""#### 📈 Dorongan PDB Nasional:
#### Rp {(hemat_rakyat * k_res):.2f} Triliun""")

st.divider()

# ==========================================
# 2. PENGHEMATAN DEVISA & KETAHANAN EKONOMI
# ==========================================
st.header("2️⃣ Penghematan Devisa & Ketahanan Ekonomi")
with st.container(border=True):
    st.markdown("Menghentikan impor BBM menyelamatkan devisa negara dalam jumlah masif. Devisa ini menjadi bantalan tangguh untuk menekan defisit APBN 2026 dan memperkuat PDB Nasional.")
    
    barel_solar = impor_dihemat_solar * 6.2898
    barel_bensin = vol_hemat_bensin * 6.2898
    tot_barel = barel_solar + barel_bensin
    
    hemat_usd_miliar = (tot_barel * harga_minyak) / 1000 
    hemat_rp_devisa = (tot_barel * harga_minyak * kurs_rp) / 1_000_000 
    
    defisit_2026 = 689.10
    pdb_2025 = 23821.10
    
    persen_defisit_tot = (hemat_rp_devisa / defisit_2026) * 100
    persen_pdb_tot = (hemat_rp_devisa / pdb_2025) * 100
    
    html_cards_2 = f"""<div style="background-color:#f8fafc;padding:25px;border-radius:12px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;gap:20px;flex-wrap:wrap;"><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #f59e0b;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#b45309;margin-top:0;font-size:17px;">🛢️ Neraca Volume Impor Dicegah</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Impor Solar: <b>{barel_solar:.2f} Jt Barel</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Impor Bensin: <b>{barel_bensin:.2f} Jt Barel</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#16a34a;font-size:16px;">✅ Total Dicegah: <b>{tot_barel:.2f} Jt Barel</b></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #3b82f6;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#1d4ed8;margin-top:0;font-size:17px;">💵 Total Devisa Terselamatkan</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Setara USD: <span style="color:#16a34a;">$ {hemat_usd_miliar:.2f} Miliar</span></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:20px 0 8px 0;color:#334155;font-size:17px;">🛡️ Total Rupiah: <span style="color:#16a34a;"><b>Rp {hemat_rp_devisa:.2f} T</b></span></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #10b981;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#047857;margin-top:0;font-size:17px;">📈 Bantalan Makroekonomi</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Menutup Defisit APBN: <span style="color:#16a34a;"><b>{persen_defisit_tot:.2f} %</b></span></p><p style="margin:2px 0;color:#64748b;font-size:13px;">(Dari target defisit 2026 Rp 689,1 T)</p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#334155;font-size:15px;">Porsi terhadap PDB: <span style="color:#16a34a;"><b>{persen_pdb_tot:.2f} %</b></span></p><p style="margin:2px 0;color:#64748b;font-size:13px;">(Dari PDB Nominal 2025 Rp 23.821,1 T)</p></div></div>"""
    st.markdown(html_cards_2, unsafe_allow_html=True)

    with st.expander("💡 Dari Mana Angka Ketahanan Devisa Berasal?", expanded=True):
        st.markdown(f"""
        **Alur Simulasi Angka:**
        * **Konversi ke Satuan Barel:** Di pasar global, minyak dihitung dalam Barel. Konstanta konversinya adalah 1 kL setara 6,2898 Barel.
            * Total Solar dan Bensin yang tidak jadi diimpor dikalikan konstanta tersebut, menghasilkan **{tot_barel:.2f} Juta Barel** minyak yang tidak perlu kita beli dari luar negeri.
        * **Perhitungan Devisa Negara:** {tot_barel:.2f} Juta Barel dikalikan dengan Harga Minyak (USD {harga_minyak}/barel) dan Kurs (Rp {kurs_rp}/USD). Hasilnya adalah nilai Rupiah yang berhasil ditahan di dalam negeri (**Rp {hemat_rp_devisa:.2f} Triliun**).
        * **Rasio terhadap Defisit:** Uang devisa yang diselamatkan ini dibandingkan dengan proyeksi defisit APBN pemerintah, membuktikan bahwa kebijakan ini bisa menambal celah utang negara secara signifikan.
        """)

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
        st.info("💡 **Konversi Energi:**\n$1 \\text{{ Liter BBM}} = 1,2 \\text{{ kWh}}$")
        if kebutuhan_twh <= surplus_twh:
            st.success(f"**Aman!** Beban {kebutuhan_twh:.2f} TWh di bawah surplus PLN ({surplus_twh} TWh).")
        else:
            st.error(f"**Defisit!** Butuh daya melampaui surplus PLN.")
            
    with st.expander("💡 Dari Mana Angka Skenario Listrik Berasal?", expanded=True):
        st.markdown(f"""
        **Alur Simulasi Angka:**
        * **Kebutuhan Listrik Tambahan:** Berasal dari total bensin yang dihemat ({vol_hemat_bensin:.2f} Juta kL atau Miliar Liter) dikalikan dengan faktor konversi 1,2 kWh per liter. Hasilnya adalah beban tambahan **{kebutuhan_twh:.2f} TWh** per tahun.
        * **Surplus Listrik Nasional (Kapasitas Menganggur):** Berdasarkan data PLN, kapasitas produksi listrik nasional adalah 354 TWh, sementara yang terpakai hanya 317,69 TWh. 
        * **Kesimpulan:** Selisihnya menciptakan cadangan tenaga sebesar **36,31 TWh**, yang jauh lebih besar dari beban baru kendaraan listrik. Tidak perlu membangun pembangkit listrik baru secara mendadak.
        """)

st.divider()

# ==========================================
# 4. KEBUTUHAN INFRASTRUKTUR & SUBSIDI
# ==========================================
st.header("4️⃣ Kebutuhan Infrastruktur, Transisi & Subsidi")
col_i1, col_i2, col_i3 = st.columns(3)

with col_i1:
    with st.container(border=True):
        st.subheader("Transisi Motor & Biaya Subsidi")
        # Parameter Baru sesuai instruksi
        porsi_konversi = st.slider("Porsi Konversi Bengkel (%)", 0, 100, 70, step=5)
        porsi_baru = 100 - porsi_konversi
        
        col_s1, col_s2 = st.columns(2)
        subsidi_konv = col_s1.number_input("Subsidi Konversi (Juta Rp/unit)", value=10.0, step=1.0)
        subsidi_baru = col_s2.number_input("Subsidi Unit Baru (Juta Rp/unit)", value=7.0, step=1.0)
        
        # Kalkulasi
        total_motor_ev = 145.24 * (target_ev_motor / 100)
        vol_konversi = total_motor_ev * (porsi_konversi / 100)
        vol_baru = total_motor_ev * (porsi_baru / 100)
        
        biaya_subsidi_konv = vol_konversi * subsidi_konv
        biaya_subsidi_baru = vol_baru * subsidi_baru
        total_biaya_subsidi = biaya_subsidi_konv + biaya_subsidi_baru
        
        st.warning(f"""**Volume Target EV Motor:** {total_motor_ev:.2f} Juta Unit
- **Jalur Konversi:** {vol_konversi:.2f} Juta unit
- **Jalur Beli Baru:** {vol_baru:.2f} Juta unit""")
        st.success(f"#### 💰 Total Biaya Subsidi Pemerintah:\n#### Rp {total_biaya_subsidi:.2f} Triliun")

with col_i2:
    with st.container(border=True):
        st.subheader("Kebutuhan Bengkel & Swap Baterai")
        # Parameter Bengkel
        lama_proyek = st.slider("Lama Pengerjaan Proyek (Tahun)", 1, 10, 4)
        
        # Asumsi 1 line: 730 hingga 3650 motor per tahun
        line_bengkel_min = (vol_konversi * 1_000_000) / (3650 * lama_proyek)
        line_bengkel_max = (vol_konversi * 1_000_000) / (730 * lama_proyek)
        
        st.warning(f"**Kebutuhan Line Bengkel:**\n### {line_bengkel_min:,.0f} - {line_bengkel_max:,.0f} Line")
        st.divider()
        
        # Swap Baterai
        porsi_swap = st.slider("Pengguna Swap (%)", 0, 100, 40)
        estimasi_baterai = (182.21 + (258.04 - 182.21) * (porsi_swap/100)) * (target_ev_motor/100)
        st.warning(f"**Kebutuhan Pack Baterai:**\n### {estimasi_baterai:.2f} Juta Unit")

with col_i3:
    with st.container(border=True):
        st.subheader("Mesin Charging Mobil (SPKLU)")
        mobil_ev = 4.46 * (target_ev_mobil / 100)
        rasio_spklu = st.number_input("Rasio Mobil : 1 SPKLU", value=15)
        kebutuhan_spklu = (mobil_ev * 1_000_000) / rasio_spklu
        investasi_spklu = (kebutuhan_spklu * 250) / 1_000_000 # Asumsi 250jt
        
        st.warning(f"""**Kebutuhan Mesin:**
### {kebutuhan_spklu:,.0f} Unit

**Estimasi Biaya Infrastruktur:**
### Rp {investasi_spklu:.2f} Triliun""")

with st.expander("💡 Dari Mana Angka Infrastruktur & Subsidi Berasal?", expanded=True):
    st.markdown(f"""
    **Alur Simulasi Angka:**
    * **Jalur Transisi Motor:** Total target populasi motor listrik yang dituju ({total_motor_ev:.2f} Juta unit) dipecah menjadi dua jalur masuk. Ada yang mengubah mesinnya di bengkel (Konversi {porsi_konversi}%), dan ada yang membeli unit keluaran pabrik (Baru {porsi_baru}%).
    * **Total Biaya Subsidi Pemerintah:** - Anggaran Konversi: {vol_konversi:.2f} Juta unit $\\times$ Rp {subsidi_konv} Juta = **Rp {biaya_subsidi_konv:.2f} Triliun**.
      - Anggaran Unit Baru: {vol_baru:.2f} Juta unit $\\times$ Rp {subsidi_baru} Juta = **Rp {biaya_subsidi_baru:.2f} Triliun**.
      - Total keduanya digabung menghasilkan **Rp {total_biaya_subsidi:.2f} Triliun**.
    * **Kebutuhan Line Bengkel:** - Satu jalur pengerjaan (*line*) di bengkel diasumsikan mampu mengkonversi 2 hingga 10 motor per hari, atau setara dengan penyelesaian 730 hingga 3.650 motor per tahun.
      - Agar seluruh {vol_konversi:.2f} Juta motor konversi bisa selesai dalam waktu pengerjaan proyek **{lama_proyek} tahun**, maka jumlah motor tersebut dibagi dengan total kapasitas produksi per *line*. Hasilnya adalah kebutuhan pembukaan bengkel baru di seluruh wilayah.
    * **Swap Baterai:** Menggunakan rasio pemakaian harian pengendara, dikalikan dengan durasi antrean pengisian (charging rate), serta ditambahkan 20% stok *buffer* untuk mencegah kelangkaan baterai di jam pulang kerja (*peak hour*).
    * **Mesin Charging Mobil (SPKLU):** Jumlah mobil listrik diproyeksikan dibagi dengan rasio kepadatan ideal per mesin ({rasio_spklu}:1), lalu dikalikan dengan biaya investasi standar per unit SPKLU sebesar Rp 250 Juta.
    """)

st.divider()

# ==========================================
# 5. POTENSI LOSS PAJAK DAERAH
# ==========================================
st.header("5️⃣ Potensi Loss Pajak Daerah")
with st.container(border=True):
    st.markdown("Elektrifikasi menurunkan penerimaan Pajak Bahan Bakar Kendaraan Bermotor (PBBKB) dan Pajak Kendaraan Bermotor (PKB) daerah.")
    
    tarif_pbbkb = st.slider("Tarif PBBKB (%)", 5, 10, 10)
    loss_pbbkb = (vol_hemat_bensin * 10000 * (tarif_pbbkb / 100)) / 1000
    
    rata_rata_ev = (target_ev_motor + target_ev_mobil) / 200
    loss_pkb = 43.86 * rata_rata_ev
    
    c_p1, c_p2 = st.columns(2)
    c_p1.error(f"""#### 📉 Loss PBBKB:
#### Rp {loss_pbbkb:.2f} Triliun""")
    
    c_p2.error(f"""#### 📉 Loss PKB & SWDKLLJ:
#### Rp {loss_pkb:.2f} Triliun""")

with st.expander("💡 Dari Mana Angka Loss Pajak Berasal?", expanded=True):
    st.markdown(f"""
    **Alur Simulasi Angka:**
    1. **Pajak Bahan Bakar (PBBKB):** Volume Pertalite yang dihemat ({vol_hemat_bensin:.2f} Juta kL atau Miliar Liter) adalah bensin yang tidak lagi dibeli oleh masyarakat. Angka ini dikalikan dengan harga bensin (Rp 10.000/liter), lalu diambil {tarif_pbbkb}% nya sebagai nilai Pendapatan Asli Daerah yang hilang.
    2. **Pajak Kendaraan (PKB & SWDKLLJ):** Elektrifikasi, apalagi jika pemerintah memberikan insentif bebas pajak tahunan bagi EV, akan menghilangkan pemasukan dari perpanjangan STNK. Jika 100% populasi beralih ke EV, potensi kerugian maksimalnya mencapai Rp 43,86 Triliun. Nilai aktual (*Loss PKB*) ini akan terus menyesuaikan persentase target adopsi EV dari penggeser (*slider*) di atas.
    """)
