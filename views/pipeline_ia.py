"""
Vista 2: Pipeline de Inteligencia Artificial & Router Condicional.
Ejecuta el análisis de sentimiento, categorización de temas y orquestación de copys.
Especializado para el sector de Educación Tecnológica Superior & Ecosistema ONE.
"""
import streamlit as st
import time
from modules.ui import badge_header, get_lucide, render_tag, render_callout, render_linkedin_mockup, clean_html
from modules.mock_engine import process_community_payload

def render_pipeline_view():
    badge_header(
        icon_name="cpu",
        title="Pipeline de IA & Router Condicional",
        subtitle="Analiza sentimiento, extrae temas clave y bifurca el contenido automáticamente hacia los canales adecuados",
        color="#7C3AED",
        target_pill="Sector: Educación Superior & Ecosistema ONE"
    )

    if "raw_payload" not in st.session_state:
        render_callout(
            text="Para comenzar, carga un lote de mensajes desde el menú '1. Ingestión de Datos'.",
            title="Lote no encontrado",
            icon_name="info",
            color="#2563EB"
        )
        return

    payload = st.session_state["raw_payload"]
    interacciones = payload.get("interacciones", [])
    total_interacciones = len(interacciones)

    # Explicación clara y didáctica de cómo funciona el Router Condicional
    with st.container(border=True):
        st.markdown(
            clean_html(f"""
            <div style="display: flex; gap: 14px; align-items: flex-start; padding: 4px;">
                <div style="background: #F3E8FF; border: 1px solid #D8B4FE; padding: 10px; border-radius: 10px; margin-top: 2px;">
                    {get_lucide('git-fork', size=22, color='#7C3AED')}
                </div>
                <div>
                    <h4 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: #581C87;">¿Cómo funciona el Router Condicional en esta sección?</h4>
                    <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #6B21A8; line-height: 1.5;">
                        El motor de IA ingesta las conversaciones del campus virtual y evalúa cada mensaje. Según las reglas de negocio del Hackathon ONE:
                        <br>• <strong>Si detecta logros o contrataciones:</strong> bifurca hacia <strong>LinkedIn</strong> para generar publicaciones de impacto (User-Generated Content).
                        <br>• <strong>Si detecta resúmenes o anuncios de cátedra:</strong> bifurca hacia el <strong>Newsletter Semanal</strong> de la facultad.
                        <br>• <strong>Si detecta dudas técnicas repetitivas:</strong> bifurca hacia <strong>FAQ / Tips de Cátedra</strong> para asistir a los profesores.
                    </p>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        st.markdown(
            clean_html(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 10px; display: flex; align-items: center; gap: 12px;">
                {get_lucide('message-square', size=22, color='#7C3AED')}
                <div>
                    <span style="color: #64748B; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.03em;">Lote Activo para Procesar:</span>
                    <strong style="color: #0F172A; display: block; font-size: 0.96rem;">{payload.get('origen_comunidad', '').replace('_', ' ')} · {total_interacciones} mensajes</strong>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
    with col_cfg2:
        modelo = st.selectbox(
            "Motor de Inferencia LLM",
            ["Google Gemini 2.5 Flash", "OpenAI GPT-4o", "Modo Simulado / Hackathon MVP"],
            index=0
        )

    # Botón principal de ejecución
    if st.button("⚡ Ejecutar Análisis y Bifurcación en Router", type="primary", use_container_width=True):
        with st.status("Orquestando pipeline de inteligencia artificial...", expanded=True) as status:
            st.write("1. Normalizando textos y perfiles de estudiantes...")
            time.sleep(0.3)
            st.write("2. Extrayendo polaridad de sentimiento y entidades clave...")
            time.sleep(0.3)
            st.write("3. Evaluando condiciones de bifurcación (Logros -> LinkedIn, Pulso -> Newsletter, Dudas -> FAQ)...")
            time.sleep(0.3)
            st.write("4. Redactando activos adaptados al tono de Educación Superior...")
            time.sleep(0.3)
            
            paquete = process_community_payload(payload)
            st.session_state["generated_package"] = paquete
            st.session_state["curated_package"] = paquete.copy()
            status.update(label="Pipeline ejecutado exitosamente con router condicional", state="complete", expanded=False)

    # Si aún no se ha ejecutado en esta sesión pero ya existe o acaba de generarse
    if "generated_package" not in st.session_state:
        # Si ya había raw_payload, procesar automáticamente para conveniencia del usuario
        paquete = process_community_payload(payload)
        st.session_state["generated_package"] = paquete
        st.session_state["curated_package"] = paquete.copy()

    if "generated_package" in st.session_state:
        paquete = st.session_state["generated_package"]
        resumen = paquete.get("resumen_comunidad", {})
        activos = paquete.get("activos_distribucion_generados", {})

        st.divider()

        # Diagnóstico semántico
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                {get_lucide('bar-chart-3', size=20, color='#7C3AED')}
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1E293B;">Diagnóstico Semántico del Lote Ingerido</h3>
            </div>
            """),
            unsafe_allow_html=True
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Mensajes Procesados", resumen.get("total_interacciones_procesadas", total_interacciones))
        m2.metric("Sentimiento Predominante", resumen.get("sentimiento_predominante", "N/A"))
        m3.metric("Temas Clave Detectados", len(resumen.get("temas_principales", [])))

        st.markdown("<p style='font-size: 0.88rem; font-weight: 600; color: #475569; margin-top: 0.8rem; margin-bottom: 0.4rem;'>Temas Prioritarios Extraídos por la IA:</p>", unsafe_allow_html=True)
        tags_html = "".join([render_tag(t, "#F3E8FF", "#6B21A8") for t in resumen.get("temas_principales", [])])
        st.markdown(clean_html(tags_html), unsafe_allow_html=True)

        st.markdown("---")

        # SECCIÓN INTERACTIVA DE BIFURCACIÓN DEL ROUTER
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {get_lucide('git-fork', size=20, color='#7C3AED')}
                    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: #1E293B;">Activos Generados por el Router Condicional</h3>
                </div>
                <span style="font-size: 0.82rem; color: #64748B;">Selecciona una pestaña para ver, copiar o publicar cada activo</span>
            </div>
            """),
            unsafe_allow_html=True
        )

        tab_linkedin, tab_newsletter, tab_faq = st.tabs([
            "🎓 1. Publicación de LinkedIn (UGC Marketing)",
            "📰 2. Destaque para Newsletter Semanal",
            "💡 3. Sugerencia de FAQ / Tip de Cátedra"
        ])

        # TAB 1: LINKEDIN
        with tab_linkedin:
            post_lk = activos.get("post_linkedin", {})
            titulo_lk = post_lk.get("titulo", "")
            copy_lk = post_lk.get("copy", "")
            canal_lk = post_lk.get("canal_recomendado", "LinkedIn Institucional")
            potencial_lk = post_lk.get("potencial_engagement", "Alto")

            st.markdown(
                clean_html(f"""
                <div style="background: #EFF6FF; border: 1px solid #BFDBFE; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        {get_lucide('check-circle-2', size=18, color='#1D4ED8')}
                        <span style="color: #1E40AF; font-size: 0.9rem; font-weight: 600;">
                            Ruta de LinkedIn activada por el Router tras detectar historias de impacto estudiantil
                        </span>
                    </div>
                    <a href="https://www.linkedin.com/feed/" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; text-decoration: none; color: #FFFFFF; background-color: #0A66C2; padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 600;">
                        {get_lucide('external-link', size=13, color='#FFFFFF')}
                        Abrir LinkedIn
                    </a>
                </div>
                """),
                unsafe_allow_html=True
            )

            # Previsualización Fotorrealista del Post de LinkedIn
            render_linkedin_mockup(titulo=titulo_lk, copy=copy_lk, canal=canal_lk, engagement=potencial_lk)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Bloque para copiar el texto
            st.markdown("##### Copiar texto completo listo para publicar:")
            texto_completo_lk = f"{titulo_lk}\n\n{copy_lk}"
            st.code(texto_completo_lk, language=None)

            col_acc1, col_acc2 = st.columns([1, 1])
            with col_acc1:
                if st.button("📋 Copiar Copy al Portapapeles", key="btn_copy_lk"):
                    st.success("Texto seleccionado arriba. Utiliza el icono de copiar en la esquina del recuadro.")
            with col_acc2:
                st.caption("¿Necesitas hacer ajustes o correcciones editoriales? Puedes hacerlo en el menú lateral **'3. Panel de Curaduría'**.")

        # TAB 2: NEWSLETTER
        with tab_newsletter:
            nl = activos.get("destaque_newsletter_semanal", {})
            seccion_nl = nl.get("seccion", "Logro Estudiantil")
            titular_nl = nl.get("titular", "")
            resumen_nl = nl.get("resumen", "")

            st.markdown(
                clean_html(f"""
                <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    {get_lucide('newspaper', size=18, color='#059669')}
                    <span style="color: #065F46; font-size: 0.9rem; font-weight: 600;">
                        Ruta de Newsletter Semanal: Síntesis optimizada para el boletín académico y graduados
                    </span>
                </div>
                """),
                unsafe_allow_html=True
            )

            with st.container(border=True):
                st.markdown(
                    clean_html(f"""
                    <div style="padding: 6px;">
                        <span style="background: #E0F2FE; color: #0369A1; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                            Sección: {seccion_nl}
                        </span>
                        <h4 style="margin: 8px 0 6px 0; font-size: 1.12rem; color: #0F172A; font-weight: 700;">{titular_nl}</h4>
                        <p style="margin: 0; color: #334155; font-size: 0.92rem; line-height: 1.5;">{resumen_nl}</p>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

            st.markdown("##### Copiar bloque de boletín:")
            texto_nl = f"[{seccion_nl.upper()}]\n{titular_nl}\n\n{resumen_nl}"
            st.code(texto_nl, language=None)

        # TAB 3: FAQ / TIPS
        with tab_faq:
            faq = activos.get("sugerencia_contenido_faq", {})
            tema_faq = faq.get("tema", "")
            origen_faq = faq.get("origen", "")
            status_faq = faq.get("status", "derivado_a_ayudantes_de_catedra")

            st.markdown(
                clean_html(f"""
                <div style="background: #FFFBEB; border: 1px solid #FDE68A; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    {get_lucide('help-circle', size=18, color='#D97706')}
                    <span style="color: #92400E; font-size: 0.9rem; font-weight: 600;">
                        Ruta de Soporte de Cátedra: Identificación de dudas repetitivas para generar material preventivo
                    </span>
                </div>
                """),
                unsafe_allow_html=True
            )

            with st.container(border=True):
                st.markdown(
                    clean_html(f"""
                    <div style="padding: 6px;">
                        <span style="background: #FEF3C7; color: #92400E; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                            Estado: {status_faq.replace('_', ' ').title()}
                        </span>
                        <h4 style="margin: 8px 0 6px 0; font-size: 1.12rem; color: #0F172A; font-weight: 700;">{tema_faq}</h4>
                        <p style="margin: 0; color: #64748B; font-size: 0.88rem;"><strong>Detección:</strong> {origen_faq}</p>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

            texto_faq = f"[FAQ DE CÁTEDRA]\nTema: {tema_faq}\nOrigen: {origen_faq}\nEstado: {status_faq}"
            st.code(texto_faq, language=None)

        # EXPANDER JSON OFICIAL
        with st.expander("📄 Ver JSON estructurado de salida (formato oficial de las págs. 4 y 5 del PDF)"):
            st.json(paquete)

        st.markdown(
            clean_html(f"""
            <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 14px 16px; border-radius: 10px; display: flex; align-items: center; gap: 12px; margin-top: 1.2rem;">
                {get_lucide('check-circle-2', size=22, color='#059669')}
                <div>
                    <strong style="color: #065F46; font-size: 0.95rem; display: block;">Activos generados y validados con éxito</strong>
                    <span style="color: #047857; font-size: 0.88rem;">
                        Pasa al <strong>Panel de Curaduría</strong> para aprobar o dar el visto bueno editorial, o a <strong>OCI Object Storage</strong> para persistir el paquete en la nube de Oracle.
                    </span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
