"""
CommunityLab - Motor Inteligente de Transformación y Distribución para Comunidades Digitales
Hackathon ONE G10 - LATAM · Equipo 47
Sector: Educación Superior & Comunidades Digitales de Aprendizaje
Punto de Entrada Principal (Streamlit)
"""
import streamlit as st
from modules.auth import check_login, render_login_form, render_user_sidebar
from modules.ui import get_lucide, GITHUB_REPO_URL, render_footer, clean_html
from views.ingestion import render_ingestion_view
from views.pipeline_ia import render_pipeline_view
from views.curaduria import render_curatorship_view
from views.dashboard import render_dashboard_view
from views.almacenamiento_oci import render_oci_storage_view

# Configuración de página
st.set_page_config(
    page_title="CommunityLab | Equipo 47 ONE LATAM",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales refinados con estética moderna
st.markdown(
    """
    <style>
    /* Ajuste para que la barra lateral quede arriba sin espacio muerto */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
    }
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Botones más modernos y táctiles */
    .stButton>button {
        border-radius: 9px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
        border: 1px solid #CBD5E1;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .stButton>button:hover {
        border-color: #94A3B8;
        background-color: #F8FAFC;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.06);
    }
    
    /* Tarjetas de métricas */
    .stMetric {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    .stMetric:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 8px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Opciones de Radio Button */
    div[role="radiogroup"] > label {
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        border: 1px solid transparent;
        transition: all 0.15s ease;
    }
    div[role="radiogroup"] > label:hover {
        background-color: #F1F5F9;
    }

    /* Tabs elegantes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        font-weight: 600;
    }
    
    /* Contenedores con borde */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
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

# 3. Router de Vistas Modular (Simple: 1 menú = 1 función de vista independiente)
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
