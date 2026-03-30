import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Makroekonomi Substitusi BBM", layout="wide")

st.title("🔋 Analisis Komprehensif: Substitusi Impor BBM & Elektrifikasi")
st.markdown("""
Aplikasi ini mensimulasikan 7 dampak makroekonomi dari penghentian impor Solar dan Bensin (Pertalite) melalui kebijakan mandatori B50 dan Elektrifikasi Kendaraan.
""")

# --- GLOBAL SLIDER (Main Page) ---
st.subheader("⚙️ Parameter Makro Global")
col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    target_ev = st.slider("Target Elektrifikasi Kendaraan (%)", 0, 100, 100, step=5)
with col_g2:
    harga_minyak = st.slider("Harga Minyak Dunia ($/bbl)", 50, 150, 90, step=5)
with col_g3:
    kurs_rp = st.slider("Kurs Rupiah (Rp/USD)", 14000, 18000, 16000, step=100)

# Kebutuhan dasar berdasarkan data
konsumsi_solar_2026 = 39.84 # jt kl
produksi_solar_lokal = 20.1 # jt kl (termasuk RDMP 1.8 jt kl)
target_pertalite = 17.4 # jt kl (Motor + Mobil < 1400cc)

st.divider()

# --- 7 TAB PEMBAHASAN ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. Pasokan B50", 
    "2. Subsidi Pemerintah", 
    "3. PDB & Masyarakat", 
    "4. Kecukupan Listrik", 
    "5. Devisa", 
    "6. Bioetanol (E10)", 
    "7. Transisi & Pajak"
])

# ==========================================
# TAB 1: SOLUSI PASOKAN SOLAR (B50)
# ==========================================
with tab1:
    st.header("1. Solusi Pasokan Solar Indonesia (Mandatori B50)")
    st.markdown("""
    Melalui regresi logaritmik, diproyeksikan konsumsi solar 2026 mencapai **39,84 juta kL**. 
    Dengan implementasi **B50** (50% FAME Sawit, 50% Solar Fosil), kebutuhan masing-masing adalah 19,92 juta kL. 
    Karena kapasitas kilang domestik (plus RDMP) mencapai 20,1 juta kL, **impor solar bisa ditekan menjadi 0 (Nol)**, bahkan surplus 0,18 juta kL.
    """)
    
    with st.container(border=True):
        st.subheader("🧮 Kalkulator Kebutuhan Lahan Sawit")
        prod_sawit = st.number_input("Produktivitas CPO (ton/ha/tahun)", min_value=1.0, max_value=10.0, value=3.3, step=0.1)
        
        # Konversi 19.92 jt kl FAME ke ton CPO (asumsi 1 ton = 1086 liter)
        ton_cpo_dibutuhkan = (19.92 * 1_000_000) / 1086 / 1_000_000 # dalam juta ton
        lahan_dibutuhkan = ton_cpo_dibutuhkan / prod_sawit
        
        st.info(f"Untuk memproduksi 19,92 juta kL FAME, dibutuhkan **{ton_cpo_dibutuhkan:.2f} Juta Ton CPO**.\n\nDengan produktivitas {prod_sawit} ton/ha, dibutuhkan tambahan lahan sawit seluas **{lahan_dibutuhkan:.2f} Juta Hektare**.")

