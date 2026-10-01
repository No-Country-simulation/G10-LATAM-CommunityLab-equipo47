"""
Vista 3: Panel de Curaduría & Aprobación Humana (Human-in-the-Loop).
Permite al equipo de Marketing Universitario y Community Management revisar, ajustar y validar
los contenidos antes de su publicación oficial.
Especializado para el sector de Educación Superior & Ecosistema ONE (Admisiones, Prensa de Facultad y Soporte de Cátedra).
"""
import streamlit as st
from modules.ui import badge_header, get_lucide, render_callout, render_linkedin_mockup, clean_html

def render_curatorship_view():
    badge_header(
        icon_name="pen-tool",
        title="Panel de Curaduría y Aprobación",
        subtitle="Supervisión humana (Human-in-the-Loop) para editar, ajustar el tono institucional y dar el visto bueno a los copys",
        color="#059669",
        target_pill="Sector: Educación Superior & Ecosistema ONE"
    )

    # Explicación clara de qué es curaduría
    with st.container(border=True):
        st.markdown(
            clean_html(f"""
            <div style="display: flex; gap: 14px; align-items: flex-start; padding: 4px;">
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 10px; border-radius: 10px; margin-top: 2px;">
                    {get_lucide('graduation-cap', size=22, color='#059669')}
                </div>
                <div>
                    <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #065F46;">¿Por qué es indispensable la Curaduría en Educación Superior?</h4>
                    <p style="margin: 4px 0 0 0; font-size: 0.9rem; color: #047857; line-height: 1.5;">
                        La <strong>curaduría</strong> es el filtro ético y editorial que garantiza que ningún activo salga a la luz sin validación humana. 
                        La Inteligencia Artificial se encarga del 80% del trabajo pesado (lee cientos de mensajes en foros y redacta borradores en segundos), 
                        pero <strong>el equipo de comunicación académica o de cátedra</strong> debe revisar que el tono respete la voz institucional, corregir nombres o datos sensibles y decidir con un clic si el post se aprueba, se ajusta o se descarta.
                    </p>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    if "curated_package" not in st.session_state and "generated_package" not in st.session_state:
        render_callout(
            text="Para comenzar la curaduría, primero procesa un lote de mensajes en el menú '2. Pipeline de IA & Router'.",
            title="Sin paquete generado",
            icon_name="info",
            color="#2563EB"
        )
        return

    # Sincronizar si aún no se había copiado a curated_package
    if "curated_package" not in st.session_state:
        st.session_state["curated_package"] = st.session_state["generated_package"].copy()

    paquete = st.session_state["curated_package"]
    activos = paquete.get("activos_distribucion_generados", {})

    tab_linkedin, tab_newsletter, tab_faq = st.tabs([
        "Post para LinkedIn", 
        "Destaque de Newsletter", 
        "Sugerencia de FAQ y Cátedra"
    ])

    # 1. TAB LINKEDIN
    with tab_linkedin:
        post_lk = activos.get("post_linkedin", {})
        
        st.markdown(
            clean_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0 1rem 0;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {get_lucide('share-2', size=19, color='#0A66C2')}
                    <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Curaduría Editorial para LinkedIn</h4>
                </div>
                <span style="font-size: 0.8rem; background: #EFF6FF; color: #1D4ED8; padding: 4px 10px; border-radius: 6px; font-weight: 600; border: 1px solid #BFDBFE;">
                    Canal: {post_lk.get('canal_recomendado', 'LinkedIn Institucional')}
                </span>
            </div>
            """),
            unsafe_allow_html=True
        )

        col_edit_lk, col_prev_lk = st.columns([1, 1])

        with col_edit_lk:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    {get_lucide('pen-tool', size=16, color='#2563EB')}
                    <strong style="font-size: 0.95rem; color: #0F172A;">Editor de Contenido</strong>
                </div>
                """),
                unsafe_allow_html=True
            )
            st.caption("Ajusta el titular y el texto. La previsualización de la derecha se adaptará a tus modificaciones:")
            nuevo_titulo_lk = st.text_input("Titular de la publicación:", value=post_lk.get("titulo", ""), key="input_titulo_lk")
            nuevo_copy_lk = st.text_area("Cuerpo del post (puedes editarlo libremente):", value=post_lk.get("copy", ""), height=220, key="textarea_copy_lk")

            estado_lk = st.radio(
                "Decisión del Curador:",
                ["Aprobado para Publicar", "Pendiente de Modificaciones", "Rechazado"],
                horizontal=True,
                key="curaduria_lk_radio"
            )

            if st.button("Guardar Cambios de LinkedIn", type="primary", use_container_width=True):
                post_lk["titulo"] = nuevo_titulo_lk
                post_lk["copy"] = nuevo_copy_lk
                post_lk["estado_curaduria"] = estado_lk
                paquete["activos_distribucion_generados"]["post_linkedin"] = post_lk
                st.session_state["curated_package"] = paquete
                st.success("Cambios editoriales guardados. Se reflejarán en el paquete final de OCI.")

        with col_prev_lk:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    {get_lucide('linkedin', size=16, color='#0A66C2')}
                    <strong style="font-size: 0.95rem; color: #0F172A;">Previsualización Fotorrealista en Vivo</strong>
                </div>
                """),
                unsafe_allow_html=True
            )
            canal_mostrar = post_lk.get("canal_recomendado", "LinkedIn Institucional")
            potencial_mostrar = post_lk.get("potencial_engagement", "Alto")
            render_linkedin_mockup(titulo=nuevo_titulo_lk, copy=nuevo_copy_lk, canal=canal_mostrar, engagement=potencial_mostrar)

        # Sección para Copiar y Publicar en LinkedIn
        st.markdown("---")
        col_pub_izq, col_pub_der = st.columns([3, 1])
        with col_pub_izq:
            texto_a_copiar = f"{nuevo_titulo_lk}\n\n{nuevo_copy_lk}"
            st.code(texto_a_copiar, language=None)
        with col_pub_der:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown(
                clean_html(f"""
                <a href="https://www.linkedin.com/feed/" target="_blank" style="display: flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; color: #FFFFFF; background-color: #0A66C2; padding: 10px 16px; border-radius: 8px; font-size: 0.9rem; font-weight: 700; box-shadow: 0 2px 4px rgba(10,102,194,0.3);">
                    {get_lucide('external-link', size=15, color='#FFFFFF')}
                    Abrir LinkedIn
                </a>
                """),
                unsafe_allow_html=True
            )

    # 2. TAB NEWSLETTER
    with tab_newsletter:
        nl = activos.get("destaque_newsletter_semanal", {})
        
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 0.5rem 0 1rem 0;">
                {get_lucide('newspaper', size=18, color='#059669')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Sección para Newsletter / Boletín Académico</h4>
            </div>
            """),
            unsafe_allow_html=True
        )

        col_nl_edit, col_nl_prev = st.columns([1, 1])

        with col_nl_edit:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    {get_lucide('pen-tool', size=16, color='#059669')}
                    <strong style="font-size: 0.95rem; color: #0F172A;">Redacción del Boletín</strong>
                </div>
                """),
                unsafe_allow_html=True
            )
            nueva_seccion = st.text_input("Nombre de la sección en el boletín:", value=nl.get("seccion", "Logro Estudiantil de la Semana"), key="nl_sec_input")
            nuevo_titular_nl = st.text_input("Titular destacado:", value=nl.get("titular", ""), key="nl_tit_input")
            nuevo_resumen_nl = st.text_area("Cuerpo sintetizado para el lector:", value=nl.get("resumen", ""), height=150, key="nl_res_input")

            estado_nl = st.radio(
                "Decisión del Curador:",
                ["Incluir en la Edición Semanal", "Omitir en este envío"],
                horizontal=True,
                key="curaduria_nl_radio"
            )

            if st.button("Guardar Cambios de Newsletter", type="primary", use_container_width=True):
                nl["seccion"] = nueva_seccion
                nl["titular"] = nuevo_titular_nl
                nl["resumen"] = nuevo_resumen_nl
                nl["estado_curaduria"] = estado_nl
                paquete["activos_distribucion_generados"]["destaque_newsletter_semanal"] = nl
                st.session_state["curated_package"] = paquete
                st.success("Sección de Newsletter actualizada.")

        with col_nl_prev:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    {get_lucide('mail', size=16, color='#059669')}
                    <strong style="font-size: 0.95rem; color: #0F172A;">Previsualización de Correo Electrónico</strong>
                </div>
                """),
                unsafe_allow_html=True
            )
            with st.container(border=True):
                st.markdown(
                    clean_html(f"""
                    <div style="padding: 12px; background: #FFFFFF; border-radius: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                            <span style="background: #E0F2FE; color: #0369A1; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                                {nueva_seccion}
                            </span>
                            <span style="font-size: 0.75rem; color: #64748B;">Boletín Semanal ONE LATAM</span>
                        </div>
                        <h4 style="margin: 0 0 8px 0; font-size: 1.15rem; color: #0F172A; font-weight: 700; line-height: 1.3;">{nuevo_titular_nl}</h4>
                        <p style="margin: 0; color: #334155; font-size: 0.92rem; line-height: 1.6;">{nuevo_resumen_nl}</p>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

            st.markdown("##### Copiar bloque de boletín:")
            texto_newsletter_copiar = f"[{nueva_seccion.upper()}]\n{nuevo_titular_nl}\n\n{nuevo_resumen_nl}"
            st.code(texto_newsletter_copiar, language=None)

    # 3. TAB FAQ / TIPS
    with tab_faq:
        faq = activos.get("sugerencia_contenido_faq", {})
        
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin: 0.5rem 0 1rem 0;">
                {get_lucide('lightbulb', size=18, color='#D97706')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Propuesta de Tip de Cátedra y FAQ de Soporte</h4>
            </div>
            """),
            unsafe_allow_html=True
        )

        col_faq_edit, col_faq_prev = st.columns([1, 1])

        with col_faq_edit:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    {get_lucide('help-circle', size=16, color='#D97706')}
                    <strong style="font-size: 0.95rem; color: #0F172A;">Configuración de Soporte</strong>
                </div>
                """),
                unsafe_allow_html=True
            )
            st.caption(f"**Origen detectado en comunidad:** {faq.get('origen', 'Comunidad')}")
            nuevo_tema_faq = st.text_input("Tema propuesto para el tip o FAQ:", value=faq.get("tema", ""), key="faq_tema_input")
            
            opciones_status = ["derivado_a_mentoria", "derivado_a_ayudantes_de_catedra", "convertir_en_tutorial_corto", "publicado_en_campus_virtual", "descartado"]
            idx_default = 0
            if faq.get("status") in opciones_status:
                idx_default = opciones_status.index(faq.get("status"))

            nuevo_status_faq = st.selectbox(
                "Acción de soporte asignada:",
                opciones_status,
                index=idx_default,
                key="faq_status_select"
            )

            if st.button("Guardar Decisión de FAQ / Tip", type="primary", use_container_width=True):
                faq["tema"] = nuevo_tema_faq
                faq["status"] = nuevo_status_faq
                paquete["activos_distribucion_generados"]["sugerencia_contenido_faq"] = faq
                st.session_state["curated_package"] = paquete
                st.success("Acción de documentación y soporte guardada.")

        with col_faq_prev:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    {get_lucide('book-open', size=16, color='#D97706')}
                    <strong style="font-size: 0.95rem; color: #0F172A;">Tarjeta de Asistencia Comunitaria</strong>
                </div>
                """),
                unsafe_allow_html=True
            )
            with st.container(border=True):
                st.markdown(
                    clean_html(f"""
                    <div style="padding: 12px; background: #FFFFFF; border-radius: 8px;">
                        <span style="background: #FEF3C7; color: #92400E; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                            Estado: {nuevo_status_faq.replace('_', ' ').title()}
                        </span>
                        <h4 style="margin: 8px 0 6px 0; font-size: 1.08rem; color: #0F172A; font-weight: 700;">{nuevo_tema_faq}</h4>
                        <p style="margin: 0; color: #64748B; font-size: 0.85rem; line-height: 1.4;">
                            <strong>Detección automática:</strong> {faq.get('origen', '')}
                        </p>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

            texto_faq_copiar = f"[FAQ DE CÁTEDRA]\nTema: {nuevo_tema_faq}\nAcción: {nuevo_status_faq.replace('_', ' ').title()}\nOrigen: {faq.get('origen', '')}"
            st.code(texto_faq_copiar, language=None)

    st.divider()
    st.markdown(
        clean_html(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 18px; border-radius: 10px;">
            <div style="display: flex; align-items: center; gap: 8px; color: #475569; font-size: 0.9rem;">
                {get_lucide('cloud', size=18, color='#059669')}
                <span>¿Decisiones validadas? Continúa a <strong>5. OCI Object Storage</strong> para persistir el paquete en la nube de Oracle.</span>
            </div>
            <span style="font-size: 0.78rem; font-weight: 700; color: #059669; background: #ECFDF5; padding: 3px 10px; border-radius: 6px; border: 1px solid #A7F3D0;">
                Always Free Ready
            </span>
        </div>
        """),
        unsafe_allow_html=True
    )
