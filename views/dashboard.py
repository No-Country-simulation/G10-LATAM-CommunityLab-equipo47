"""
Vista 4: Dashboard de Salud y Sentimiento de la Comunidad.
Monitorea indicadores clave de satisfacción, canales con mayor actividad y alertas tempranas de apoyo.
Especializado para el sector de Educación Tecnológica Superior & Ecosistema ONE.
"""
import streamlit as st
import pandas as pd
from modules.ui import badge_header, get_lucide, render_kpi_card, render_callout, clean_html

def render_dashboard_view():
    badge_header(
        icon_name="bar-chart-3",
        title="Dashboard de Salud y Sentimiento",
        subtitle="Monitoreo en tiempo real del clima de la comunidad universitaria y alertas tempranas de apoyo estudiantil",
        color="#D97706",
        target_pill="Sector: Educación Superior & Ecosistema ONE"
    )

    if "raw_payload" not in st.session_state:
        render_callout(
            text="Carga un lote en '1. Ingestión de Datos' para calcular las métricas en tiempo real.",
            title="Sin datos para analizar",
            icon_name="info",
            color="#2563EB"
        )
        interacciones = []
    else:
        payload = st.session_state["raw_payload"]
        interacciones = payload.get("interacciones", [])

    total_msg = len(interacciones)
    testimonios_cnt = sum(1 for i in interacciones if i.get("tipo") in ["testimonio", "logro"])
    dudas_cnt = sum(1 for i in interacciones if i.get("tipo") in ["pregunta_tecnica", "duda"])
    alertas_cnt = sum(1 for i in interacciones if i.get("tipo") in ["alerta_apoyo", "dificultades"])
    otros_cnt = total_msg - (testimonios_cnt + dudas_cnt + alertas_cnt)

    # Métricas con estilo visual enriquecido
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_kpi_card("Total Interacciones", str(total_msg), "Mensajes analizados", "message-square", "#2563EB"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card("Logros y Grado", str(testimonios_cnt), "Casos para LinkedIn", "award", "#059669"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card("Consultas Cátedra", str(dudas_cnt), "Dudas de laboratorio", "cpu", "#7C3AED"), unsafe_allow_html=True)
    with col4:
        color_alerta = "#DC2626" if alertas_cnt > 0 else "#059669"
        sub_alerta = f"{alertas_cnt} alertas activas" if alertas_cnt > 0 else "Sin riesgo"
        st.markdown(render_kpi_card("Retención & Apoyo", str(alertas_cnt), sub_alerta, "alert-circle", color_alerta), unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    col_chart, col_alerts = st.columns([3, 2])

    with col_chart:
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                {get_lucide('bar-chart-3', size=19, color='#D97706')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Distribución de Tipos de Mensajes en el Campus</h4>
            </div>
            """),
            unsafe_allow_html=True
        )
        if total_msg > 0:
            df_chart = pd.DataFrame({
                "Categoría": ["Logros y Grado", "Consultas Técnicas", "Alertas de Apoyo", "Recursos y Sugerencias"],
                "Cantidad": [testimonios_cnt, dudas_cnt, alertas_cnt, max(0, otros_cnt)]
            }).set_index("Categoría")
            st.bar_chart(df_chart, color="#2563EB")

            # Desglose por canal
            df_interacciones = pd.DataFrame(interacciones)
            if "canal" in df_interacciones.columns:
                st.markdown("<h5 style='margin-top: 1rem; color: #334155; font-size: 0.95rem;'>Actividad por Canal del Campus Virtual:</h5>", unsafe_allow_html=True)
                conteo_canales = df_interacciones["canal"].value_counts()
                st.dataframe(pd.DataFrame({"Canal": conteo_canales.index, "Mensajes": conteo_canales.values}), hide_index=True, use_container_width=True)
        else:
            st.caption("No hay datos cargados para graficar.")

    with col_alerts:
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                {get_lucide('alert-circle', size=19, color='#DC2626')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Alertas Tempranas de Retención</h4>
            </div>
            """),
            unsafe_allow_html=True
        )
        alertas = [i for i in interacciones if i.get("tipo") in ["alerta_apoyo", "pregunta_tecnica"]]
        if alertas:
            # Mostrar hasta 4 alertas prioritarias
            for a in alertas[:4]:
                with st.container(border=True):
                    pais_tag = f" ({a.get('pais', 'LATAM')})"
                    carrera_tag = f" · {a.get('carrera', 'Ingeniería')}" if a.get('carrera') else ""
                    tipo_color = "#DC2626" if a.get("tipo") == "alerta_apoyo" else "#2563EB"
                    st.markdown(
                        clean_html(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <strong style="color: #0F172A; font-size: 0.9rem;">{a.get('autor')}{pais_tag}</strong>
                            <span style="font-size: 0.75rem; font-weight: 600; color: {tipo_color}; background: {tipo_color}14; padding: 2px 8px; border-radius: 4px;">
                                {a.get('tipo').replace('_', ' ').upper()}
                            </span>
                        </div>
                        <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 6px;">Canal: <code>{a.get('canal')}</code>{carrera_tag}</div>
                        """),
                        unsafe_allow_html=True
                    )
                    st.caption(f"_{a.get('texto')[:130]}..._")
        else:
            st.markdown(
                clean_html(f"""
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 14px; border-radius: 10px; display: flex; align-items: center; gap: 10px;">
                    {get_lucide('check-circle-2', size=20, color='#059669')}
                    <span style="color: #065F46; font-size: 0.9rem;">No se detectaron alertas críticas de deserción o sobrecarga en este lote.</span>
                </div>
                """),
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown(
        clean_html(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
            {get_lucide('sparkles', size=18, color='#2563EB')}
            <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Recomendación Estratégica para Gestión Académica</h4>
        </div>
        """),
        unsafe_allow_html=True
    )
    if alertas_cnt > 0:
        render_callout(
            text="Se detectaron estudiantes con dificultades para coordinar tiempos laborales con las entregas de laboratorio. "
                 "Recomendamos activar a la <strong>Red de Tutores Pares</strong> y habilitar talleres de apoyo sincrónicos este fin de semana.",
            title="Acción Prioritaria de Retención Estudiantil",
            icon_name="heart",
            color="#DC2626"
        )
    elif testimonios_cnt > dudas_cnt:
        render_callout(
            text="El sentimiento estudiantil es sumamente positivo gracias a contrataciones de grado y proyectos destacados en OCI. "
                 "Oportunidad inmejorable para que el equipo de Admisiones publique estos testimonios reales en LinkedIn y campañas de matriculación.",
            title="Momento Ideal de Difusión Institucional (UGC Marketing)",
            icon_name="award",
            color="#059669"
        )
    elif dudas_cnt > 0:
        render_callout(
            text="Se concentran dudas técnicas repetitivas sobre configuración de entornos cloud y límites de cuota Always Free. "
                 "Recomendamos al equipo docente publicar una cápsula o FAQ oficial en el campus virtual para evitar cuellos de botella en la entrega.",
            title="Oportunidad de Refuerzo en Cátedra",
            icon_name="book-open",
            color="#D97706"
        )
