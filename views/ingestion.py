"""
Vista 1: Ingestión de Actividad Comunitaria.
Permite cargar y revisar los mensajes de la comunidad antes de pasarlos al motor de IA.
Diseño orientado al sector de Educación Superior & Ecosistema ONE (Campus Virtual, Foros y Discord de Cátedra).
"""
import streamlit as st
import json
from io import BytesIO
from pathlib import Path
import pandas as pd
from modules.ui import badge_header, get_lucide, render_callout, clean_html
from modules.mock_engine import process_community_payload
from modules.session import load_payload, store_generated

SAMPLES_DIR = Path(__file__).resolve().parents[1] / "data" / "samples"

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
                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Selecciona un Caso de Demostración (Datasets Listos para Evaluar)</h4>
            </div>
            """),
            unsafe_allow_html=True
        )

        # 1. BOTÓN DESTACADO: CASO OFICIAL DEL PDF DE HACKATHON ONE G10
        with st.container(border=True):
            col_pdf_txt, col_pdf_btn = st.columns([3, 1])
            with col_pdf_txt:
                st.markdown(
                    clean_html(f"""
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: #FEF3C7; color: #92400E; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid #FDE68A;">
                            ESPECIFICACIÓN OFICIAL
                        </span>
                        <strong style="color: #0F172A; font-size: 0.98rem;">Caso Canónico</strong>
                    </div>
                    <p style="margin: 4px 0 0 0; font-size: 0.84rem; color: #64748B;">
                        Testimonio de <strong>Mariana Souza</strong> (contratada como Dev Jr IA tras proyecto LangChain + OCI) y duda técnica de <strong>Lucas Albuquerque</strong> (LangGraph / Router).
                    </p>
                    """),
                    unsafe_allow_html=True
                )
            with col_pdf_btn:
                if st.button("Cargar Caso Oficial PDF", type="primary", use_container_width=True, help="Carga exactamente el JSON de ejemplo especificado en las páginas 4 y 5 del PDF"):
                    ejemplo_seleccionado = "ejemplo_oficial_pdf_one_g10.json"

        st.caption("Otros casos representativos y canales de comunidad en vivo:")
        c1, c2, c3, c4 = st.columns(4)

        if "ejemplo_seleccionado" not in locals():
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

        # Segunda fila de canales realistas (Discord y Slack)
        c5, c6 = st.columns(2)
        with c5:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #5865F2; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                    {get_lucide('message-square', size=14, color='#5865F2')}
                    DISCORD COMUNIDAD TECH (14 MSGS)
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 5: Discord Comunidad ONE LATAM", use_container_width=True, help="14 mensajes reales de Discord: contrataciones en Globant y MeLi, dudas de SDK de OCI y Streamlit"):
                ejemplo_seleccionado = "ejemplo_5_discord_comunidad_one.json"

        # Segunda fila de canales realistas (Discord, Slack y GitHub)
        c5, c6, c7 = st.columns(3)
        with c5:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #5865F2; margin-bottom: 4px; display: flex; align-items: center; gap: 4px;">
                    {get_lucide('message-square', size=14, color='#5865F2')}
                    DISCORD COMUNIDAD (14 MSGS)
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 5: Discord ONE LATAM", use_container_width=True, help="14 mensajes reales de Discord: contrataciones en Globant y MeLi, dudas de SDK de OCI y Streamlit"):
                ejemplo_seleccionado = "ejemplo_5_discord_comunidad_one.json"

        with c6:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #E11D48; margin-bottom: 4px; display: align-items: center; gap: 4px;">
                    {get_lucide('users', size=14, color='#E11D48')}
                    SLACK ALUMNI (6 MSGS)
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 6: Slack Alumni Network", use_container_width=True, help="6 mensajes de egresados de ONE en la industria: Tech Leads, buenas prácticas OCI y mentorías"):
                ejemplo_seleccionado = "ejemplo_6_slack_alumni_tech.json"

        with c7:
            st.markdown(
                clean_html(f"""
                <div style="font-size: 0.78rem; font-weight: 700; color: #0284C7; margin-bottom: 4px; display: align-items: center; gap: 4px;">
                    {get_lucide('github', size=14, color='#0284C7')}
                    GITHUB DISCUSSIONS (6 MSGS)
                </div>
                """),
                unsafe_allow_html=True
            )
            if st.button("Caso 7: GitHub Discussions", use_container_width=True, help="6 mensajes técnicos: buffer en memoria vs simulación local, schemas de Gemini y buenas prácticas"):
                ejemplo_seleccionado = "ejemplo_7_github_discussions_soporte.json"

        if not ejemplo_seleccionado and "raw_payload" not in st.session_state:
            ejemplo_seleccionado = "ejemplo_oficial_pdf_one_g10.json"

        if ejemplo_seleccionado:
            filepath = SAMPLES_DIR / ejemplo_seleccionado
            try:
                with filepath.open("r", encoding="utf-8-sig") as f:
                    load_payload(json.load(f), ejemplo_seleccionado)
            except (OSError, ValueError) as error:
                st.error(f"No se pudo cargar el caso de demostración: {error}")

    else:
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-1.2rem 0 0.6rem 0;">
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
                    data_cargada = json.loads(uploaded_file.getvalue().decode("utf-8-sig"))
                else:
                    df = pd.read_csv(BytesIO(uploaded_file.getvalue())).fillna("")
                    if "texto" not in df.columns:
                        raise ValueError("El CSV debe incluir una columna texto.")
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
                load_payload(data_cargada, uploaded_file.name)
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
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {get_lucide('message-square', size=20, color='#2563EB')}
                    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1E293B;">Resumen del Lote Comunitario Activo</h3>
                </div>
                <span style="background: #EFF6FF; color: #1D4ED8; font-size: 0.82rem; font-weight: 700; padding: 4px 12px; border-radius: 8px; border: 1px solid #BFDBFE;">
                    Archivo Activo: {st.session_state.get('archivo_origen', 'Lote')}
                </span>
            </div>
            """),
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Comunidad de Origen", payload.get("origen_comunidad", "N/A").replace("_", " "))
        c2.metric("Período / Sprint", payload.get("periodo_referencia", "N/A").replace("_", " "))
        c3.metric("Mensajes Ingeridos", len(interacciones))
        testimonios_count = sum(1 for i in interacciones if i.get("tipo") in ["testimonio", "logro"])
        c4.metric("Testimonios para LinkedIn", testimonios_count)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        tab_chat, tab_tabla, tab_json = st.tabs([
            "Mensajes Orgánicos de la Comunidad",
            "Vista Tabular de Datos",
            "Estructura Técnica JSON"
        ])

        # TAB 1: VISTA CHAT ORGANICO
        with tab_chat:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 8px; margin: 0.6rem 0 1rem 0;">
                    {get_lucide('message-square', size=18, color='#2563EB')}
                    <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Mensajes de la Comunidad en Canales Monitoreados</h4>
                </div>
                """),
                unsafe_allow_html=True
            )
            if interacciones:
                for idx, item in enumerate(interacciones):
                    autor = item.get("autor", "Miembro")
                    canal = item.get("canal", "#general")
                    tipo = item.get("tipo", "mensaje")
                    texto = item.get("texto", "")
                    pais = item.get("pais", "LATAM")
                    carrera = item.get("carrera", "")
                    fecha = item.get("fecha", "Reciente")

                    # Color según tipo
                    if tipo in ["testimonio", "logro"]:
                        tipo_color = "#059669"
                        tipo_bg = "#ECFDF5"
                        tipo_label = "LOGRO / EMPLEABILIDAD"
                    elif tipo in ["pregunta_tecnica", "duda"]:
                        tipo_color = "#2563EB"
                        tipo_bg = "#EFF6FF"
                        tipo_label = "PREGUNTA TÉCNICA"
                    elif tipo in ["alerta_apoyo", "dificultades"]:
                        tipo_color = "#DC2626"
                        tipo_bg = "#FEF2F2"
                        tipo_label = "ALERTA DE RETENCIÓN"
                    else:
                        tipo_color = "#7C3AED"
                        tipo_bg = "#F5F3FF"
                        tipo_label = tipo.replace("_", " ").upper()

                    sub_info = f" · {carrera}" if carrera else ""

                    with st.container(border=True):
                        st.markdown(
                            clean_html(f"""
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                                <div>
                                    <strong style="color: #0F172A; font-size: 0.95rem;">{autor}</strong>
                                    <span style="color: #64748B; font-size: 0.8rem; margin-left: 6px;">({pais}{sub_info})</span>
                                    <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 2px;">
                                        Canal: <code style="color: #475569; background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{canal}</code> · {fecha}
                                    </div>
                                </div>
                                <span style="background: {tipo_bg}; color: {tipo_color}; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; border: 1px solid {tipo_color}30;">
                                    {tipo_label}
                                </span>
                            </div>
                            <div style="color: #334155; font-size: 0.91rem; line-height: 1.5; margin-top: 6px;">
                                {texto}
                            </div>
                            """),
                            unsafe_allow_html=True
                        )
            else:
                st.info("No hay interacciones para mostrar.")

        # TAB 2: VISTA TABULAR
        with tab_tabla:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 8px; margin: 0.6rem 0 0.8rem 0;">
                    {get_lucide('bar-chart-3', size=18, color='#2563EB')}
                    <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Tabla Normalizada de Mensajes</h4>
                </div>
                """),
                unsafe_allow_html=True
            )
            if interacciones:
                df_interacciones = pd.DataFrame(interacciones)
                cols_disponibles = [c for c in ["autor", "pais", "carrera", "rol", "canal", "tipo", "texto"] if c in df_interacciones.columns]
                
                filtro_canal = st.selectbox(
                    "Filtrar interacciones por canal:",
                    ["Todos los canales"] + sorted(list(df_interacciones["canal"].unique())),
                    index=0,
                    key="filtro_canales_ingestion"
                )
                
                if filtro_canal != "Todos los canales":
                    df_mostrar = df_interacciones[df_interacciones["canal"] == filtro_canal]
                else:
                    df_mostrar = df_interacciones

                st.dataframe(df_mostrar[cols_disponibles], use_container_width=True, hide_index=True)

        # TAB 3: VISTA JSON
        with tab_json:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 8px; margin: 0.6rem 0 0.8rem 0;">
                    {get_lucide('file-text', size=18, color='#2563EB')}
                    <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Payload JSON Oficial Ingerido</h4>
                </div>
                """),
                unsafe_allow_html=True
            )
            st.json(payload)

        # Botón de acción directa para procesar de inmediato
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            if st.button("Ejecutar Pipeline de IA y Router Condicional", type="primary", use_container_width=True):
                with st.spinner("Analizando el lote y generando contenido..."):
                    store_generated(process_community_payload(payload))
                st.success("Lote analizado con éxito. Continúa en '2. Pipeline de IA & Router' para revisar las bifurcaciones y los activos generados.")
        with col_btn2:
            st.caption("Cumplimiento estricto con el esquema JSON oficial del Hackathon ONE G10.")
