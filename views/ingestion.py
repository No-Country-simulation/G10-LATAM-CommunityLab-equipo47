"""
Vista 1: Ingestión de Actividad Comunitaria.
Permite cargar y revisar los mensajes de la comunidad antes de pasarlos al motor de IA.
Diseño orientado al sector de Educación Superior & Ecosistema ONE (Campus Virtual, Foros y Discord de Cátedra).
"""
import streamlit as st
import json
from pathlib import Path
import pandas as pd
from modules.ui import badge_header, get_lucide, render_callout, clean_html
from modules.mock_engine import process_community_payload

SAMPLES_DIR = Path("data/samples")

def render_ingestion_view():
    badge_header(
        icon_name="upload-cloud",
        title="Ingestión de Actividad Comunitaria",
        subtitle="Carga y previsualiza los mensajes orgánicos de Campus Virtual, Discord y Foros Académicos antes del análisis",
        color="#2563EB",
        target_pill="Sector: Educación Superior & Ecosistema ONE"
    )

    render_callout(
        text="En esta etapa el sistema ingesta las conversaciones orgánicas generadas por estudiantes, graduados y docentes en el campus virtual. "
             "Estos datos sin procesar alimentan el motor de IA para detectar historias de éxito, cuellos de botella en cátedras y alertas de retención.",
        title="Flujo de Ingestión Automática",
        icon_name="info",
        color="#2563EB"
    )

    # Selector de método de carga
    metodo = st.radio(
        "Origen de los datos:",
        ["Cargar Casos de Demostración (Educación Superior & Ecosistema ONE)", "Subir archivo JSON o CSV personalizado"],
        horizontal=True
    )

    data_cargada = None

    if metodo.startswith("Cargar Casos de Demostración"):
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 1.2rem 0 0.6rem 0;">
                {get_lucide('book-open', size=19, color='#1E293B')}
                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Selecciona un Caso de Estudio Universitario</h4>
            </div>
            """),
            unsafe_allow_html=True
        )
        st.caption("Casos representativos con datasets ampliados (12 a 14 mensajes por lote):")

        c1, c2, c3, c4 = st.columns(4)

        ejemplo_seleccionado = None
        with c1:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #059669; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                    {get_lucide('award', size=14, color='#059669')}
                    EMPLEABILIDAD
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 1: Inserción Laboral", use_container_width=True, help="12 mensajes: Testimonios de contratación en IA y Cloud antes de defender tesis"):
                ejemplo_seleccionado = "ejemplo_1_contratacion.json"

        with c2:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #2563EB; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                    {get_lucide('cpu', size=14, color='#2563EB')}
                    SOPORTE CÁTEDRA
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 2: Cátedra Cloud", use_container_width=True, help="12 mensajes: Dudas de OCI Always Free, llaves PEM y variables de entorno"):
                ejemplo_seleccionado = "ejemplo_2_soporte_dudas.json"

        with c3:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #D97706; margin-bottom: 4px; display: align-items: center; gap: 4px;">
                    {get_lucide('heart', size=14, color='#D97706')}
                    BIENESTAR Y RETENCIÓN
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 3: Tutorías Pares", use_container_width=True, help="14 mensajes: Alertas de sobrecarga académica y red de apoyo par"):
                ejemplo_seleccionado = "ejemplo_3_feedback_mixto.json"

        with c4:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #7C3AED; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                    {get_lucide('sparkles', size=14, color='#7C3AED')}
                    HACKATHON & FERIA
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 4: Feria de Innovación", use_container_width=True, help="12 mensajes: Proyectos finales en OCI, pitches y pre-incubación"):
                ejemplo_seleccionado = "ejemplo_4_innovacion_hackathon.json"

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
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 1.2rem 0 0.6rem 0;">
                {get_lucide('upload-cloud', size=18, color='#475569')}
                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Subir Archivo de Interacciones</h4>
            </div>
            """),
            unsafe_allow_html=True
        )
        uploaded_file = st.file_uploader("Formato soportado: .json o .csv (Discord, Moodle o Slack)", type=["json", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".json"):
                    data_cargada = json.load(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                    interacciones = []
                    for _, row in df.iterrows():
                        interacciones.append({
                            "autor": str(row.get("autor", "Estudiante")),
                            "pais": str(row.get("pais", "LATAM")),
                            "carrera": str(row.get("carrera", "Ingeniería")),
                            "canal": str(row.get("canal", "#general")),
                            "tipo": str(row.get("tipo", "mensaje")),
                            "texto": str(row.get("texto", ""))
                        })
                    data_cargada = {
                        "origen_comunidad": "Campus_CSV_Importado",
                        "periodo_referencia": "Reciente",
                        "target_sector": "Educacion_Superior",
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
        interacciones = payload.get("interacciones", [])
        st.divider()

        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {get_lucide('message-square', size=20, color='#2563EB')}
                    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1E293B;">Resumen del Lote Académico Ingerido</h3>
                </div>
                <span style="background: #EFF6FF; color: #1D4ED8; font-size: 0.8rem; font-weight: 700; padding: 4px 10px; border-radius: 6px; border: 1px solid #BFDBFE;">
                    Archivo: {st.session_state.get('archivo_origen', 'Lote Activo')}
                </span>
            </div>
            """),
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Canal de Origen", payload.get("origen_comunidad", "N/A").replace("_", " "))
        c2.metric("Período Académico", payload.get("periodo_referencia", "N/A").replace("_", " "))
        c3.metric("Mensajes en el Lote", len(interacciones))
        testimonios_count = sum(1 for i in interacciones if i.get("tipo") in ["testimonio", "logro"])
        c4.metric("Testimonios Detectados", testimonios_count)

        # Tabla limpia para lectura humana con filtro
        if interacciones:
            df_interacciones = pd.DataFrame(interacciones)
            cols_disponibles = [c for c in ["autor", "pais", "carrera", "rol", "canal", "tipo", "texto"] if c in df_interacciones.columns]
            
            filtro_canal = st.selectbox(
                "Filtrar interacciones por canal:",
                ["Todos los canales"] + sorted(list(df_interacciones["canal"].unique())),
                index=0
            )
            
            if filtro_canal != "Todos los canales":
                df_mostrar = df_interacciones[df_interacciones["canal"] == filtro_canal]
            else:
                df_mostrar = df_interacciones

            st.dataframe(df_mostrar[cols_disponibles], use_container_width=True, hide_index=True)

        with st.expander("Ver estructura técnica en JSON (según la pág. 4 del PDF)"):
            st.json(payload)

        # Botón de acción directa para procesar de inmediato
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            if st.button("🚀 Ejecutar Pipeline de IA & Router con este lote", type="primary", use_container_width=True):
                paquete = process_community_payload(payload)
                st.session_state["generated_package"] = paquete
                st.session_state["curated_package"] = paquete.copy()
                st.success("¡Lote analizado con éxito! Pasa al menú '2. Pipeline de IA & Router' para ver las bifurcaciones y los activos generados.")
        with col_btn2:
            st.caption("Cumplimiento estricto con el esquema JSON oficial del Hackathon ONE G10.")
