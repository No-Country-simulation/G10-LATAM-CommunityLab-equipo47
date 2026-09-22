"""
CommunityLab - Motor Inteligente de Transformación y Distribución para Comunidades Digitales
Hackathon ONE G10 - Oracle Next Education & Alura
Punto de Entrada Principal (Streamlit)
"""
import streamlit as st
from modules.auth import check_login, render_login_form, render_user_sidebar
from modules.ui import get_lucide
from views.ingestion import render_ingestion_view
from views.pipeline_ia import render_pipeline_view
from views.curaduria import render_curatorship_view
from views.dashboard import render_dashboard_view
from views.almacenamiento_oci import render_oci_storage_view

# Configuración de página (limpia, sin emojis)
st.set_page_config(
    page_title="CommunityLab | ONE G10",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de estilos de producto SaaS moderno y humanizado
st.markdown(
    """
    <style>
    /* Tipografía y acabados suaves */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s ease-in-out;
        border: 1px solid #CBD5E1;
    }
    .stButton>button:hover {
        border-color: #94A3B8;
        background-color: #F8FAFC;
    }
    .stMetric {
        background: #FFFFFF;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    }
    /* Limpieza de bordes en radios */
    div[role="radiogroup"] > label {
        padding: 6px 10px;
        border-radius: 8px;
        margin-bottom: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 1. Verificación de Autenticación
if not check_login():
    render_login_form()
    st.stop()

# 2. Barra Lateral y Navegación
with st.sidebar:
    logo_svg = get_lucide("sparkles", size=22, color="#E04F16")
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #E2E8F0;">
            <div style="background: #FFF1EE; border: 1px solid #FFD8CE; padding: 8px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                {logo_svg}
            </div>
            <div>
                <h3 style="margin: 0; color: #0F172A; font-size: 1.15rem; font-weight: 700; letter-spacing: -0.01em;">CommunityLab</h3>
                <span style="font-size: 0.78rem; color: #64748B;">Motor de Contenidos & MarTech</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    opciones = [
        "1. Ingestión de Datos",
        "2. Pipeline de IA & Router",
        "3. Panel de Curaduría",
        "4. Dashboard de Sentimiento",
        "5. OCI Object Storage"
    ]

    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>Módulos de Trabajo</p>", unsafe_allow_html=True)
    
    opcion_menu = st.radio(
        "Navegación:",
        opciones,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    render_user_sidebar()

    st.markdown(
        """
        <div style="margin-top: 1rem; padding: 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; font-size: 0.75rem; color: #64748B;">
            <strong style="color: #334155;">Oracle Next Education</strong><br>
            Hackathon G10 · Always Free
        </div>
        """,
        unsafe_allow_html=True
    )

# 3. Router de Vistas
if opcion_menu == "1. Ingestión de Datos":
    render_ingestion_view()
elif opcion_menu == "2. Pipeline de IA & Router":
    render_pipeline_view()
elif opcion_menu == "3. Panel de Curaduría":
    render_curatorship_view()
elif opcion_menu == "4. Dashboard de Sentimiento":
    render_dashboard_view()
elif opcion_menu == "5. OCI Object Storage":
    render_oci_storage_view()
