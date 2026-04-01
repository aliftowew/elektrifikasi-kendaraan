import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Makroekonomi BBM", layout="wide")

# CSS HACK: Sembunyikan angka di titik slider agar Range Slider terlihat natural
st.markdown("""
<style>
    div[data-testid="stThumbValue"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# --- SINKRONISASI SESSION STATE (Untuk Widget Double di Sidebar & Main) ---
def sync_var(source_key, target_key):
    st.session_state[target_key] = st.session_state[source_key]

defaults = {
    'porsi_konv': 70, 'sub_konv': 10.0, 'sub_baru': 7.0,
    'lama_proyek': 4, 'porsi_tipe_a': 16, 'porsi_swap': 40,
    'rasio_spklu': 15, 'batas_spklu': (55, 83),
    'h_med': 150, 'h_fast': 350, 'h_ultra': 500,
    'k_motor': 1.6, 'h_motor': 15.0, 'k_bat': 2.0, 'h_bat': 5.0,
    'tarif_pbbkb': 10, 'pkb_mobil': 2.50, 'pkb_motor': 0.25
}

for k, v in defaults.items():
    if f"main_{k}" not in st.session_state: st.session_state[f"main_{k}"] = v
    if f"sb_{k}" not in st.session_state: st.session_state[f"sb_{k}"] = v

st.title("📊 Analisis Kebijakan Substitusi Impor BBM & Elektrifikasi")

# --- PENGATURAN GLOBAL (Di Sidebar) ---
with st.sidebar:
    st.header("⚙️ Parameter Global")
    st.markdown("Atur variabel simulasi di sini:")
    target_ev_motor = st.slider("🏍️ Target EV Motor (%)", 0, 100, 100, step=5)
    target_ev_mobil = st.slider("🚗 Target EV Mobil <1400cc (%)", 0, 100, 100, step=5)
    target_fame = st.slider("🌱 Komposisi FAME (Biosolar) (%)", 30, 80, 50, step=5)
    st.divider()
    harga_minyak = st.slider("🛢️ Harga Minyak Dunia ($/bbl)", 50, 150, 90, step=5)
    kurs_rp = st.slider("💱 Kurs Rupiah (Rp/USD)", 14000, 18000, 16896, step=100)
    
    st.divider()
    st.header("🎛️ Navigasi Detail")
    
    with st.expander("🛠️ Subsidi & Infrastruktur", expanded=False):
        st.slider("Porsi Konversi (%)", 0, 100, key="sb_porsi_konv", on_change=sync_var, args=("sb_porsi_konv", "main_porsi_konv"))
        st.number_input("Sub. Konversi (Jt)", step=1.0, key="sb_sub_konv", on_change=sync_var, args=("sb_sub_konv", "main_sub_konv"))
        st.number_input("Sub. Baru (Jt)", step=1.0, key="sb_sub_baru", on_change=sync_var, args=("sb_sub_baru", "main_sub_baru"))
        st.slider("Lama Proyek (Thn)", 1, 10, key="sb_lama_proyek", on_change=sync_var, args=("sb_lama_proyek", "main_lama_proyek"))
        st.slider("Porsi Bengkel A (%)", 0, 100, key="sb_porsi_tipe_a", on_change=sync_var, args=("sb_porsi_tipe_a", "main_porsi_tipe_a"))
        st.slider("Pengguna Swap (%)", 0, 100, key="sb_porsi_swap", on_change=sync_var, args=("sb_porsi_swap", "main_porsi_swap"))
        st.number_input("Rasio Mobil:SPKLU", key="sb_rasio_spklu", on_change=sync_var, args=("sb_rasio_spklu", "main_rasio_spklu"))
        st.slider("Porsi Mesin (%)", 0, 100, key="sb_batas_spklu", on_change=sync_var, args=("sb_batas_spklu", "main_batas_spklu"))
        st.number_input("Harga Med (Jt)", key="sb_h_med", on_change=sync_var, args=("sb_h_med", "main_h_med"))
        st.number_input("Harga Fast (Jt)", key="sb_h_fast", on_change=sync_var, args=("sb_h_fast", "main_h_fast"))
        st.number_input("Harga Ultra (Jt)", key="sb_h_ultra", on_change=sync_var, args=("sb_h_ultra", "main_h_ultra"))

    with st.expander("🏭 Supply Chain", expanded=False):
        st.slider("Kapasitas Motor (Jt)", 0.5, 10.0, step=0.1, key="sb_k_motor", on_change=sync_var, args=("sb_k_motor", "main_k_motor"))
        st.number_input("Impor Motor (Jt Rp)", step=1.0, key="sb_h_motor", on_change=sync_var, args=("sb_h_motor", "main_h_motor"))
        st.slider("Kapasitas Bat. (Jt)", 0.1, 100.0, step=0.1, key="sb_k_bat", on_change=sync_var, args=("sb_k_bat", "main_k_bat"))
        st.number_input("Impor Baterai (Jt Rp)", step=1.0, key="sb_h_bat", on_change=sync_var, args=("sb_h_bat", "main_h_bat"))

    with st.expander("📉 Pajak Daerah", expanded=False):
        st.slider("Tarif PBBKB (%)", 5, 10, key="sb_tarif_pbbkb", on_change=sync_var, args=("sb_tarif_pbbkb", "main_tarif_pbbkb"))
        st.number_input("PKB Mobil (Jt)", min_value=1.85, max_value=3.32, step=0.01, key="sb_pkb_mobil", on_change=sync_var, args=("sb_pkb_mobil", "main_pkb_mobil"))
        st.number_input("PKB Motor (Jt)", min_value=0.10, max_value=0.50, step=0.01, key="sb_pkb_motor", on_change=sync_var, args=("sb_pkb_motor", "main_pkb_motor"))

st.divider()

# ==========================================
# 1. PENGHEMATAN PEMERINTAH (SOLAR & BENSIN)
# ==========================================
st.header("1️⃣ Penghematan Pemerintah (Subsidi BBM)")

# --- Sub-Poin Solar ---
with st.container(border=True):
    st.subheader("a. Substitusi Impor Solar & Dinamika FAME")
    st.markdown("Berdasarkan regresi logaritmik, **konsumsi solar 2026 diprediksi sebesar 39,84 Juta kL**.")
    
    df_solar_hist = pd.DataFrame({
        "Tahun": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
        "Konsumsi (Juta kL)": [33.5, 33.4, 36.2, 37.8, 39.2, 39.5, 39.84]
    })
    fig_solar = px.line(df_solar_hist, x="Tahun", y="Konsumsi (Juta kL)", markers=True, title="Historis & Proyeksi Konsumsi Solar Nasional")
    fig_solar.add_vline(x=2025, line_dash="dash", line_color="red", annotation_text="Proyeksi 2026 ->")
    fig_solar.update_traces(line_color="#e63946", marker=dict(size=10))
    fig_solar.update_layout(xaxis=dict(tickformat="d", dtick=1))
    st.plotly_chart(fig_solar, use_container_width=True, config={'staticPlot': True})
    
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
    
    html_cards_1a = f"""<div style="background-color:#f8fafc;padding:25px;border-radius:12px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;gap:20px;flex-wrap:wrap;"><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #f59e0b;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#b45309;margin-top:0;font-size:17px;">🛢️ Neraca Pasokan Solar 2026</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Proyeksi Konsumsi: <b>{konsumsi_2026:.2f} Jt KL</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Kebutuhan FAME ({target_fame}%): <b>{vol_fame:.2f} Jt KL</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#16a34a;font-size:16px;">✅ Fosil Tersedia: <b>{produksi_fosil_lokal:.2f} Jt KL</b></p><p style="margin:8px 0;color:#dc2626;font-size:16px;">⚠️ Sisa Impor Solar: <b>{vol_impor:.2f} Jt KL</b></p></div><div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #3b82f6;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#1d4ed8;margin-top:0;font-size:17px;">💰 Dampak Keuangan Negara</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Hemat Subsidi Impor: <span style="color:#16a34a;">Rp {hemat_kotor_solar:.2f} T</span></p><p style="margin:8px 0;color:#334155;font-size:15px;">Biaya Selisih FAME: <span style="color:#dc2626;">- Rp {beban_fame:.2f} T</span></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:20px 0 8px 0;color:#334155;font-size:17px;">🛡️ Penghematan Bersih: <span style="color:#16a34a;"><b>Rp {hemat_bersih_solar:.2f} T</b></span></p></div></div>"""
    st.markdown(html_cards_1a, unsafe_allow_html=True)

    with st.expander("💡 Dari Mana Angka Penghematan Solar Berasal?", expanded=True):
        st.markdown(f"""
        **Alur Simulasi Angka:**
        * **Kebutuhan Solar Fosil:** Proyeksi Konsumsi (39,84 Jt kL) dikurangi porsi campuran Biosolar (FAME). Pada komposisi {target_fame}%, dibutuhkan Fosil sebanyak {vol_fosil_dibutuhkan:.2f} Jt kL.
        * **Sisa Impor:** Kebutuhan Fosil dikurangi kapasitas kilang lokal (20,10 Jt kL). Defisitnya adalah {vol_impor:.2f} Jt kL.
        * **Volume Impor Dicegah:** Target impor lama (4,90 Jt kL) dikurangi Sisa Impor yang baru = **{impor_dihemat_solar:.2f} Jt kL**.
        * **Hemat Subsidi:** {impor_dihemat_solar:.2f} Jt kL × Rp 5.150/liter = **Rp {hemat_kotor_solar:.2f} Triliun**.
        * **Biaya Kompensasi FAME (BPDPKS):** {impor_dihemat_solar:.2f} Jt kL × Selisih Harga Rp 3.000/liter = **Rp {beban_fame:.2f} Triliun**.
        * **Kesimpulan Penghematan Bersih:** Rp {hemat_kotor_solar:.2f} T − Rp {beban_fame:.2f} T = **Rp {hemat_bersih_solar:.2f} Triliun**.
        """)

# --- Sub-Poin Bensin ---
st.subheader("b. Substitusi Impor Bensin (Pertalite)")

col_b1, col_b2 = st.columns([1, 1])
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

    st.markdown("<br><br>", unsafe_allow_html=True) # Spacer agar sejajar dengan donat
    html_card_neraca = f"""<div style="background:white;padding:20px;border-radius:10px;border-top:4px solid #f59e0b;box-shadow:0 2px 4px rgba(0,0,0,0.05);height:100%;"><h4 style="color:#b45309;margin-top:0;font-size:17px;">⛽ Neraca Pertalite Nasional</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Total Konsumsi: <b>{vol_total_pertalite:.2f} Jt KL</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Import Awal: <b>{import_awal:.2f} Jt KL</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#16a34a;font-size:16px;">✅ Bensin Dihemat: <b>{vol_hemat_bensin:.2f} Jt KL</b></p><p style="margin:8px 0;color:#dc2626;font-size:16px;">⚠️ Sisa Import: <b>{sisa_import_bensin:.2f} Jt KL</b></p><p style="margin:20px 0 5px 0;color:#475569;font-size:15px;">Sisa Konsumsi: <b>{sisa_konsumsi:.2f} Jt KL</b></p></div>"""
    st.markdown(html_card_neraca, unsafe_allow_html=True)

# Lanjut ke hitungan Ekonomi & Lahan di bawah kolom
hemat_kas_negara = (vol_hemat_bensin * 1700) / 1000
biaya_bensin_awal = vol_hemat_bensin * 10 
biaya_listrik = biaya_bensin_awal / 5
hemat_rakyat = biaya_bensin_awal - biaya_listrik 

k_multiplier = 1.934
efek_pengganda = hemat_rakyat * k_multiplier
pdb_nominal = 23821.10
persen_pdb_bensin = (efek_pengganda / pdb_nominal) * 100

keb_etanol = sisa_konsumsi * 0.10
opsi_tebu = keb_etanol / 4.9
opsi_singkong = keb_etanol / 4.07

html_card_eko_lahan = f"""<div style="background-color:#f8fafc;padding:25px;border-radius:12px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;gap:20px;flex-wrap:wrap;">
<div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #3b82f6;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#1d4ed8;margin-top:0;font-size:17px;">💰 Dampak Ekonomi Nasional</h4><p style="margin:8px 0;color:#334155;font-size:15px;">Hemat Kas Negara: <span style="color:#16a34a;">Rp {hemat_kas_negara:.2f} T</span></p><p style="margin:8px 0;color:#334155;font-size:15px;">Hemat Rakyat: <span style="color:#16a34a;">Rp {hemat_rakyat:.2f} T</span></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#334155;font-size:15px;">Efek Pengganda (K): <span style="color:#2563eb;">+Rp {efek_pengganda:.2f} T</span></p><p style="margin:2px 0;color:#64748b;font-size:13px;">(porsi +{persen_pdb_bensin:.2f}% terhadap PDB Nominal)</p></div>
<div style="flex:1;min-width:280px;background:white;padding:20px;border-radius:10px;border-top:4px solid #10b981;box-shadow:0 2px 4px rgba(0,0,0,0.05);"><h4 style="color:#047857;margin-top:0;font-size:17px;">🌾 Kebutuhan Lahan E10</h4><p style="margin:8px 0;color:#64748b;font-size:13px;">(Untuk mem-backup 10% dari sisa konsumsi)</p><p style="margin:15px 0 8px 0;color:#334155;font-size:15px;">Kebutuhan Etanol: <b>{keb_etanol:.2f} Jt KL</b></p><hr style="border:none;border-top:1px dashed #cbd5e1;margin:15px 0;"><p style="margin:8px 0;color:#334155;font-size:15px;">Opsi Tebu: <b>{opsi_tebu:.2f} Jt Ha</b></p><p style="margin:8px 0;color:#334155;font-size:15px;">Opsi Singkong: <b>{opsi_singkong:.2f} Jt Ha</b></p></div>
</div>"""
st.markdown(html_card_eko_lahan, unsafe_allow_html=True)

# MULTIPLIER EFFECT 
with st.expander("💡 Dari Mana Angka Hemat Rakyat & Multiplier (PDB) Berasal?", expanded=True):
    st.markdown(f"""
    **1. Analisis Biaya Kendaraan (Hemat Rakyat):**
    * **Biaya Motor Bensin:** Asumsi efisiensi 50 km/liter dengan harga BBM Rp 10.000/liter = **Rp 200 / km**.
    * **Biaya Motor Listrik:** Tarif dasar Rp 1.444,7/kWh. Konversi uji coba (1 kWh untuk 35 km) menghasilkan biaya operasional = **Rp 41,3 / km**.
    * **Biaya Mobil Bensin:** Asumsi efisiensi 16 km/liter (Rp 10.000/liter) = **Rp 625 / km**.
    * **Biaya Mobil Listrik:** Biaya rata-rata operasional EV = **Rp 150 / km**.
    * **Kesimpulan:** Secara rata-rata, menggunakan kendaraan listrik memangkas **biaya operasional (Hemat) sebesar 5x lipat** dari bensin biasa.
    
    **Simulasi Angka Hemat Rakyat:**
    * Total Biaya Bensin Awal: {vol_hemat_bensin:.2f} Juta kL × Rp 10.000 = **Rp {biaya_bensin_awal:.2f} Triliun**.
    * Total Biaya Listrik: Rp {biaya_bensin_awal:.2f} Triliun ÷ 5 = **Rp {biaya_listrik:.2f} Triliun**.
    * **Hemat Bersih Masyarakat (E):** Rp {biaya_bensin_awal:.2f} T − Rp {biaya_listrik:.2f} T = **Rp {hemat_rakyat:.2f} Triliun**.
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
        * Belanja ini memicu siklus ekonomi lanjutan yang diukur dengan rumus: `Nilai Hemat Rakyat dikalikan Konstanta Multiplier`.
        * **Perhitungan PDB:** Rp {hemat_rakyat:.2f} Triliun × {k_res:.3f} = **Rp {(hemat_rakyat * k_res):.2f} Triliun**.
        """)

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
            * **Total Barel Dicegah:** (Impor Solar {impor_dihemat_solar:.2f} Jt kL + Impor Bensin {vol_hemat_bensin:.2f} Jt kL) × 6,2898 = **{tot_barel:.2f} Juta Barel**.
        * **Perhitungan Devisa Negara:** {tot_barel:.2f} Juta Barel × Harga Minyak (USD {harga_minyak}/barel) × Kurs (Rp {kurs_rp}/USD) = **Rp {hemat_rp_devisa:.2f} Triliun**.
        * **Rasio terhadap Defisit:** Rp {hemat_rp_devisa:.2f} T ÷ Target Defisit APBN (Rp 689,1 T) = **{persen_defisit_tot:.2f}%**.
        * **Rasio terhadap PDB Nominal:** Rp {hemat_rp_devisa:.2f} T ÷ PDB 2025 (Rp 23.821,1 T) = **{persen_pdb_tot:.2f}%**.
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
        st.info("💡 **Konversi Energi:**\n1 Liter BBM setara dengan 1,2 kWh")
        if kebutuhan_twh <= surplus_twh:
            st.success(f"**Aman!** Beban {kebutuhan_twh:.2f} TWh di bawah surplus PLN ({surplus_twh} TWh).")
        else:
            st.error(f"**Defisit!** Butuh daya melampaui surplus PLN.")
            
    with st.expander("💡 Dari Mana Angka Skenario Listrik Berasal?", expanded=True):
        st.markdown(f"""
        **Alur Simulasi Angka:**
        * **Kebutuhan Listrik Tambahan:** Berasal dari total bensin yang dihemat ({vol_hemat_bensin:.2f} Juta kL atau Miliar Liter) dikalikan dengan faktor konversi 1,2 kWh per liter. Hasilnya adalah beban tambahan **{kebutuhan_twh:.2f} TWh** per tahun.
        * **Surplus Listrik Nasional (Kapasitas Menganggur):** Berdasarkan data PLN, kapasitas produksi listrik nasional adalah 354 TWh, sementara yang terpakai hanya 317,69 TWh. 
        * **Kesimpulan:** Selisihnya menciptakan cadangan tenaga sebesar 354 − 317,69 = **36,31 TWh**, yang jauh lebih besar dari beban baru kendaraan listrik. Tidak perlu membangun pembangkit listrik baru secara mendadak.
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
        porsi_konversi = st.slider("Porsi Konversi Bengkel (%)", 0, 100, key="main_porsi_konv", on_change=sync_var, args=("main_porsi_konv", "sb_porsi_konv"))
        porsi_baru = 100 - porsi_konversi
        
        col_s1, col_s2 = st.columns(2)
        subsidi_konv = col_s1.number_input("Subsidi Konversi (Juta Rp)", step=1.0, key="main_sub_konv", on_change=sync_var, args=("main_sub_konv", "sb_sub_konv"))
        subsidi_baru = col_s2.number_input("Subsidi Unit Baru (Juta Rp)", step=1.0, key="main_sub_baru", on_change=sync_var, args=("main_sub_baru", "sb_sub_baru"))
        
        # Kalkulasi Total Unit
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

    st.divider()
    
    with st.container(border=True):
        st.subheader("Swap Baterai Motor")
        porsi_swap = st.slider("Pengguna Swap (%)", 0, 100, key="main_porsi_swap", on_change=sync_var, args=("main_porsi_swap", "sb_porsi_swap"))
        estimasi_baterai_awal = (182.21 + (258.04 - 182.21) * (porsi_swap/100)) * (target_ev_motor/100)
        st.warning(f"**Kebutuhan Pack Baterai:**\n### {estimasi_baterai_awal:.2f} Juta Unit")

with col_i2:
    with st.container(border=True):
        st.subheader("Kebutuhan Bengkel & SDM")
        lama_proyek = st.slider("Lama Pengerjaan Proyek (Tahun)", 1, 10, key="main_lama_proyek", on_change=sync_var, args=("main_lama_proyek", "sb_lama_proyek"))
        
        # Kapasitas 1 Line = 730 hingga 3650 motor per tahun
        line_bengkel_min = (vol_konversi * 1_000_000) / (3650 * lama_proyek)
        line_bengkel_max = (vol_konversi * 1_000_000) / (730 * lama_proyek)
        
        porsi_tipe_a = st.slider("Porsi Bengkel Tipe A (%)", 0, 100, key="main_porsi_tipe_a", on_change=sync_var, args=("main_porsi_tipe_a", "sb_porsi_tipe_a"))
        porsi_tipe_b = 100 - porsi_tipe_a
        
        pa = porsi_tipe_a / 100
        pb = porsi_tipe_b / 100
        
        faktor_pembagi = (2 * pa) + pb
        bengkel_tot_min = line_bengkel_min / faktor_pembagi
        bengkel_tot_max = line_bengkel_max / faktor_pembagi
        
        bengkel_a_min = bengkel_tot_min * pa
        bengkel_a_max = bengkel_tot_max * pa
        bengkel_b_min = bengkel_tot_min * pb
        bengkel_b_max = bengkel_tot_max * pb
        
        sdm_min = line_bengkel_min * 2
        sdm_max = line_bengkel_max * 2

        st.warning(f"""**Kebutuhan Infrastruktur Bengkel:**
### {line_bengkel_min:,.0f} - {line_bengkel_max:,.0f} Line

👤 **Kebutuhan SDM:** {sdm_min:,.0f} - {sdm_max:,.0f} Teknisi  
*(1 Perawatan & 1 Instalatur per line)*
""")
        
        st.info(f"""**Distribusi Tipe Bengkel:**
* **Tipe A (2 Line):** {bengkel_a_min:,.0f} - {bengkel_a_max:,.0f} Unit ({porsi_tipe_a}%)
* **Tipe B (1 Line):** {bengkel_b_min:,.0f} - {bengkel_b_max:,.0f} Unit ({porsi_tipe_b}%)
""")

with col_i3:
    with st.container(border=True):
        st.subheader("Mesin Charging Mobil (SPKLU)")
        mobil_ev = 4.46 * (target_ev_mobil / 100)
        rasio_spklu = st.number_input("Rasio Mobil : 1 SPKLU", key="main_rasio_spklu", on_change=sync_var, args=("main_rasio_spklu", "sb_rasio_spklu"))
        kebutuhan_spklu = (mobil_ev * 1_000_000) / rasio_spklu
        
        with st.expander("⚙️ Atur Komposisi & Harga Mesin", expanded=True):
            st.markdown("**Geser Titik Untuk Komposisi (%)**")
            st.markdown("<br>", unsafe_allow_html=True)
            batas = st.slider("Atur Batas Porsi", 0, 100, label_visibility="collapsed", key="main_batas_spklu", on_change=sync_var, args=("main_batas_spklu", "sb_batas_spklu"))
            
            p_med = batas[0]
            p_fast = batas[1] - batas[0]
            p_ultra = 100 - batas[1]
            
            # Visualisasi Komposisi
            df_bar = pd.DataFrame({
                "Tipe": ["Medium", "Fast", "Ultra Fast"],
                "Porsi (%)": [p_med, p_fast, p_ultra],
                "Kategori": ["Komposisi SPKLU", "Komposisi SPKLU", "Komposisi SPKLU"]
            })
            fig_bar = px.bar(df_bar, x="Porsi (%)", y="Kategori", color="Tipe", orientation='h',
                             color_discrete_map={"Medium": "#3b82f6", "Fast": "#f59e0b", "Ultra Fast": "#ef4444"},
                             text="Porsi (%)")
            fig_bar.update_traces(texttemplate='%{text}%', textposition='inside')
            fig_bar.update_layout(barmode='stack', height=100, margin=dict(l=0, r=0, t=0, b=0),
                                  xaxis=dict(visible=False), yaxis=dict(visible=False),
                                  showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
            st.plotly_chart(fig_bar, use_container_width=True, config={'staticPlot': True})
            
            st.markdown("**Harga per Unit (Juta Rp)**")
            col_h1, col_h2, col_h3 = st.columns(3)
            h_med = col_h1.number_input("Medium", key="main_h_med", on_change=sync_var, args=("main_h_med", "sb_h_med"))
            h_fast = col_h2.number_input("Fast", key="main_h_fast", on_change=sync_var, args=("main_h_fast", "sb_h_fast"))
            h_ultra = col_h3.number_input("Ultra", key="main_h_ultra", on_change=sync_var, args=("main_h_ultra", "sb_h_ultra"))
            
        unit_med = kebutuhan_spklu * (p_med / 100)
        unit_fast = kebutuhan_spklu * (p_fast / 100)
        unit_ultra = kebutuhan_spklu * (p_ultra / 100)
        
        investasi_spklu = ((unit_med * h_med) + (unit_fast * h_fast) + (unit_ultra * h_ultra)) / 1_000_000 
        
        st.warning(f"""**Kebutuhan Mesin SPKLU:**
### {kebutuhan_spklu:,.0f} Unit

**Estimasi Biaya Infrastruktur:**
### Rp {investasi_spklu:.2f} Triliun""")

# --- NEW SECTION: RANTAI PASOK / SUPPLY CHAIN ---
st.divider()
st.subheader("🏭 Kesiapan Industri & Risiko Kebocoran Impor (*Supply Chain*)")
with st.container(border=True):
    st.markdown("Menganalisis kesenjangan (*gap*) antara lonjakan permintaan kendaraan listrik tahunan dengan kapasitas riil pabrik perakitan dan produksi baterai di dalam negeri.")
    
    col_sc1, col_sc2 = st.columns(2)
    
    # Kolom 1: Supply Chain Motor
    with col_sc1:
        st.markdown("#### 🏍️ Produksi Motor Listrik Nasional")
        kapasitas_motor = st.slider("Kapasitas Pabrik Lokal (Juta Unit/Tahun)", 0.5, 10.0, step=0.1, key='main_k_motor', on_change=sync_var, args=('main_k_motor', 'sb_k_motor'))
        harga_impor_motor = st.number_input("Harga Impor 1 Unit Motor EV (Juta Rp)", step=1.0, key='main_h_motor', on_change=sync_var, args=('main_h_motor', 'sb_h_motor'))
        
        # Kalkulasi
        demand_motor_thn = vol_baru / lama_proyek
        defisit_motor_thn = max(0, demand_motor_thn - kapasitas_motor)
        bocor_devisa_motor = defisit_motor_thn * harga_impor_motor
        
        if defisit_motor_thn > 0:
            st.warning(f"**Kesenjangan Pasokan (Defisit):**\n### {defisit_motor_thn:.2f} Juta Unit / Tahun\n*(Permintaan {demand_motor_thn:.2f} Juta vs Kapasitas {kapasitas_motor:.2f} Juta)*")
            st.error(f"**Potensi Kebocoran Devisa Impor (CBU):**\n### Rp {bocor_devisa_motor:.2f} Triliun / Tahun")
        else:
            st.success(f"**Pasokan Aman!**\nKapasitas {kapasitas_motor:.2f} Juta sanggup memenuhi permintaan {demand_motor_thn:.2f} Juta unit/tahun.")

    # Kolom 2: Supply Chain Battery Pack
    with col_sc2:
        st.markdown("#### 🔋 Produksi Battery Pack Nasional")
        kapasitas_baterai = st.slider("Kapasitas Pabrik Baterai Lokal (Juta Unit/Tahun)", 0.1, 100.0, step=0.1, key='main_k_bat', on_change=sync_var, args=('main_k_bat', 'sb_k_bat'))
        harga_impor_baterai = st.number_input("Harga Impor 1 Pack Baterai (Juta Rp)", step=1.0, key='main_h_bat', on_change=sync_var, args=('main_h_bat', 'sb_h_bat'))
        
        # Kalkulasi
        estimasi_baterai_swap = (182.21 + (258.04 - 182.21) * (porsi_swap/100)) * (target_ev_motor/100)
        demand_bat_thn = (total_motor_ev + estimasi_baterai_swap) / lama_proyek
        defisit_bat_thn = max(0, demand_bat_thn - kapasitas_baterai)
        bocor_devisa_bat = defisit_bat_thn * harga_impor_baterai
        
        if defisit_bat_thn > 0:
            st.warning(f"**Kesenjangan Pasokan Baterai (Defisit):**\n### {defisit_bat_thn:.2f} Juta Unit / Tahun\n*(Permintaan {demand_bat_thn:.2f} Juta vs Kapasitas {kapasitas_baterai:.2f} Juta)*")
            st.error(f"**Potensi Kebocoran Devisa Impor Baterai:**\n### Rp {bocor_devisa_bat:.2f} Triliun / Tahun")
        else:
            st.success(f"**Pasokan Baterai Aman!**\nKapasitas {kapasitas_baterai:.2f} Juta sanggup memenuhi permintaan tahunan.")

    bocor_devisa_total = bocor_devisa_motor + bocor_devisa_bat

with st.expander("💡 Dari Mana Angka Infrastruktur, Subsidi, dan Rantai Pasok Berasal?", expanded=True):
    st.markdown(f"""
    **Alur Simulasi Angka:**
    * **Jalur Transisi Motor:** Total target motor listrik ({total_motor_ev:.2f} Juta unit) dipecah menjadi Konversi ({porsi_konversi}%) sebesar **{vol_konversi:.2f} Juta unit** dan Beli Baru ({porsi_baru}%) sebesar **{vol_baru:.2f} Juta unit**.
    * **Biaya Subsidi Pemerintah:** Subsidi Konversi (Rp {biaya_subsidi_konv:.2f} T) + Subsidi Beli Baru (Rp {biaya_subsidi_baru:.2f} T) = **Rp {total_biaya_subsidi:.2f} Triliun**.
    * **Kebutuhan Bengkel & SDM:** Satu *line* menyelesaikan 730–3.650 motor/tahun. Setiap *line* butuh 2 teknisi terampil. *Line* ini didistribusikan ke Bengkel Tipe A (2 *line*) dan Tipe B (1 *line*).
    * **Mesin Charging Mobil (SPKLU):** Total mobil listrik dibagi kepadatan ideal ({rasio_spklu}:1) = **{kebutuhan_spklu:,.0f} Unit SPKLU**.
    * **Total Kebutuhan Baterai & Rantai Pasok:** Dihitung dari 2 komponen utama:
        1. **Baterai Bawaan (1 Unit/Motor):** Sebesar **{total_motor_ev:.2f} Juta unit**.
        2. **Baterai Cadangan (Ekosistem Swap):** Membutuhkan rasio ekstra agar tidak ada antrean. Dengan asumsi {porsi_swap}% pengguna swap, dibutuhkan total cadangan yang terus berputar hingga **{estimasi_baterai_awal:.2f} Juta unit**.
    * **Risiko Kebocoran Devisa:** Total kebutuhan motor dan baterai tersebut dibagi **durasi penyelesaian proyek ({lama_proyek} Tahun)**. Angka permintaan tahunan ini disandingkan dengan kapasitas pabrik lokal. Jika defisit, negara terpaksa melakukan impor utuh (CBU), yang justru memicu kebocoran devisa baru.
    """)

st.divider()

# ==========================================
# 5. POTENSI LOSS PAJAK DAERAH
# ==========================================
st.header("5️⃣ Potensi Loss Pajak Daerah (PBBKB & PKB)")
with st.container(border=True):
    st.markdown("Elektrifikasi menurunkan penerimaan Pajak Bahan Bakar Kendaraan Bermotor (PBBKB). Lebih buruk lagi, karena **EV saat ini bebas PKB (Pajak Kendaraan Bermotor) dan hanya membayar SWDKLLJ**, pemerintah daerah akan kehilangan 100% penerimaan pajak dari setiap kendaraan yang beralih ke listrik.")
    
    st.markdown("---")
    
    # BARIS 1: Input dan Output PBBKB
    col_in_pbbkb, col_out_pbbkb = st.columns(2)
    with col_in_pbbkb:
        tarif_pbbkb = st.slider("Tarif PBBKB Daerah (%)", 5, 10, key="main_tarif_pbbkb", on_change=sync_var, args=("main_tarif_pbbkb", "sb_tarif_pbbkb"))
    
    loss_pbbkb = (vol_hemat_bensin * 10000 * (tarif_pbbkb / 100)) / 1000
    
    with col_out_pbbkb:
        st.error(f"""#### 📉 Potensi Loss PBBKB:
#### Rp {loss_pbbkb:.2f} Triliun""")
    
    st.markdown("---")
    
    # BARIS 2: Input PKB (Mobil & Motor) dan Output Loss PKB
    col_in_pkb, col_out_pkb = st.columns(2)
    
    with col_in_pkb:
        c1, c2 = st.columns(2)
        pkb_mobil = c1.number_input("Rata-rata PKB Mobil <1400cc (Juta Rp)", min_value=1.85, max_value=3.32, step=0.01, key="main_pkb_mobil", on_change=sync_var, args=("main_pkb_mobil", "sb_pkb_mobil"))
        pkb_motor = c2.number_input("Rata-rata PKB Motor (Juta Rp)", min_value=0.10, max_value=0.50, step=0.01, key="main_pkb_motor", on_change=sync_var, args=("main_pkb_motor", "sb_pkb_motor"))
    
    loss_pkb_mobil = (4.46 * (target_ev_mobil / 100)) * pkb_mobil
    loss_pkb_motor = (145.24 * (target_ev_motor / 100)) * pkb_motor
    loss_pkb_total = loss_pkb_mobil + loss_pkb_motor
    
    with col_out_pkb:
        st.error(f"""#### 📉 Potensi Loss PKB & SWDKLLJ:
#### Rp {loss_pkb_total:.2f} Triliun""")

    st.info("""
    💡 **Saran Kebijakan:**
    Mengingat potensi hilangnya Pendapatan Asli Daerah (PAD) yang sangat masif dari pembebasan PKB ini (mencapai puluhan triliun), pemerintah pusat dan daerah perlu segera merumuskan **Pajak Kendaraan Khusus Listrik**. Tarifnya harus tetap menarik bagi masyarakat di masa transisi, namun tidak membuat kas daerah 'berdarah'.
    """)

with st.expander("💡 Dari Mana Angka Loss Pajak Berasal?", expanded=True):
    st.markdown(f"""
    **Alur Simulasi Angka:**
    * **Loss Pajak Bahan Bakar (PBBKB):** Volume Pertalite yang dihemat ({vol_hemat_bensin:.2f} Juta kL) adalah bensin yang tidak lagi dibeli oleh masyarakat. 
        * Perhitungan: {vol_hemat_bensin:.2f} Juta kL × Harga Bensin (Rp 10.000/liter) × Tarif PBBKB Daerah ({tarif_pbbkb}%) = **Rp {loss_pbbkb:.2f} Triliun**.
    * **Loss Pajak Kendaraan Bermotor (PKB):** Karena mobil/motor listrik dibebaskan dari PKB, pemda kehilangan seluruh potensi pajak tahunan dari unit EV yang mengaspal.
        * Loss dari Mobil EV: {mobil_ev:.2f} Juta Unit × Asumsi Rata-rata PKB (Rp {pkb_mobil:.2f} Juta) = **Rp {loss_pkb_mobil:.2f} Triliun**.
        * Loss dari Motor EV: {total_motor_ev:.2f} Juta Unit × Asumsi Rata-rata PKB (Rp {pkb_motor:.2f} Juta) = **Rp {loss_pkb_motor:.2f} Triliun**.
        * Total Loss PKB = **Rp {loss_pkb_total:.2f} Triliun**.
    """)

st.divider()

# ==========================================
# 6. ANALISIS ROI & KESIMPULAN
# ==========================================
st.header("6️⃣ Kesimpulan & Analisis ROI (Return on Investment)")

# Kalkulasi Variabel Agregat
total_hemat_kas_negara = hemat_kas_negara + hemat_bersih_solar
total_modal = total_biaya_subsidi + investasi_spklu
total_kas_pemda_menguap = loss_pbbkb + loss_pkb_total
fiskal_net = total_hemat_kas_negara - total_kas_pemda_menguap
makro_net = (hemat_rp_devisa - bocor_devisa_total) + hemat_rakyat # Dikurangi kebocoran impor CBU/Baterai
roi_persen = (makro_net / total_modal) * 100 if total_modal > 0 else 0
payback_period = total_modal / makro_net if makro_net > 0 else 0

with st.container(border=True):
    st.markdown("### 📈 1. Penghematan dari Zero Import (Benefit Tahunan)")
    st.markdown("Analisis dari perspektif kas negara (Subsidi APBN) dan perputaran uang internasional (Devisa).")
    
    c_b1, c_b2, c_b3 = st.columns(3)
    c_b1.success(f"**Hemat Subsidi BBM (APBN):**\n* Bensin: Rp {hemat_kas_negara:.2f} T\n* Solar: Rp {hemat_bersih_solar:.2f} T\n* **Total: Rp {total_hemat_kas_negara:.2f} Triliun / tahun**")
    c_b2.info(f"**Net Devisa Nasional:**\n* Devisa Ditahan: Rp {hemat_rp_devisa:.2f} T\n* Kebocoran Impor EV/Baterai: -Rp {bocor_devisa_total:.2f} T\n* **Netto: Rp {(hemat_rp_devisa - bocor_devisa_total):.2f} Triliun / tahun**")
    c_b3.success(f"**Hemat Uang Masyarakat:**\n* Biaya Bensin Rp {biaya_bensin_awal:.2f} T dikurangi Biaya Listrik Rp {biaya_listrik:.2f} T.\n* **Total: Rp {hemat_rakyat:.2f} Triliun / tahun**")

    st.divider()

    st.markdown("### 📉 2. Kebutuhan Investasi & Risiko Fiskal (Cost)")
    st.markdown("Estimasi alokasi modal dan potensi risiko pada Pendapatan Asli Daerah (PAD).")
    
    c_c1, c_c2 = st.columns(2)
    c_c1.warning(f"**Kebutuhan Investasi Awal (Capex):**\n* Subsidi Kendaraan: Rp {total_biaya_subsidi:.2f} T\n* Infrastruktur SPKLU: Rp {investasi_spklu:.2f} T\n* **Total Kebutuhan Modal: Rp {total_modal:.2f} Triliun**")
    c_c2.error(f"**Potensi Kontraksi PAD (Minus Tahunan):**\n* Loss PBBKB: Rp {loss_pbbkb:.2f} T\n* Loss PKB: Rp {loss_pkb_total:.2f} T\n* **Total Penurunan Kas Pemda: Rp {total_kas_pemda_menguap:.2f} Triliun / tahun**")

    st.divider()

    st.markdown("### ⚖️ 3. Analisis Kelayakan & Rekomendasi Kebijakan")
    st.markdown(f"Apabila penghematan devisa dari kebijakan *zero import* dialokasikan untuk membiayai kebutuhan investasi sebesar **Rp {total_modal:.2f} Triliun**, bagaimana tingkat kelayakannya? Analisis berikut menunjukkan anomali signifikan antara dampak fiskal dan makroekonomi yang patut menjadi atensi.")
    
    c_r1, c_r2 = st.columns(2)
    with c_r1:
        st.error("**A. Perspektif Fiskal Pemerintah (APBN & APBD) = DEFISIT**")
        st.markdown(f"Secara kalkulasi kas negara murni, pemerintah pusat menghemat subsidi **Rp {total_hemat_kas_negara:.2f} T**, namun pemerintah daerah berpotensi kehilangan pajak **Rp {total_kas_pemda_menguap:.2f} T**. Secara agregat, arus kas (*cashflow*) birokrasi pemerintahan akan mengalami kontraksi sebesar **Rp {abs(fiskal_net):.2f} Triliun per tahun**.")
        st.markdown("**Rekomendasi Fiskal:** Negara akan kesulitan mencapai titik impas (*break-even*) kecuali **Pajak Kendaraan Khusus Listrik segera diberlakukan** untuk mengkompensasi tergerusnya Pendapatan Asli Daerah (PAD).")
        
    with c_r2:
        st.success("**B. Perspektif Makroekonomi Nasional = SANGAT POSITIF**")
        st.markdown(f"Namun, jika ditinjau dari kacamata ekonomi agregat (Pemerintah + Swasta + Masyarakat), kebijakan ini memberikan dampak yang sangat masif.")
        st.markdown(f"* **Total Kebutuhan Investasi Transisi:** Rp {total_modal:.2f} Triliun.\n* **Keuntungan Nasional Tahunan:** Net Penyelamatan Devisa (Rp {(hemat_rp_devisa - bocor_devisa_total):.2f} T) + Penghematan Masyarakat (Rp {hemat_rakyat:.2f} T) = **Rp {makro_net:.2f} Triliun / tahun**.\n* **Return on Investment (ROI) Nasional:** **{roi_persen:.2f}% per tahun**.\n* **Payback Period:** Rp {total_modal:.2f} T ÷ Rp {makro_net:.2f} T = **Hanya dalam {payback_period:.1f} Tahun, investasi nasional akan kembali (*Break-Even*)!**")

st.divider()

# ==========================================
# FOOTER TAGLINE
# ==========================================
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <h4>💡 Semua Bisa Dihitung</h4>
    <p>by Alif Towew</p>
</div>
""", unsafe_allow_html=True)
