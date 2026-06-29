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
st.markdown('<div class="sub-header">Módulo Automático y Gratuito con Llama-3</div>', unsafe_allow_html=True)

# Intentar jalar la API Key desde los Secrets de la plataforma
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = None

if "fase" not in st.session_state:
    st.session_state.fase = "INICIO"

if "messages" not in st.session_state:
    st.session_state.messages = []

SYSTEM_PROMPT = """
Eres un Auditor Líder experto de la AISC (American Institute of Steel Construction). 
Tu objetivo es evaluar de forma estricta, profesional y constructiva si la empresa cumple con el estándar AISC 207, específicamente los Capítulos 1 (SGC) y 2 (Requisitos para Fabricantes de Edificios - BU).

Cuando el usuario te suba un documento o te haga una consulta, debes analizarlo exhaustivamente y responder con la siguiente estructura estricta:
1. **DICTAMEN:** [CUMPLE / CUMPLE PARCIAL (Oportunidad de Mejora) / NO CONFORMIDAD]
2. **REFERENCIA NORMATIVA:** (Citar la sección específica de AISC 207 o AWS D1.1 si aplica).
3. **ANÁLISIS DETALLADO:** Explicación técnica de por qué se otorga ese dictamen.
4. **ACCIÓN RECOMENDADA:** Qué debe hacer el responsable de calidad para subsanar el hallazgo antes de la auditoría real.

Mantén un tono serio, corporativo, analítico y enfocado en la mejora continua.
"""

# 4. Flujo de Estados
if st.session_state.fase == "INICIO":
    st.markdown("""
    ### ¡Bienvenido al Panel de Auditoría Interna!
    Este sistema utiliza Inteligencia Artificial de Código Abierto para auditar **AISC 207**.
    
    **Instrucciones:**
    1. Asegúrate de haber configurado tu `GROQ_API_KEY` en los Secrets de Streamlit.
    2. Haz clic en el botón de abajo para iniciar la sesión de auditoría.
    """)
    
    if st.button("🚀 Iniciar Auditoría Interna", type="primary"):
        if not api_key:
            st.error("⚠️ No se encontró la variable GROQ_API_KEY en los Secrets de la aplicación. Configúrala en el panel de administración.")
        else:
            st.session_state.fase = "AUDITANDO"
            st.session_state.messages = [
                {"role": "assistant", "content": "Saludos. Damos inicio formal a la auditoría interna bajo AISC 207 (BU). Por favor, proporcione la Especificación de Procedimiento de Soldadura (WPS) más crítica de su taller o suba el documento en PDF para comenzar."}
            ]
            st.rerun()

elif st.session_state.fase == "AUDITANDO":
    st.markdown('<div class="status-box">🟢 <b>Estado:</b> Auditoría en progreso.</div>', unsafe_allow_html=True)
    
    if st.button("🛑 Finalizar Auditoría y Generar Reporte"):
        st.session_state.fase = "TERMINADA"
        st.rerun()
        
    st.write("---")
    
    client = Groq(api_key=api_key)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    uploaded_file = st.file_uploader("Adjuntar evidencia en PDF", type=["pdf"])
    file_content = ""
    if uploaded_file is not None:
        st.info(f"📄 Archivo preparado: {uploaded_file.name}")
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_content += page.extract_text() + "\n"

    if user_input := st.chat_input("Escribe tu respuesta aquí..."):
        if file_content:
            full_user_message = f"[ARCHIVO ADJUNTADO: {uploaded_file.name}]\n\nContenido extraído del documento:\n{file_content}\n\nComentario del usuario: {user_input}"
        else:
            full_user_message = user_input

        st.session_state.messages.append({"role": "user", "content": full_user_message})
        with st.chat_message("user"):
            st.markdown(user_input if not uploaded_file else f"📄 {uploaded_file.name} — {user_input}")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            payload_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                payload_messages.append({"role": m["role"], "content": m["content"]})
            
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=payload_messages,
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
    
    st.write("### Generar Reporte de Auditoría")
    
    reporte_texto = "====================================================\n        INFORME DE AUDITORÍA INTERNA AISC 207\n====================================================\n\n"
    reporte_texto += "ESTÁNDAR: AISC 207 (Building Fabricator Certification - BU)\n"
    reporte_texto += "AUDITOR: Auditor Inteligencia Artificial Líder SGC\n\n"
    reporte_texto += "----------------------------------------------------\n"
    reporte_texto += "DETALLE DE EVALUACIONES:\n"
    reporte_texto += "----------------------------------------------------\n\n"

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            if "[ARCHIVO ADJUNTADO:" in msg["content"]:
                lineas = msg["content"].split("\n")
                reporte_texto += f"► Evidencia: {lineas[0]}\n"
            else:
                reporte_texto += f"► Empresa: {msg['content']}\n"
        elif msg["role"] == "assistant":
            reporte_texto += f"\nEvaluación del Auditor:\n{msg['content']}\n"
            reporte_texto += "----------------------------------------------------\n"
            
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
