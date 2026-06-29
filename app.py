import streamlit as st
from openai import OpenAI
import pypdf
import io

# 1. Configuración de la página
st.set_page_config(page_title="Auditor IA - AISC 207 Cloud", page_icon="🏗️", layout="centered")

# Estilos personalizados para darle un look corporativo y profesional
st.markdown("""
    <style>
    .main-header { font-size:24pt; font-weight:bold; color:#1E3A8A; margin-bottom:5px; }
    .sub-header { font-size:12pt; color:#4B5563; margin-bottom:20px; }
    .status-box { padding: 15px; border-radius: 5px; margin-bottom: 20px; background-color: #EFF6FF; border-left: 5px solid #1D4ED8; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏗️ Sistema de Auditoría Interna IA — AISC 207</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Módulo de Preparación Automatizada para Certificación AISC BU</div>', unsafe_allow_html=True)

# 2. Configuración de la API Key en la barra lateral
st.sidebar.header("⚙️ Configuración")
api_key = st.sidebar.text_input("Introduce tu OpenAI API Key:", type="password")

# 3. Inicialización de variables de estado de la sesión (State Management)
if "fase" not in st.session_state:
    st.session_state.fase = "INICIO"  # Fases: INICIO, AUDITANDO, TERMINADA

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Flujo de Estados del Aplicativo
if st.session_state.fase == "INICIO":
    st.markdown("""
    ### ¡Bienvenido al Panel de Auditoría Interna!
    Este sistema simula el comportamiento de un **Auditor Líder de AISC** bajo el estándar **AISC 207 (Capítulos 1 y 2)**.
    
    **Instrucciones:**
    1. Introduce tu API Key de OpenAI en la barra lateral.
    2. Haz clic en **"Iniciar Auditoría Interna"** para que el auditor comience a solicitarte evidencias.
    3. Sube tus documentos (WPS, PQR, calificaciones, MTRs) a demanda y responde al chatbot.
    4. Cuando consideres que has entregado todo, presiona **"Finalizar y Solicitar Informe"**.
    """)
    
    if st.button("🚀 Iniciar Auditoría Interna", type="primary"):
        if not api_key:
            st.error("⚠️ Debes ingresar una OpenAI API Key válida en la barra lateral antes de iniciar.")
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
                {"role": "assistant", "content": "Saludos. Damos inicio formal a la auditoría interna bajo AISC 207 (BU). Para comenzar, por favor proporcione la **Especificación de Procedimiento de Soldadura (WPS)** más crítica de su taller, junto con su respectivo **PQR** de respaldo, o indique si es precalificada."}
            ]
            st.rerun()

elif st.session_state.fase == "AUDITANDO":
    st.markdown('<div class="status-box">🟢 <b>Estado:</b> Auditoría en progreso. El auditor está esperando tus respuestas o archivos adjuntos.</div>', unsafe_allow_html=True)
    
    # Botón para terminar la auditoría visible en la parte superior derecha/lateral
    if st.button("🛑 Finalizar Auditoría y Generar Reporte", type="secondary"):
        st.session_state.fase = "TERMINADA"
        st.rerun()
        
    st.write("---")
    
    # Mostrar el chat
    client = OpenAI(api_key=api_key)
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Carga de archivos
    uploaded_file = st.file_uploader("Adjuntar evidencia en PDF (WPS, PQR, Certificados, etc.)", type=["pdf"])
    file_content = ""
    if uploaded_file is not None:
        st.info(f"📄 Archivo preparado para enviar: {uploaded_file.name}")
        pdf_reader = pypdf.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_content += page.extract_text() + "\n"

    # Input del chat
    if user_input := st.chat_input("Escribe tu respuesta al auditor aquí..."):
        if file_content:
            full_user_message = f"[ARCHIVO ADJUNTADO: {uploaded_file.name}]\n\nContenido:\n{file_content}\n\nComentario del usuario: {user_input}"
        else:
            full_user_message = user_input

        st.session_state.messages.append({"role": "user", "content": full_user_message})
        with st.chat_message("user"):
            st.markdown(user_input if not uploaded_file else f"📄 Archivo: {uploaded_file.name} — {user_input}")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

elif st.session_state.fase == "TERMINADA":
    st.markdown('<div class="status-box" style="background-color: #ECFDF5; border-left-color: #10B981;">✅ <b>Auditoría Finalizada:</b> Las evaluaciones han concluido con éxito y el informe técnico está listo para procesarse.</div>', unsafe_allow_html=True)
    
    st.write("### Resumen del Cierre")
    st.write("El auditor de IA ha recopilado todas las evidencias compartidas en el chat y ha estructurado la lista de hallazgos. Haz clic abajo para consolidar y descargar tu Reporte Formal de Auditoría Interna.")
    
    if st.button("📊 Descargar Reporte Formal en TXT", type="primary"):
        # Generar el reporte compilando el historial de hallazgos de forma limpia
        reporte_texto = "====================================================\n"
        reporte_texto += "        INFORME DE AUDITORÍA INTERNA AISC 207\n"
        reporte_texto += "====================================================\n\n"
        reporte_texto += "ESTÁNDAR: AISC 207-20 (Building Fabricator Certification - BU)\n"
        reporte_texto += "AUDITOR: Auditor Inteligencia Artificial Líder SGC\n\n"
        reporte_texto += "----------------------------------------------------\n"
        reporte_texto += "LOG DE HALLAZGOS Y EVALUACIONES DISCUTIDAS:\n"
        reporte_texto += "----------------------------------------------------\n\n"
        
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                if "[ARCHIVO ADJUNTADO:" in msg["content"]:
                    lineas = msg["content"].split("\n")
                    reporte_texto += f"► Evidencia Presentada: {lineas[0]}\n"
                else:
                    reporte_texto += f"► Respuesta de la Empresa: {msg['content']}\n"
            elif msg["role"] == "assistant":
                reporte_texto += f"  Evaluación del Auditor:\n{msg['content']}\n\n"
                reporte_texto += "----------------------------------------------------\n"
                
        # Botón nativo de descarga en Streamlit
        st.download_button(
            label="💾 Guardar Archivo del Reporte (.txt)",
            data=reporte_texto,
            file_name="Informe_Auditoria_Interna_AISC207.txt",
            mime="text/plain"
        )
        
    if st.button("🔄 Iniciar una Nueva Auditoría"):
        st.session_state.fase = "INICIO"
        st.session_state.messages = []
        st.rerun()
