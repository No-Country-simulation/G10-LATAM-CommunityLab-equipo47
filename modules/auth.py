"""
Módulo de autenticación simple para CommunityLab.
Permite inicio de sesión en memoria (admin / admin) sin base de datos externa.
Diseño humano y profesional con iconos de Lucide (lucide.dev).
"""
import streamlit as st
from modules.ui import get_lucide, GITHUB_REPO_URL

def check_login():
    """Verifica si el usuario está autenticado en la sesión actual."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None

    return st.session_state.authenticated

def render_login_form():
    """Renderiza el formulario de inicio de sesión."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        sparkles_svg = get_lucide("sparkles", size=32, color="#E04F16")
        lock_svg = get_lucide("lock", size=18, color="#475569")
        gh_svg = get_lucide("github", size=14, color="#475569")
        
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
                <div style="display: inline-flex; background: #FFF1EE; border: 1px solid #FFD8CE; padding: 14px; border-radius: 16px; margin-bottom: 12px;">
                    {sparkles_svg}
                </div>
                <h1 style="color: #0F172A; font-size: 2rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;">CommunityLab</h1>
                <p style="color: #64748B; font-size: 1.05rem; margin-top: 6px;">
                    Motor de Transformación y Curaduría para Comunidades Digitales
                </p>
                <div style="display: inline-flex; gap: 8px; margin-top: 4px;">
                    <span style="background-color: #F1F5F9; color: #1E293B; padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 700; border: 1px solid #E2E8F0;">
                        Hackathon ONE G10 - LATAM · Equipo 47
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    {lock_svg}
                    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 600; color: #1E293B;">Acceso a la Plataforma</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption("Credenciales predeterminadas para evaluación técnica: **admin** / **admin**")
            
            with st.form("login_form"):
                user_input = st.text_input("Usuario", placeholder="admin", value="admin")
                pass_input = st.text_input("Contraseña", type="password", placeholder="admin", value="admin")
                submit = st.form_submit_button("Ingresar al Panel", use_container_width=True, type="primary")

                if submit:
                    if user_input.strip() == "admin" and pass_input.strip() == "admin":
                        st.session_state.authenticated = True
                        st.session_state.username = "Equipo 47 (Admin)"
                        st.toast("Sesión iniciada correctamente")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas. Ingresa admin / admin para acceder.")

        # Enlace al repositorio de GitHub
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 1.5rem;">
                <a href="{GITHUB_REPO_URL}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; text-decoration: none; color: #475569; font-size: 0.85rem; font-weight: 500;">
                    {gh_svg}
                    <span>Repositorio oficial en GitHub</span>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_user_sidebar():
    """Renderiza información del usuario en el sidebar y botón para cerrar sesión."""
    user_svg = get_lucide("user", size=15, color="#64748B")
    username = st.session_state.get('username', 'Admin')
    
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; padding: 6px 0; color: #334155; font-size: 0.9rem;">
            {user_svg}
            <span><strong>Usuario:</strong> {username}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
