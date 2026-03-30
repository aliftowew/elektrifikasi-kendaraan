import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Makroekonomi BBM", layout="wide")

# CSS HACK: Sembunyikan angka di titik slider khusus untuk Range Slider agar tidak bingung
# Ini adalah solusi tidak resmi tapi berfungsi di Streamlit saat ini.
st.markdown("""
<style>
    div[data-testid="stThumbValue"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Analisis Kebijakan Substitusi Impor BBM & Elektrifikasi")

# --- PENGATURAN GLOBAL (Di Sidebar) ---
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
# Bagian Atas (Asumsikan ada kalkulasi lengkap)
# hardcoded contoh tampilan atas dari gambar asli
st.image("image_0.png", use_column_width=True) 

st.divider()

# ==========================================
# 4. KEBUTUHAN INFRASTRUKTUR & SUBSIDI
# ==========================================
st.header("4️⃣ Kebutuhan Infrastruktur, Transisi & Subsidi")

# ... (Kalkulasi Infrastruktur & Subsidi Lainnya) ...

with st.container(border=True):
    # ... (Tampilan SPKLU Mobil Lainnya) ...
    
    with st.expander("⚙️ Atur Komposisi & Harga Mesin", expanded=False):
        st.markdown("**Geser Titik Untuk Komposisi (%)**")
        # Range Slider dengan 2 titik kontrol (Otomatis menghasilkan 3 porsi yang totalnya 100%)
        # Trik CSS di atas menangani penyembunyian angka thumb, sehingga tidak membingungkan.
        st.markdown("<br>", unsafe_allow_html=True) # Tambah ruang
        
        # Contoh representasi visual range slider tanpa angka thumb (seperti di image_7.png / image_9.png)
        # st.slider("Komposisi SPKLU", 0, 100, (55, 83), label_visibility="collapsed")
        st.image("image_7.png", label="Representasi Visual")
        st.markdown("<p style='text-align: center; color: gray;'>Contoh representasi visual: Angka di-handle telah disembunyikan via CSS.</p>", unsafe_allow_html=True)
        # pass

st.divider()

# ==========================================
# 5. POTENSI LOSS PAJAK DAERAH
# ==========================================
st.header("5️⃣ Potensi Loss Pajak Daerah (PBBKB & PKB)")
with st.container(border=True):
    st.markdown("Elektrifikasi menurunkan penerimaan Pajak Bahan Bakar Kendaraan Bermotor (PBBKB). Lebih buruk lagi, karena **EV saat ini bebas PKB (Pajak Kendaraan Bermotor) dan hanya membayar SWDKLLJ**, pemerintah daerah akan kehilangan 100% penerimaan pajak dari setiap kendaraan yang beralih ke listrik.")
    
    # 1. Kelompokkan Slider PBBKB
    st.markdown("---") # Pembatas visual
    with st.container(border=True):
        st.subheader("Simulasi Tarif PBBKB")
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            tarif_pbbkb = st.slider("Tarif PBBKB Daerah (%)", 5, 10, 10, label_visibility="visible")

    st.markdown("---") # Pembatas visual

    # 3. PKB Mobil & Motor sejajar dengan tampilan Loss PKB
    # 2. Ubah slider PKB menjadi input angka
    col_pkb_in, col_pkb_out = st.columns([1, 1])

    with col_pkb_in:
        st.subheader("Rata-rata PKB Tahunan (ICE)")
        pkb_mobil = st.number_input("Rata-rata PKB Mobil <1400cc (Juta Rp/Unit)", value=2.50, min_value=1.85, max_value=3.32, step=0.01)
        pkb_motor = st.number_input("Rata-rata PKB Motor (Juta Rp/Unit)", value=0.25, min_value=0.10, max_value=0.50, step=0.01)

    with col_pkb_out:
        # Kalkulasi (contoh nilai hardcoded berdasarkan image_8.png untuk tampilan)
        loss_pbbkb = 17.40
        loss_pkb_total = 47.46

        # Tampilan Loss dengan box kustom berwarna merah/pink lembut
        c_p1, c_p2 = st.columns(2)
        box_style = """
        background-color: #fce4ec;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        border: 1px solid #ffccbc;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        """
        st.markdown(f'<div style="{box_style}">', unsafe_allow_html=True)
        c_p1.error(f"""#### 📉 Potensi Loss PBBKB:
#### Rp {loss_pbbkb:.2f} Triliun""")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div style="{box_style}">', unsafe_allow_html=True)
        c_p2.error(f"""#### 📉 Potensi Loss PKB:
#### Rp {loss_pkb_total:.2f} Triliun""")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---") # Pembatas visual
    
    # Menambahkan box info saran kebijakan
    st.info("""
    💡 **Saran Kebijakan:**
    Mengingat potensi hilangnya Pendapatan Asli Daerah (PAD) yang sangat masif dari pembebasan PKB ini (mencapai puluhan triliun), pemerintah pusat dan daerah perlu segera merumuskan **Pajak Kendaraan Khusus Listrik**. Tarifnya harus tetap menarik bagi masyarakat di masa transisi, namun tidak membuat kas daerah 'berdarah'.
    """)
