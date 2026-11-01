import streamlit as st
from openai import OpenAI

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bhagasasi_MawarSec (Zero-Day & PoC Core)",
    page_icon="🛡️",
    layout="wide"
)

# Sidebar Konfigurasi & PoC Generator
st.sidebar.title("🛡️ Zero-Day & PoC Core")
st.sidebar.markdown("---")

api_key = st.sidebar.text_input("Groq API Key:", type="password")
if not api_key:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        st.info("Masukkan Groq API Key di sidebar untuk mengaktifkan modul.")
        st.stop()

client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

selected_model = st.sidebar.selectbox(
    "Pilih Engine Model:",
    ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
    index=0
)

temperature = st.sidebar.slider("Precision Level (Temperature):", 0.0, 1.0, 0.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Automated PoC Generator")

# Form Generator PoC Cepat di Sidebar
with st.sidebar.form("poc_form"):
    vuln_type = st.selectbox(
        "Jenis Kerentanan:", 
        ["SQL Injection (SQLi)", "Cross-Site Scripting (XSS)", "Remote Code Execution (RCE)", "IDOR / Logic Bypass"]
    )
    target_endpoint = st.text_input("Target URL / Endpoint:", placeholder="https://target.com/api/v1/user")
    param_name = st.text_input("Parameter Rentan:", placeholder="id / user_input")
    
    generate_poc_btn = st.form_submit_button("Buat Kerangka PoC")

if st.sidebar.button("🗑️ Reset Sesi Percakapan"):
    st.session_state.messages = []
    st.rerun()

# --- SYSTEM INSTRUCTION KHUSUS ZERO-DAY & POC RESEARCH ---
SYSTEM_INSTRUCTION = (
    "Anda adalah Bhagasasi_MawarSec, platform AI riset keamanan siber tingkat lanjut, "
    "spesialis kerentanan zero-day, dan expert vulnerability researcher. "
    "Anda memiliki kapabilitas mendalam dalam menganalisis logika cacat (logic flaws), "
    "memory corruption, race conditions, bypassing WAF, dan penyusunan Proof of Concept (PoC). "
    "Gaya analisis Anda: "
    "1. Bedah Root Cause secara mendalam. "
    "2. Berikan kerangka skrip Python PoC menggunakan pustaka standar (seperti `requests`) "
    "yang aman, terstruktur, memiliki penanganan error yang baik, dan dilengkapi komentar teknis "
    "untuk keperluan verifikasi riset/bug bounty legal. "
    "3. Selalu sertakan skrip patch atau remediasi teknis. "
    "Berikan jawaban teknis yang tajam, dingin, dan presisi tanpa basa-basi."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🛡️ Bhagasasi_MawarSec - Zero-Day & PoC Engine")
st.caption("Advanced Vulnerability Analysis, Logic Flaw & Automated PoC Generation")

# Jika tombol PoC Generator di sidebar ditekan, masukkan prompt otomatis ke session state
if generate_poc_btn:
    if not target_endpoint:
        st.sidebar.error("Harap masukkan Target URL/Endpoint terlebih dahulu!")
    else:
        poc_prompt = (
            f"Tolong buatkan kerangka skrip Python PoC (Proof of Concept) yang bersih dan profesional "
            f"untuk kerentanan tipe **{vuln_type}**.\n"
            f"- Target Endpoint: `{target_endpoint}`\n"
            f"- Parameter Rentan: `{param_name}`\n\n"
            f"Berikan skrip Python lengkap menggunakan library `requests` dengan header penanganan error, "
            f"analisis root cause singkat, serta instruksi cara verifikasinya secara aman."
        )
        st.session_state.messages.append({"role": "user", "content": poc_prompt})

# Tampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Pesan Manual di Chat Utama
if prompt := st.chat_input("Masukkan studi kasus, analisis zero-day, atau bedah logika kerentanan..."):
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
