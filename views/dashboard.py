"""
Vista 4: Dashboard de Salud y Sentimiento de la Comunidad.
Monitorea indicadores clave de satisfacción, canales con mayor actividad y alertas tempranas.
Diseño modular y fácil de entender.
"""
import streamlit as st
import pandas as pd
from modules.ui import badge_header, get_lucide

def render_dashboard_view():
    badge_header(
        icon_name="bar-chart-3",
        title="Dashboard de Salud y Sentimiento",
        subtitle="Monitoreo en tiempo real del clima de la comunidad y alertas tempranas de apoyo",
        color="#D97706"
    )

    if "raw_payload" not in st.session_state:
        st.info("Carga un lote en '1. Ingestión de Datos' para calcular las métricas en tiempo real.")
        interacciones = []
    else:
        payload = st.session_state["raw_payload"]
        interacciones = payload.get("interacciones", [])

    total_msg = len(interacciones)
    testimonios_cnt = sum(1 for i in interacciones if i.get("tipo") in ["testimonio", "logro", "agradecimiento"])
    dudas_cnt = sum(1 for i in interacciones if i.get("tipo") in ["pregunta_tecnica", "duda", "alerta_apoyo"])
    otros_cnt = total_msg - (testimonios_cnt + dudas_cnt)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Interacciones", total_msg)
    col2.metric("Logros y Testimonios", testimonios_cnt, delta="Impacto positivo")
    col3.metric("Dudas Técnicas", dudas_cnt, delta="Atención requerida" if dudas_cnt > 0 else "Al día")
    col4.metric("Canales Activos", len(set(i.get("canal", "") for i in interacciones)) if interacciones else 0)

    st.divider()

    col_chart, col_alerts = st.columns([3, 2])

    with col_chart:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                {get_lucide('bar-chart-3', size=18, color='#D97706')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Distribución de Tipos de Mensajes</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        if total_msg > 0:
            df_chart = pd.DataFrame({
                "Categoría": ["Logros y Testimonios", "Dudas Técnicas", "Recursos y Sugerencias"],
                "Cantidad": [testimonios_cnt, dudas_cnt, max(0, otros_cnt)]
            }).set_index("Categoría")
            st.bar_chart(df_chart)
        else:
            st.caption("No hay datos cargados para graficar.")

    with col_alerts:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                {get_lucide('alert-circle', size=18, color='#DC2626')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Alertas de Soporte Comunitario</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        alertas = [i for i in interacciones if i.get("tipo") in ["alerta_apoyo", "pregunta_tecnica"]]
        if alertas:
            for a in alertas:
                with st.container(border=True):
                    pais_tag = f" ({a.get('pais')})" if a.get('pais') else ""
                    st.markdown(f"**{a.get('autor')}**{pais_tag} en `{a.get('canal')}`")
                    st.caption(f"_{a.get('texto')[:130]}..._")
        else:
            st.markdown(
                f"""
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 12px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                    {get_lucide('check-circle-2', size=18, color='#059669')}
                    <span style="color: #065F46; font-size: 0.9rem;">No hay alertas críticas pendientes de soporte en este lote.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
            {get_lucide('sparkles', size=18, color='#2563EB')}
            <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Recomendación Estratégica del Sistema</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    if testimonios_cnt > dudas_cnt:
        st.info(
            "Momento ideal para difusión: La comunidad está experimentando un pico de contrataciones y logros. "
            "Es una excelente oportunidad para publicar testimonios en LinkedIn para atraer nuevos talentos al programa ONE."
        )
    elif dudas_cnt > 0:
        st.warning(
            "Oportunidad de refuerzo formativo: Se detectaron dudas técnicas repetidas en temas específicos. "
            "Recomendamos programar una sesión en vivo ('Office Hours') o publicar una guía rápida en el foro."
        )
