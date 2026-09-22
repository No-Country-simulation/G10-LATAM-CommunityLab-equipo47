"""
Vista 3: Panel de Curaduría & Aprobación Humana (Human-in-the-Loop).
Permite al equipo de Marketing y Community Management revisar, ajustar y validar
los contenidos antes de su publicación oficial.
Diseño modular y fácil de entender.
"""
import streamlit as st
from modules.ui import badge_header, get_lucide

def render_curatorship_view():
    badge_header(
        icon_name="pen-tool",
        title="Panel de Curaduría y Aprobación",
        subtitle="Supervisión humana (Human-in-the-Loop) para editar, ajustar el tono y dar el visto bueno a los copys",
        color="#059669"
    )

    # Explicación clara y sencilla de qué es curaduría
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; gap: 12px; align-items: flex-start;">
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 8px; border-radius: 8px; margin-top: 2px;">
                    {get_lucide('help-circle', size=20, color='#059669')}
                </div>
                <div>
                    <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #065F46;">¿Qué es la Curaduría y por qué es indispensable?</h4>
                    <p style="margin: 4px 0 0 0; font-size: 0.9rem; color: #047857; line-height: 1.5;">
                        La <strong>curaduría</strong> es el filtro editorial que garantiza que ningún contenido salga a la luz sin validación de una persona real. 
                        La Inteligencia Artificial se encarga del 80% del trabajo pesado (lee cientos de mensajes y redacta borradores en segundos), 
                        pero <strong>un integrante del equipo</strong> debe revisar el tono, corregir datos si es necesario y decidir con un clic si el post se aprueba, se ajusta o se descarta.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if "curated_package" not in st.session_state:
        st.info("Para comenzar la curaduría, primero procesa un lote de mensajes en el menú '2. Pipeline de IA & Router'.")
        return

    paquete = st.session_state["curated_package"]
    activos = paquete.get("activos_distribucion_generados", {})

    tab_linkedin, tab_newsletter, tab_faq = st.tabs([
        "Post para LinkedIn", 
        "Destaque en Newsletter", 
        "Sugerencia de FAQ o Tip"
    ])

    # 1. TAB LINKEDIN
    with tab_linkedin:
        post_lk = activos.get("post_linkedin", {})
        
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0 1rem 0;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {get_lucide('briefcase', size=18, color='#059669')}
                    <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Borrador para LinkedIn</h4>
                </div>
                <span style="font-size: 0.8rem; background: #EEF2FF; color: #4338CA; padding: 4px 10px; border-radius: 6px; font-weight: 600;">
                    Canal: {post_lk.get('canal_recomendado', 'LinkedIn Oficial')}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_traz1, col_traz2 = st.columns(2)
        with col_traz1:
            st.caption("🤖 **Redacción inicial:** Generado por LLM mediante análisis del testimonio.")
        with col_traz2:
            st.caption("👤 **Curador asignado:** Integrante del equipo en turno.")

        nuevo_titulo_lk = st.text_input("Titular de la publicación en redes:", value=post_lk.get("titulo", ""))
        nuevo_copy_lk = st.text_area("Cuerpo del post (puedes editarlo libremente antes de publicar):", value=post_lk.get("copy", ""), height=200)

        estado_lk = st.radio(
            "Decisión del Curador:",
            ["Aprobado para Publicar", "Pendiente de Modificaciones", "Rechazado"],
            horizontal=True,
            key="curaduria_lk_radio"
        )

        if st.button("Guardar Decisión de LinkedIn", type="primary"):
            post_lk["titulo"] = nuevo_titulo_lk
            post_lk["copy"] = nuevo_copy_lk
            post_lk["estado_curaduria"] = estado_lk
            paquete["activos_distribucion_generados"]["post_linkedin"] = post_lk
            st.session_state["curated_package"] = paquete
            st.success("Decisión guardada. El paquete oficial reflejará estos cambios al guardarse en OCI.")

        # Sección para Copiar y Publicar en LinkedIn
        st.markdown("---")
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {get_lucide('share-2', size=18, color='#0A66C2')}
                    <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #0A66C2;">Listo para Publicar en LinkedIn</h4>
                </div>
                <a href="https://www.linkedin.com/feed/" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; text-decoration: none; color: #FFFFFF; background-color: #0A66C2; padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">
                    {get_lucide('external-link', size=13, color='#FFFFFF')}
                    Abrir LinkedIn
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("Haz clic en el icono de copiar (arriba a la derecha del recuadro) para llevarte el texto completo al portapapeles:")

        # Texto consolidado listo para pegar en LinkedIn
        texto_a_copiar = f"{nuevo_titulo_lk}\n\n{nuevo_copy_lk}"
        st.code(texto_a_copiar, language=None)

    # 2. TAB NEWSLETTER
    with tab_newsletter:
        nl = activos.get("destaque_newsletter_semanal", {})
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 0.5rem 0 1rem 0;">
                {get_lucide('newspaper', size=18, color='#059669')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Sección para Newsletter Semanal</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_nl1, col_nl2 = st.columns(2)
        with col_nl1:
            st.caption("🤖 **Origen:** Extraído del logro o evento más relevante de la semana.")
        with col_nl2:
            st.caption("👤 **Curador asignado:** Editor de contenidos comunitarios.")

        nueva_seccion = st.text_input("Nombre de la sección en el boletín:", value=nl.get("seccion", "Logro de la Semana"))
        nuevo_titular_nl = st.text_input("Titular destacado para el correo:", value=nl.get("titular", ""))
        nuevo_resumen_nl = st.text_area("Cuerpo sintetizado para el lector:", value=nl.get("resumen", ""), height=130)

        estado_nl = st.radio(
            "Decisión del Curador:",
            ["Incluir en la Edición Semanal", "Omitir en este envío"],
            horizontal=True,
            key="curaduria_nl_radio"
        )

        if st.button("Guardar Decisión de Newsletter", type="primary"):
            nl["seccion"] = nueva_seccion
            nl["titular"] = nuevo_titular_nl
            nl["resumen"] = nuevo_resumen_nl
            nl["estado_curaduria"] = estado_nl
            paquete["activos_distribucion_generados"]["destaque_newsletter_semanal"] = nl
            st.session_state["curated_package"] = paquete
            st.success("Sección de Newsletter actualizada.")

        # Sección para Copiar bloque de Newsletter
        st.markdown("---")
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                {get_lucide('newspaper', size=18, color='#059669')}
                <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #059669;">Listo para Pegar en el Boletín / Email</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("Copia este bloque con el botón de la esquina superior derecha:")
        texto_newsletter_copiar = f"[{nueva_seccion.upper()}]\n{nuevo_titular_nl}\n\n{nuevo_resumen_nl}"
        st.code(texto_newsletter_copiar, language=None)

    # 3. TAB FAQ / TIPS
    with tab_faq:
        faq = activos.get("sugerencia_contenido_faq", {})
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 0.5rem 0 1rem 0;">
                {get_lucide('help-circle', size=18, color='#059669')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Propuesta de Tip de Soporte y Pregunta Frecuente</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(f"📌 **Origen detectado por la IA:** {faq.get('origen', 'Comunidad')}")

        nuevo_tema_faq = st.text_input("Tema propuesto para el tip o FAQ:", value=faq.get("tema", ""))
        
        opciones_status = ["derivado_a_mentoria", "convertir_en_tutorial_corto", "publicado_en_faq", "descartado"]
        idx_default = 0
        if faq.get("status") in opciones_status:
            idx_default = opciones_status.index(faq.get("status"))

        nuevo_status_faq = st.selectbox(
            "Acción de soporte asignada:",
            opciones_status,
            index=idx_default
        )

        if st.button("Guardar Decisión de FAQ / Tip", type="primary"):
            faq["tema"] = nuevo_tema_faq
            faq["status"] = nuevo_status_faq
            paquete["activos_distribucion_generados"]["sugerencia_contenido_faq"] = faq
            st.session_state["curated_package"] = paquete
            st.success("Acción de documentación y FAQ guardada.")

    st.divider()
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; color: #475569; font-size: 0.9rem;">
            {get_lucide('cloud', size=16, color='#64748B')}
            <span>Una vez aprobados los copys, dirígete a <strong>5. OCI Object Storage</strong> para persistir el paquete final en Oracle Cloud.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
