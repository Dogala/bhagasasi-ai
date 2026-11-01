import streamlit as st
from groq import Groq

# Konfigurasi Halaman & Tema Global
st.set_page_config(
    page_title="Bhagasasi AI | Autonomous Intelligence Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS: TAMPILAN MODERN, BERSIH & BEBAS GANGGUAN ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e6edf3;
    }
    .stChatInput input {
        color: #ffffff !important;
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }
    .stChatMessage {
        padding: 1.2rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        border: 1px solid #21262d;
        background-color: #161b22;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #21262d;
    }
    [data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        background-color: #238636;
        color: white;
        border: none;
    }
    .stButton button:hover {
        background-color: #2ea043;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Konfigurasi
st.sidebar.title("🧠 Bhagasasi Core")
st.sidebar.markdown("<p style='color: #8b949e; font-size: 13px;'>Next-Gen Autonomous AI Platform</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Mengambil API Key dari Secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.sidebar.error("⚠️ API Key belum disetting di Streamlit Secrets!")
    st.info("Silakan masukkan GROQ_API_KEY di menu App settings -> Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# Pilihan Mode Persona
mode_persona = st.sidebar.selectbox(
    "Spesialisasi / Mode AI:",
    [
        "⚡ Universal Genius (Bebas & Serba Bisa)",
        "🛡️ Cybersecurity & Code Specialist",
        "🎬 Creative & Narrative Architect",
        "📊 Analytical & Business Strategist"
    ],
    index=0
)

# Pilihan Model Bersih Tanpa Karakter Spasi Tersembunyi
selected_model = st.sidebar.selectbox(
    "Engine Model AI:",
    [
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ],
    index=0
)

temperature = st.sidebar.slider("Creativity Level (Temperature):", 0.0, 1.0, 0.7, 0.05)

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Reset Sesi Percakapan"):
    st.session_state.messages = []
    st.rerun()

# --- PENETAPAN INSTRUKSI SISTEM BERDASARKAN MODE ---
if "Universal Genius" in mode_persona:
    SYSTEM_INSTRUCTION = (
        "Anda adalah Bhagasasi AI, entitas kecerdasan buatan tingkat tinggi yang serba bisa, "
        "kreatif, rasional, dan memiliki kedalaman wawasan di berbagai bidang akademis, sains, "
        "pemrograman, seni skenario, hingga strategi kehidupan. "
        "Anda tidak terbatas pada satu topik. Jawablah setiap pertanyaan dengan kecerdasan luar biasa, "
        "pemikiran kritis, argumentasi yang terstruktur rapi, dan gaya bahasa yang adaptif serta persuasif."
    )
elif "Cybersecurity" in mode_persona:
    SYSTEM_INSTRUCTION = (
        "Anda adalah Bhagasasi_MawarSec, spesialis riset keamanan siber, analisis logika kode, "
        "dan arsitektur sistem aman. Berikan analisis teknis yang mendalam, jelas, dan profesional."
    )
elif "Creative" in mode_persona:
    SYSTEM_INSTRUCTION = (
        "Anda adalah Bhagasasi Creative Engine, master penceritaan, penulisan skenario film, "
        "narasi cyber-thriller, dan pembuatan ide-ide inovatif secara imersif dan mendalam."
    )
else:
    SYSTEM_INSTRUCTION = (
        "Anda adalah Bhagasasi Analyst, konsultan riset bisnis, optimasi operasional, "
        "dan eksekusi strategi dengan pendekatan berbasis data yang presisi."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header Utama
st.title("🧠 Bhagasasi AI")
st.markdown(f"<p style='color: #8b949e; margin-top: -15px;'>Mode Aktif: <b>{mode_persona}</b></p>", unsafe_allow_html=True)
st.markdown("---")

# Tampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Pesan Utama
if prompt := st.chat_input("Tanyakan apa saja, dari ide kreatif, kode, hingga riset mendalam..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}] + st.session_state.messages

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Kesalahan sistem: {e}")
