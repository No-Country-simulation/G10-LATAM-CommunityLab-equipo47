"""
Vista 2: Pipeline de Inteligencia Artificial & Router Condicional.
Ejecuta el análisis de sentimiento, categorización de temas y orquestación de copys.
Diseño humano y profesional con iconos de Lucide (lucide.dev).
"""
import streamlit as st
import time
from modules.ui import badge_header, get_lucide, render_tag
from modules.mock_engine import process_community_payload

def render_pipeline_view():
    badge_header(
        icon_name="sparkles",
        title="Pipeline de IA & Router Condicional",
        subtitle="Analiza sentimiento, extrae temas clave y bifurca el contenido automáticamente",
        color="#7C3AED"
    )

    if "raw_payload" not in st.session_state:
        st.info("Para comenzar, carga un lote de mensajes desde el menú '1. Ingestión de Datos'.")
        return

    payload = st.session_state["raw_payload"]

    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 14px; border-radius: 8px;">
                <span style="color: #64748B; font-size: 0.85rem;">Lote cargado:</span>
                <strong style="color: #0F172A; display: block;">{payload.get('origen_comunidad')} ({len(payload.get('interacciones', []))} interacciones)</strong>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_cfg2:
        modelo = st.selectbox("Motor de Lenguaje", ["Google Gemini 2.5 Flash", "OpenAI GPT-4o", "Modo Simulado / Demostración"])

    if st.button("Ejecutar Análisis y Generación de Contenidos", type="primary", use_container_width=True):
        with st.status("Orquestando flujo de inteligencia artificial...", expanded=True) as status:
            st.write("Ingestión y limpieza de los textos comunitarios...")
            time.sleep(0.3)
            st.write("Análisis de sentimiento y extracción de temas principales...")
            time.sleep(0.4)
            st.write("Evaluación en Router Condicional (Bifurcación: logros vs dudas técnicas)...")
            time.sleep(0.3)
            st.write("Redacción de copys multicanal adaptados para LinkedIn, Newsletter y FAQ...")
            time.sleep(0.3)
            
            paquete = process_community_payload(payload)
            st.session_state["generated_package"] = paquete
            st.session_state["curated_package"] = paquete.copy()
            status.update(label="Pipeline ejecutado exitosamente", state="complete", expanded=False)

    if "generated_package" in st.session_state:
        paquete = st.session_state["generated_package"]
        resumen = paquete.get("resumen_comunidad", {})
        activos = paquete.get("activos_distribucion_generados", {})

        st.divider()

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                {get_lucide('bar-chart-3', size=20, color='#7C3AED')}
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1E293B;">Diagnóstico del Lote</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Mensajes Analizados", resumen.get("total_interacciones_procesadas", 0))
        m2.metric("Sentimiento Predominante", resumen.get("sentimiento_predominante", "N/A"))
        m3.metric("Temas Detectados", len(resumen.get("temas_principales", [])))

        st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #475569; margin-top: 1rem; margin-bottom: 0.4rem;'>Temas Clave Extraídos:</p>", unsafe_allow_html=True)
        tags_html = "".join([render_tag(t, "#F3E8FF", "#6B21A8") for t in resumen.get("temas_principales", [])])
        st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.6rem;">
                {get_lucide('git-fork', size=20, color='#7C3AED')}
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1E293B;">Decisiones del Router Condicional</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            * **Condición de Logro o Testimonio:** Al detectar mensajes positivos de contratación o avance, se activó automáticamente la redacción del **Post para LinkedIn** y la sección **Logro de la Semana** en Newsletter.
            * **Condición de Duda Técnica:** Al detectar consultas técnicas recurrentes, se derivó la temática al generador de **Tips Rápidos / FAQ** para soporte a la comunidad.
            """
        )

        with st.expander("Ver JSON estructurado de salida (formato oficial del PDF)"):
            st.json(paquete)

        st.markdown(
            f"""
            <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 12px; border-radius: 8px; display: flex; align-items: center; gap: 10px; margin-top: 1rem;">
                {get_lucide('check-circle-2', size=20, color='#059669')}
                <span style="color: #065F46; font-size: 0.95rem;">
                    Activos de marketing generados. Pasa al <strong>Panel de Curaduría</strong> para revisar y aprobar los copys antes de publicarlos.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
