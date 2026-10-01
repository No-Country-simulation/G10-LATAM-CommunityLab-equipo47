"""
CommunityLab - Motor Inteligente de Transformación y Distribución para Comunidades Digitales
Hackathon ONE G10 - LATAM · Equipo 47
Sector: Educación Superior & Comunidades Digitales de Aprendizaje
Punto de Entrada Principal (Streamlit)
"""
import sys
import os

# Garantizar que el directorio raíz del proyecto esté en sys.path (indispensable para Streamlit Cloud en Linux)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from modules.auth import check_login, render_login_form, render_user_sidebar

try:
    from modules.ui import get_lucide, GITHUB_REPO_URL, DEMO_URL, render_footer, clean_html
except ImportError:
    from modules.ui import get_lucide, GITHUB_REPO_URL, render_footer, clean_html
    DEMO_URL = "https://proyectohackathon-vmuqmx28sqeyagkyoebamt.streamlit.app/"

from views.ingestion import render_ingestion_view
from views.pipeline_ia import render_pipeline_view
from views.curaduria import render_curatorship_view
from views.dashboard import render_dashboard_view
from views.almacenamiento_oci import render_oci_storage_view

# Configuración de página
st.set_page_config(
    page_title="CommunityLab | Equipo 47 ONE LATAM",
    page_icon="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/layers.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales refinados con estética SaaS moderna y profesional
st.markdown(
    """
    <style>
    /* Ajuste para que la barra lateral quede arriba sin espacio muerto */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
    }
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0F172A;
    }

    /* Fondo general sutil */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Botones primarios y secundarios con estética refinada */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 0.55rem 1.1rem;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
        border: 1px solid #CBD5E1;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }
    .stButton>button:hover {
        border-color: #94A3B8;
        background-color: #F1F5F9;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px -2px rgba(15, 23, 42, 0.08);
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #E04F16, #C23B06) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(224, 79, 22, 0.28) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #F05C24, #D1420C) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(224, 79, 22, 0.35) !important;
    }
    
    /* Tarjetas de métricas */
    .stMetric {
        background: #FFFFFF;
        padding: 16px 18px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
    }
    .stMetric:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.06);
    }
    
    /* Menú lateral estilizado como lista de navegación moderna */
    div[role="radiogroup"] > label {
        padding: 9px 14px;
        border-radius: 10px;
        margin-bottom: 4px;
        border: 1px solid transparent;
        transition: all 0.16s ease;
        font-weight: 500;
        color: #334155;
    }
    div[role="radiogroup"] > label:hover {
        background-color: #F1F5F9;
        color: #0F172A;
    }
    div[role="radiogroup"] > label[data-checked="true"], 
    div[role="radiogroup"] > label:has(input:checked) {
        background: #FFF1EE !important;
        color: #C23B06 !important;
        font-weight: 700 !important;
        border: 1px solid #FFD8CE !important;
        box-shadow: 0 1px 2px rgba(224, 79, 22, 0.08);
    }

    /* Tabs elegantes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 9px 18px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        color: #E04F16 !important;
        border-bottom-color: #E04F16 !important;
    }
    
    /* Contenedores con borde */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02);
    }

    /* Inputs y Textareas */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        font-size: 0.92rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #E04F16 !important;
        box-shadow: 0 0 0 2px rgba(224, 79, 22, 0.15) !important;
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
    logo_svg = get_lucide("graduation-cap", size=22, color="#E04F16")
    sparkle_svg = get_lucide("sparkles", size=13, color="#E04F16")
    
    st.markdown(
        clean_html(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0.8rem; padding-bottom: 0.8rem; border-bottom: 1px solid #E2E8F0;">
            <div style="background: #FFF1EE; border: 1px solid #FFD8CE; padding: 8px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(224, 79, 22, 0.08);">
                {logo_svg}
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 4px;">
                    <h3 style="margin: 0; color: #0F172A; font-size: 1.15rem; font-weight: 700; line-height: 1.2;">CommunityLab</h3>
                </div>
                <div style="display: flex; align-items: center; gap: 4px; margin-top: 2px;">
                    {sparkle_svg}
                    <span style="font-size: 0.74rem; font-weight: 700; color: #E04F16; letter-spacing: 0.02em;">Equipo 47 · ONE LATAM</span>
                </div>
            </div>
        </div>
        <div style="margin-bottom: 0.9rem; padding: 6px 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; font-size: 0.75rem; color: #475569; display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #10B981;"></span>
            <span><strong>Target:</strong> Educación Superior & Ecosistema ONE</span>
        </div>
        """),
        unsafe_allow_html=True
    )

    # Menú limpio sin la palabra sprint
    opciones = [
        "1. Ingestión de Datos",
        "2. Pipeline de IA & Router",
        "3. Panel de Curaduría",
        "4. Dashboard de Sentimiento",
        "5. OCI Object Storage"
    ]

    opcion_menu = st.radio(
        "Navegación:",
        opciones,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top: 1rem; border-top: 1px solid #E2E8F0;'></div>", unsafe_allow_html=True)
    render_user_sidebar()

    gh_svg = get_lucide("github", size=14, color="#475569")
    sparkle_svg = get_lucide("sparkles", size=14, color="#E04F16")
    link_svg = get_lucide("external-link", size=12, color="#64748B")
    st.markdown(
        clean_html(f"""
        <div style="margin-top: 1rem; padding: 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;">
            <div style="font-size: 0.78rem; font-weight: 700; color: #1E293B; margin-bottom: 2px;">
                Hackathon ONE G10 - LATAM
            </div>
            <div style="font-size: 0.72rem; color: #64748B; margin-bottom: 8px;">
                Oracle Next Education & Alura
            </div>
            <a href="{DEMO_URL}" target="_blank" style="display: flex; align-items: center; justify-content: space-between; text-decoration: none; color: #E04F16; font-size: 0.75rem; font-weight: 700; background: #FFF1EE; padding: 6px 10px; border-radius: 6px; border: 1px solid #FFD8CE; margin-bottom: 6px; transition: background 0.15s ease;">
                <span style="display: flex; align-items: center; gap: 6px;">
                    {sparkle_svg}
                    Demo en Vivo (Streamlit Cloud)
                </span>
                {link_svg}
            </a>
            <a href="{GITHUB_REPO_URL}" target="_blank" style="display: flex; align-items: center; justify-content: space-between; text-decoration: none; color: #0F172A; font-size: 0.75rem; font-weight: 600; background: #FFFFFF; padding: 6px 10px; border-radius: 6px; border: 1px solid #CBD5E1; transition: background 0.15s ease;">
                <span style="display: flex; align-items: center; gap: 6px;">
                    {gh_svg}
                    Ver Código en GitHub
                </span>
                {link_svg}
            </a>
        </div>
        """),
        unsafe_allow_html=True
    )

# 3. Barra Superior de Estado Global (Top Status Bar)
archivo_actual = st.session_state.get("archivo_origen", "Sin lote cargado")
total_msgs = len(st.session_state.get("raw_payload", {}).get("interacciones", []))
info_lote = f"{archivo_actual} ({total_msgs} mensajes)" if total_msgs > 0 else "Selecciona o sube un lote"

cloud_svg = get_lucide("cloud", size=14, color="#059669")
fork_svg = get_lucide("git-fork", size=14, color="#7C3AED")
pkg_svg = get_lucide("layers", size=14, color="#2563EB")
sparkle_svg = get_lucide("sparkles", size=14, color="#E04F16")

st.markdown(
    clean_html(f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 16px; margin-bottom: 1.5rem; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; box-shadow: 0 1px 2px rgba(15,23,42,0.03);">
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #334155;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10B981;"></span>
                <span style="color: #64748B; font-weight: 500;">Storage:</span>
                <strong style="color: #0F172A; font-weight: 600;">OCI Always Free (Espejo Local Activo)</strong>
            </div>
            <span style="color: #CBD5E1;">|</span>
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #334155;">
                {fork_svg}
                <span style="color: #64748B; font-weight: 500;">Router:</span>
                <strong style="color: #7C3AED; font-weight: 600;">LinkedIn · Newsletter · FAQ</strong>
            </div>
            <span style="color: #CBD5E1;">|</span>
            <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: #334155;">
                {pkg_svg}
                <span style="color: #64748B; font-weight: 500;">Lote:</span>
                <strong style="color: #2563EB; font-weight: 600;">{info_lote}</strong>
            </div>
        </div>
        <div>
            <a href="{DEMO_URL}" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; text-decoration: none; color: #E04F16; font-size: 0.78rem; font-weight: 700; background: #FFF1EE; padding: 4px 10px; border-radius: 6px; border: 1px solid #FFD8CE;">
                {sparkle_svg}
                <span>Demo en la Nube</span>
            </a>
        </div>
    </div>
    """),
    unsafe_allow_html=True
)

# 4. Router de Vistas Modular (Simple: 1 menú = 1 función de vista independiente)
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

# 4. Pie de página institucional común
render_footer()