# ==========================================
# TAB 2: PENGHEMATAN PEMERINTAH (SUBSIDI)
# ==========================================
with tab2:
    st.header("2. Penghematan Subsidi Pemerintah")
    st.markdown("""
    Penghentian impor menekan beban APBN. Namun, untuk solar, negara (via BPDPKS) harus membayar selisih harga keekonomian FAME yang lebih mahal dari solar fosil.
    """)
    
    with st.container(border=True):
        st.subheader("🧮 Kalkulator Penghematan Subsidi")
        subsidi_pertalite = st.number_input("Subsidi Pertalite (Rp/liter)", value=1700, step=100)
        gap_fame = st.number_input("Selisih Harga FAME vs Solar (Rp/liter)", value=3000, step=500)
        
        # Kalkulasi Solar
        hemat_impor_solar = 4.9 * 5150 # jt kl x subsidi (miliar) = 25.23 T
        beban_bpdpks = 4.9 * gap_fame / 1000 # T
        net_solar = (hemat_impor_solar / 1000) - beban_bpdpks
        
        # Kalkulasi Pertalite
        volume_hemat_pertalite = target_pertalite * (target_ev / 100)
        hemat_pertalite = (volume_hemat_pertalite * 1_000_000_000 * subsidi_pertalite) / 1_000_000_000_000
        
        col_s1, col_s2 = st.columns(2)
        col_s1.success(f"**Hemat Bersih Solar (B50):**\nRp {25.23 - beban_bpdpks:.2f} Triliun")
        col_s2.success(f"**Hemat Subsidi Pertalite (EV):**\nRp {hemat_pertalite:.2f} Triliun")

# ==========================================
# TAB 3: PENGHEMATAN MASYARAKAT & PDB
# ==========================================
with tab3:
    st.header("3. Penghematan Masyarakat & Multiplier Effect")
    st.markdown("""
    Biaya operasional kendaraan listrik (EV) rata-rata **5x lebih murah** dibanding ICE. Uang yang dihemat masyarakat ini akan dibelanjakan ke sektor lain, memicu *Multiplier Effect* Keynesian terhadap PDB.
    """)
    st.latex(r"k = \frac{1}{1 - c(1 - t) + m}")
    
    with st.container(border=True):
        st.subheader("🧮 Kalkulator PDB Multiplier")
        c_propensity = st.slider("Marginal Propensity to Consume (c)", 0.5, 0.9, 0.779, step=0.01)
        tax_rate = st.slider("Tax Revenue to GDP (t)", 0.05, 0.20, 0.118, step=0.01)
        import_rate = st.slider("Import to GDP (m)", 0.10, 0.30, 0.203, step=0.01)
        
        k_val = 1 / (1 - c_propensity * (1 - tax_rate) + import_rate)
        
        # 17.4 jt kl bensin ~ Rp 139.2 T hemat masyarakat jika 100%
        hemat_masyarakat = 139.2 * (target_ev / 100)
        pdb_tumbuh = hemat_masyarakat * k_val
        
        st.info(f"Nilai Multiplier (k) = **{k_val:.3f}**\n\nDari penghematan masyarakat **Rp {hemat_masyarakat:.2f} T**, tercipta dorongan ekonomi (PDB) sebesar **Rp {pdb_tumbuh:.2f} Triliun**.")

# ==========================================
# TAB 4: KECUKUPAN LISTRIK
# ==========================================
with tab4:
    st.header("4. Skenario Kecukupan Listrik Nasional")
    st.markdown("Jika terjadi elektrifikasi masif, apakah pasokan listrik PLN mencukupi?")
    
    with st.container(border=True):
        st.subheader("🧮 Kalkulator Beban Listrik EV")
        kwh_per_liter = st.number_input("Konversi 1 Liter BBM = x kWh", value=1.2, step=0.1)
        surplus_pln = st.number_input("Surplus Listrik Nasional (TWh)", value=36.31, step=1.0)
        
        volume_hemat = target_pertalite * (target_ev / 100)
        beban_twh = (volume_hemat * 1_000_000_000 * kwh_per_liter) / 1_000_000_000 # TWh
        
        if beban_twh <= surplus_pln:
            st.success(f"**Aman!** Kebutuhan listrik EV sebesar **{beban_twh:.2f} TWh** masih di bawah surplus pasokan nasional ({surplus_pln} TWh).")
        else:
            st.error(f"**Defisit!** Kebutuhan listrik EV ({beban_twh:.2f} TWh) melebihi surplus. Butuh pembangkit baru.")

