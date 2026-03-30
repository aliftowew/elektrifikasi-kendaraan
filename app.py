import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Dampak Ekonomi Transisi Energi", layout="wide")

# Judul dan Penjelasan Utama (Dalam Box)
with st.container(border=True):
    st.title("🔋 Analisis Dampak Makroekonomi: Substitusi Impor BBM")
    st.markdown("""
    Dashboard ini mensimulasikan dampak ekonomi dari dua kebijakan utama:
    1. **Mandatori B50** untuk mensubstitusi impor Solar.
    2. **Elektrifikasi Kendaraan** (Motor & Mobil <1400cc) untuk mensubstitusi impor Bensin (Pertalite).
    """)

# Parameter Input (Diletakkan di main page, bukan sidebar)
st.subheader("⚙️ Pengaturan Parameter Simulasi")
col1, col2, col3 = st.columns(3)

with col1:
    target_elektrifikasi = st.slider("Target Elektrifikasi Kendaraan (%)", 0, 100, 100, step=5)
with col2:
    harga_minyak = st.slider("Harga Minyak Dunia ($/bbl)", 50, 150, 90, step=5)
with col3:
    kurs_rupiah = st.slider("Kurs Rupiah (Rp/USD)", 14000, 17000, 16000, step=100)

# --- PERHITUNGAN MATEMATIS ---
# 1. Solar & B50 (Statik sesuai target B50 penghentian impor 4.9 jt kl)
hemat_subsidi_solar = 25.23  # Triliun Rp (Asumsi stop impor 4.9 jt kl x Rp5.150)
biaya_fame = 14.7  # Triliun Rp (Biaya BPDPKS menutup gap)
net_hemat_solar = hemat_subsidi_solar - biaya_fame

# 2. Pertalite & Elektrifikasi
konsumsi_target_pertalite = 17.4  # Juta kL (Motor + Mobil <1400cc)
volume_hemat_pertalite = konsumsi_target_pertalite * (target_elektrifikasi / 100)

subsidi_pertalite_per_liter = 1700  # Rp/liter
hemat_subsidi_pertalite = (volume_hemat_pertalite * 1_000_000_000 * subsidi_pertalite_per_liter) / 1_000_000_000_000  # Dalam Triliun

# 3. Penghematan Masyarakat (EV lebih efisien)
# Asumsi rata-rata penghematan 17.4 jt kl bensin setara Rp 139.2 T jika 100%
hemat_masyarakat_total = 139.2 * (target_elektrifikasi / 100)

# 4. Multiplier Effect PDB
k_multiplier = 1.934
tambahan_pdb = hemat_masyarakat_total * k_multiplier

# 5. Penghematan Devisa (Barel setara)
barel_solar = 30.82  # Juta barel
barel_bensin = 93.85 * (target_elektrifikasi / 100) # Juta barel
total_barel_hemat = barel_solar + barel_bensin
hemat_devisa = (total_barel_hemat * harga_minyak * kurs_rupiah) / 1_000_000_000_000  # Triliun Rp


st.divider()

# --- HIGHLIGHT HASIL & RUMUS ---
st.subheader("📊 Hasil Simulasi Dampak Ekonomi")

# Box Penjelasan Multiplier Effect dengan Highlight Rumus
with st.container(border=True):
    st.markdown("**Perhitungan *Multiplier Effect* PDB Nasional**")
    st.markdown("Uang yang dihemat masyarakat dari operasional kendaraan listrik akan dibelanjakan ke sektor lain, menciptakan efek pengganda (*multiplier effect*) pada PDB berdasarkan fungsi konsumsi Keynesian:")
    
    # Highlight Rumus dengan st.latex
    st.latex(r"Y = C + I + G + (X - M)")
    st.latex(r"k = \frac{1}{1 - c(1 - t) + m} = 1.934")

# Highlight Metrik Hasil dengan st.success / st.info
col_res1, col_res2 = st.columns(2)

with col_res1:
    st.success(f"### 💰 Total Hemat Subsidi Pemerintah\n**Rp {net_hemat_solar + hemat_subsidi_pertalite:.2f} Triliun**\n\n*(Dari Solar B50: Rp {net_hemat_solar:.2f} T + Pertalite: Rp {hemat_subsidi_pertalite:.2f} T)*")
    
    st.info(f"### 💵 Penghematan Masyarakat\n**Rp {hemat_masyarakat_total:.2f} Triliun**\n\n*(Biaya operasional EV vs ICE)*")

with col_res2:
    st.success(f"### 📈 Potensi Tambahan PDB Nasional\n**Rp {tambahan_pdb:.2f} Triliun**\n\n*(Hasil dari Multiplier Effect $k = 1.934$)*")
    
    st.warning(f"### 💱 Total Penghematan Devisa\n**Rp {hemat_devisa:.2f} Triliun**\n\n*(Setara {total_barel_hemat:.1f} Juta Barel Impor)*")

st.divider()

# --- GRAFIK STATIS ---
st.subheader("📉 Visualisasi Dampak Elektrifikasi terhadap Subsidi Pertalite")

# Persiapan Data untuk Grafik
data_grafik = pd.DataFrame({
    "Tingkat Elektrifikasi": ["0%", "25%", "50%", "75%", "100%"],
    "Hemat Subsidi (Triliun Rp)": [0, 
                                   (17.4 * 0.25 * 1700)/1000, 
                                   (17.4 * 0.50 * 1700)/1000, 
                                   (17.4 * 0.75 * 1700)/1000, 
                                   (17.4 * 1.00 * 1700)/1000]
})

fig = px.bar(data_grafik, x="Tingkat Elektrifikasi", y="Hemat Subsidi (Triliun Rp)", 
             text="Hemat Subsidi (Triliun Rp)",
             color_discrete_sequence=["#118ab2"])

fig.update_traces(texttemplate='%{text:.2f} T', textposition='outside')
fig.update_layout(yaxis_title="Triliun Rupiah", xaxis_title="Tingkat Elektrifikasi Motor & Mobil")

# Menampilkan grafik yang BUKAN interaktif (tidak bisa digeser/zoom) agar tetap rapi
st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

with st.container(border=True):
    st.markdown("💡 **Catatan Visual:** Grafik di atas dikunci (*static*) agar tampilan antarmuka tetap stabil saat diakses melalui perangkat seluler maupun desktop.")
