import streamlit as st
from groq import Groq
import pypdf

# 1. Configuración de la página
st.set_page_config(page_title="Auditor IA - AISC 207 Free", page_icon="🏗️", layout="centered")

st.markdown("""
    <style>
    .main-header { font-size:24pt; font-weight:bold; color:#1E3A8A; margin-bottom:5px; }
    .sub-header { font-size:12pt; color:#4B5563; margin-bottom:20px; }
    .status-box { padding: 15px; border-radius: 5px; margin-bottom: 20px; background-color: #EFF6FF; border-left: 5px solid #1D4ED8; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏗️ Sistema de Auditoría Interna IA — AISC 207</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Módulo Gratuito con Llama-3 (Meta)</div>', unsafe_allow_html=True)

# 2. Barra lateral para la llave de Groq
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Introduce tu Groq API Key (gsk_...):", type="password")

if "fase" not in st.session_state:
    st.session_state.fase = "INICIO"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Flujo de Estados
if st.session_state.fase == "INICIO":
    st.markdown("""
    ### ¡Bienvenido al Panel de Auditoría Interna Gratuito!
    Este sistema utiliza Inteligencia Artificial de Código Abierto para auditar **AISC 207**.
    
    **Instrucciones:**
    1. Introduce tu API Key gratuita de Groq en la barra lateral.
    2. Haz clic en **"Iniciar Auditoría Interna"**.
    """)
    
    if st.button("🚀 Iniciar Auditoría Interna", type="primary"):
        if not api_key:
            st.error("⚠️ Debes ingresar tu Groq API Key en la barra lateral para iniciar.")
        else:
            st.session_state.fase = "AUDITANDO"
            SYSTEM_PROMPT = """
            Eres un Auditor Líder experto de la AISC. Evalúas el cumplimiento de AISC 207 (Capítulos 1 y 2) para certificación BU.
            Estructura de evaluación por cada documento:
            1. DICTAMEN: [CUMPLE / CUMPLE PARCIAL / NO CONFORMIDAD]
            2. REFERENCIA NORMATIVA: (Citar sección de AISC 207 o AWS D1.1).
            3. ANÁLISIS DETALLADO.
            4. ACCIÓN RECOMENDADA.
            """
            st.session_state.messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "assistant", "content": "Saludos. Damos inicio formal a la auditoría interna bajo AISC 207 (BU). Por favor, proporcione la Especificación de Procedimiento de Soldadura (WPS) más crítica de su taller o suba el documento para comenzar."}
            ]
            st.rerun()

elif st.session_state.fase == "AUDITANDO":
    st.markdown('<div class="status-box">🟢 <b>Estado:</b> Auditoría en progreso.</div>', unsafe_allow_html=True)
    
    if st.button("🛑 Finalizar Auditoría y Generar Reporte"):
        st.session_state.fase = "TERMINADA"
        st.rerun()
        
    st.write("---")
    
    # Inicializar cliente Groq
    client = Groq(api_key=api_key)
    
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    uploaded_file = st.file_uploader("Adjuntar evidencia en PDF", type=["pdf"])
    file_content = ""
    if uploaded_file is not None:
        st.info(f"📄 Archivo preparado: {uploaded_file.name}")
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_content += page.extract_text() + "\n"

    if user_input := st.chat_input("Escribe aquí..."):
        if file_content:
            full_user_message = f"[ARCHIVO: {uploaded_file.name}]\n\nContenido:\n{file_content}\n\nComentario: {user_input}"
        else:
            full_user_message = user_input

        st.session_state.messages.append({"role": "user", "content": full_user_message})
        with st.chat_message("user"):
            st.markdown(user_input if not uploaded_file else f"📄 {uploaded_file.name} — {user_input}")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Usamos el modelo rápido y potente Llama 3 70B de Meta
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

elif st.session_state.fase == "TERMINADA":
    st.markdown('<div class="status-box" style="background-color: #ECFDF5; border-left-color: #10B981;">✅ <b>Auditoría Finalizada</b></div>', unsafe_allow_html=True)
    
    reporte_texto = "====================================================\n        INFORME DE AUDITORÍA INTERNA AISC 207\n====================================================\n\n"
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            reporte_texto += f"► Empresa: {msg['content'][:200]}...\n"
        elif msg["role"] == "assistant":
            reporte_texto += f"  Auditor:\n{msg['content']}\n\n----------------------------------------------------\n"
            
    st.download_button(
        label="💾 Guardar Archivo del Reporte (.txt)",
        data=reporte_texto,
        file_name="Informe_AISC207.txt",
        mime="text/plain"
    )
    
    if st.button("🔄 Iniciar Nueva Auditoría"):
        st.session_state.fase = "INICIO"
        st.session_state.messages = []
        st.rerun()