# ==========================================
# TAB 5: PENGHEMATAN DEVISA
# ==========================================
with tab5:
    st.header("5. Devisa yang Dihemat")
    st.markdown("Menghentikan impor BBM berarti menahan devisa tidak keluar dari dalam negeri, yang akan memperkuat stabilitas nilai tukar Rupiah.")
    
    with st.container(border=True):
        st.subheader("🧮 Kalkulator Penghematan Devisa")
        st.markdown("*Menggunakan slider Harga Minyak & Kurs di atas*")
        
        barrel_solar = 30.82 # Juta barel
        barrel_bensin = 93.85 * (target_ev / 100)
        tot_barrel = barrel_solar + barrel_bensin
        
        hemat_usd = tot_barrel * harga_minyak # Juta USD
        hemat_rp = (hemat_usd * kurs_rp) / 1_000_000 # Triliun Rp
        
        st.success(f"Total Impor Dicegah: **{tot_barrel:.2f} Juta Barel**\n\nDevisa Negara Terselamatkan: **$ {hemat_usd/1000:.2f} Miliar** (Setara **Rp {hemat_rp:.2f} Triliun**)")

# ==========================================
# TAB 6: BIOETANOL (E10) UNTUK SISA BENSIN
# ==========================================
with tab6:
    st.header("6. Solusi Sisa Bensin (Bioetanol E10)")
    st.markdown("Jika elektrifikasi tidak mencapai 100%, masih ada sisa impor bensin. Ini bisa diakali dengan campuran Bioetanol (E10).")
    
    with st.container(border=True):
        st.subheader("🧮 Kalkulator Lahan Bioetanol")
        sisa_bensin = target_pertalite * ((100 - target_ev) / 100)
        kebutuhan_e10 = sisa_bensin * 0.10 # 10% dari sisa bensin
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            prod_tebu = st.number_input("Yield Etanol Tebu (kL/ha)", value=4.9, step=0.1)
            lahan_tebu = kebutuhan_e10 / prod_tebu * 1_000_000 if prod_tebu > 0 else 0
            st.info(f"Opsi Tebu: Butuh **{lahan_tebu:,.0f} Hektare**")
            
        with col_e2:
            prod_singkong = st.number_input("Yield Etanol Singkong (kL/ha)", value=4.07, step=0.1)
            lahan_singkong = kebutuhan_e10 / prod_singkong * 1_000_000 if prod_singkong > 0 else 0
            st.info(f"Opsi Singkong: Butuh **{lahan_singkong:,.0f} Hektare**")

# ==========================================
# TAB 7: BIAYA TRANSISI & LOSS PAJAK
# ==========================================
with tab7:
    st.header("7. Biaya Infrastruktur & Potensi Kehilangan Pajak Daerah")
    st.markdown("Transisi ini butuh infrastruktur masif (Bengkel Konversi & SPKLU) dan berdampak pada hilangnya Pajak Bahan Bakar Kendaraan Bermotor (PBBKB) bagi Pemerintah Daerah.")
    
    with st.container(border=True):
        st.subheader("🧮 Kalkulator Dampak Sektor Publik & Swasta")
        harga_spklu = st.number_input("Rata-rata Investasi 1 SPKLU (Juta Rp)", value=200, step=50)
        
        # Asumsi total SPKLU butuh 297.200 unit jika 100% EV
        kebutuhan_spklu = 297200 * (target_ev / 100)
        biaya_spklu = (kebutuhan_spklu * harga_spklu) / 1_000_000 # Triliun
        
        loss_pbbkb_max = 17.4 * (target_ev / 100)
        loss_pkb_max = 43.86 * (target_ev / 100)
        
        st.warning(f"**Kebutuhan Investasi SPKLU:** Rp {biaya_spklu:.2f} Triliun")
        st.error(f"**Potensi Loss PBBKB Daerah:** Rp {loss_pbbkb_max:.2f} Triliun\n\n**Potensi Loss PKB & SWDKLLJ:** Rp {loss_pkb_max:.2f} Triliun\n\n*(Catatan: Perlu skema pajak baru seperti Pajak Listrik Khusus EV untuk mitigasi)*")
