"""
Vista 3: Panel de Curaduría & Aprobación Humana (Human-in-the-Loop).
Permite al equipo de Marketing y Community Management revisar, ajustar y validar
los contenidos antes de su publicación oficial.
Diseño humano y profesional con iconos de Lucide (lucide.dev).
"""
import streamlit as st
from modules.ui import badge_header, get_lucide

def render_curatorship_view():
    badge_header(
        icon_name="pen-tool",
        title="Panel de Curaduría y Aprobación",
        subtitle="Supervisión humana (Human-in-the-Loop) para editar, ajustar el tono y aprobar copys",
        color="#059669"
    )

    if "curated_package" not in st.session_state:
        st.info("Para curar contenidos, primero procesa un lote en el menú '2. Pipeline de IA & Router'.")
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
            <div style="display: flex; align-items: center; gap: 8px; margin: 0.5rem 0 1rem 0;">
                {get_lucide('briefcase', size=18, color='#059669')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Borrador para LinkedIn</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            st.info(f"Canal sugerido: **{post_lk.get('canal_recomendado', 'LinkedIn Oficial')}**")
        with col_meta2:
            st.success(f"Potencial de Engagement estimado: **{post_lk.get('potencial_engagement', 'Alto')}**")

        nuevo_titulo_lk = st.text_input("Titular de la publicación:", value=post_lk.get("titulo", ""))
        nuevo_copy_lk = st.text_area("Cuerpo del post (editable):", value=post_lk.get("copy", ""), height=220)

        estado_lk = st.radio(
            "Decisión de Curaduría:",
            ["Aprobado para Publicar", "Pendiente de Revisión", "Rechazado"],
            horizontal=True,
            key="curaduria_lk_radio"
        )

        if st.button("Guardar Aprobación LinkedIn", type="primary"):
            post_lk["titulo"] = nuevo_titulo_lk
            post_lk["copy"] = nuevo_copy_lk
            post_lk["estado_curaduria"] = estado_lk
            paquete["activos_distribucion_generados"]["post_linkedin"] = post_lk
            st.session_state["curated_package"] = paquete
            st.success("Borrador de LinkedIn actualizado correctamente.")

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

        nueva_seccion = st.text_input("Sección del boletín:", value=nl.get("seccion", "Logro de la Semana"))
        nuevo_titular_nl = st.text_input("Titular del artículo:", value=nl.get("titular", ""))
        nuevo_resumen_nl = st.text_area("Resumen del contenido:", value=nl.get("resumen", ""), height=130)

        estado_nl = st.radio(
            "Decisión de Curaduría:",
            ["Incluir en la Edición Semanal", "Omitir en este envío"],
            horizontal=True,
            key="curaduria_nl_radio"
        )

        if st.button("Guardar Aprobación Newsletter", type="primary"):
            nl["seccion"] = nueva_seccion
            nl["titular"] = nuevo_titular_nl
            nl["resumen"] = nuevo_resumen_nl
            nl["estado_curaduria"] = estado_nl
            paquete["activos_distribucion_generados"]["destaque_newsletter_semanal"] = nl
            st.session_state["curated_package"] = paquete
            st.success("Contenido de Newsletter actualizado correctamente.")

    # 3. TAB FAQ / TIPS
    with tab_faq:
        faq = activos.get("sugerencia_contenido_faq", {})
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 0.5rem 0 1rem 0;">
                {get_lucide('help-circle', size=18, color='#059669')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Propuesta de Tip de Soporte y FAQ</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        nuevo_tema_faq = st.text_input("Tema propuesto para el tip:", value=faq.get("tema", ""))
        st.caption(f"Origen identificado: {faq.get('origen', 'Comunidad')}")
        
        opciones_status = ["derivado_a_mentoria", "convertir_en_tutorial_corto", "publicado_en_faq", "descartado"]
        idx_default = 0
        if faq.get("status") in opciones_status:
            idx_default = opciones_status.index(faq.get("status"))

        nuevo_status_faq = st.selectbox(
            "Acción de documentación:",
            opciones_status,
            index=idx_default
        )

        if st.button("Guardar Aprobación FAQ / Tip", type="primary"):
            faq["tema"] = nuevo_tema_faq
            faq["status"] = nuevo_status_faq
            paquete["activos_distribucion_generados"]["sugerencia_contenido_faq"] = faq
            st.session_state["curated_package"] = paquete
            st.success("Propuesta de FAQ actualizada correctamente.")

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
