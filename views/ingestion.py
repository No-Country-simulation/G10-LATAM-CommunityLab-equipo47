"""
Vista 1: Ingestión de Actividad Comunitaria.
Permite cargar y revisar los mensajes de la comunidad antes de pasarlos al motor de IA.
Diseño humano y modular (fácil de editar o desacoplar).
"""
import streamlit as st
import json
from pathlib import Path
import pandas as pd
from modules.ui import badge_header, get_lucide
from modules.mock_engine import process_community_payload

SAMPLES_DIR = Path("data/samples")

def render_ingestion_view():
    badge_header(
        icon_name="upload-cloud",
        title="Ingestión de Actividad Comunitaria",
        subtitle="Carga y previsualiza los mensajes orgánicos de Discord, Slack o Foros antes del análisis",
        color="#2563EB"
    )

    st.markdown(
        """
        En esta primera etapa, el sistema recibe las conversaciones de los estudiantes. 
        Puedes seleccionar uno de los **3 casos preparados para el hackathon** o cargar tu propio archivo de datos.
        """
    )

    # Selector de método de carga
    metodo = st.radio(
        "Origen de los datos:",
        ["Cargar Casos de Demostración (Requisitos del Hackathon)", "Subir archivo JSON o CSV personalizado"],
        horizontal=True
    )

    data_cargada = None

    if metodo == "Cargar Casos de Demostración (Requisitos del Hackathon)":
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 1rem 0 0.5rem 0;">
                {get_lucide('file-text', size=18, color='#475569')}
                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Selecciona un Caso de Prueba Realista</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("Interacciones de estudiantes de la comunidad ONE LATAM (empleabilidad, soporte técnico y recursos):")

        col1, col2, col3 = st.columns(3)

        ejemplo_seleccionado = None
        with col1:
            if st.button("Caso 1: Mariana (Logro Laboral)", use_container_width=True, help="Testimonio de contratación y duda sobre LangGraph"):
                ejemplo_seleccionado = "ejemplo_1_contratacion.json"
        with col2:
            if st.button("Caso 2: Soporte Técnico OCI", use_container_width=True, help="Dudas técnicas sobre autenticación OCI y límites de tokens"):
                ejemplo_seleccionado = "ejemplo_2_soporte_dudas.json"
        with col3:
            if st.button("Caso 3: Proyectos de la Comunidad", use_container_width=True, help="Presentación de proyecto destacado y pedido de apoyo"):
                ejemplo_seleccionado = "ejemplo_3_feedback_mixto.json"

        if not ejemplo_seleccionado and "raw_payload" not in st.session_state:
            ejemplo_seleccionado = "ejemplo_1_contratacion.json"

        if ejemplo_seleccionado:
            filepath = SAMPLES_DIR / ejemplo_seleccionado
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    data_cargada = json.load(f)
                    st.session_state["raw_payload"] = data_cargada
                    st.session_state["archivo_origen"] = ejemplo_seleccionado

    else:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 1rem 0 0.5rem 0;">
                {get_lucide('upload-cloud', size=18, color='#475569')}
                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Subir Archivo de Interacciones</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        uploaded_file = st.file_uploader("Formato soportado: .json o .csv", type=["json", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".json"):
                    data_cargada = json.load(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                    interacciones = []
                    for _, row in df.iterrows():
                        interacciones.append({
                            "autor": str(row.get("autor", "Miembro")),
                            "canal": str(row.get("canal", "#general")),
                            "tipo": str(row.get("tipo", "mensaje")),
                            "texto": str(row.get("texto", ""))
                        })
                    data_cargada = {
                        "origen_comunidad": "CSV_Importado",
                        "periodo_referencia": "Reciente",
                        "interacciones": interacciones
                    }
                st.session_state["raw_payload"] = data_cargada
                st.session_state["archivo_origen"] = uploaded_file.name
                st.success(f"Archivo cargado correctamente: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    # Mostrar la data activa si existe en session_state
    if "raw_payload" in st.session_state:
        payload = st.session_state["raw_payload"]
        st.divider()

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                {get_lucide('message-square', size=20, color='#2563EB')}
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1E293B;">Resumen del Lote Ingerido</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Canal de Origen", payload.get("origen_comunidad", "N/A"))
        c2.metric("Período de Referencia", payload.get("periodo_referencia", "N/A"))
        c3.metric("Mensajes en el lote", len(payload.get("interacciones", [])))

        # Tabla limpia para lectura humana
        interacciones = payload.get("interacciones", [])
        if interacciones:
            df_interacciones = pd.DataFrame(interacciones)
            cols_orden = [c for c in ["autor", "pais", "canal", "tipo", "texto"] if c in df_interacciones.columns]
            st.dataframe(df_interacciones[cols_orden], use_container_width=True, hide_index=True)

        with st.expander("Ver estructura técnica en JSON (según la pág. 4 del PDF)"):
            st.json(payload)

        # Botón de acción directa para procesar de inmediato
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            if st.button("Procesar este lote con IA ahora mismo", type="primary", use_container_width=True):
                paquete = process_community_payload(payload)
                st.session_state["generated_package"] = paquete
                st.session_state["curated_package"] = paquete.copy()
                st.success("Lote analizado con éxito. Puedes revisar los resultados en la pestaña 2 o pasar directo a Curaduría.")
        with col_btn2:
            st.caption("O puedes explorar el paso a paso en '2. Pipeline de IA & Router'.")
