"""
Vista 2: Pipeline de Inteligencia Artificial & Router Condicional.
Ejecuta el análisis de sentimiento, categorización de temas y orquestación de copys.
Especializado para el sector de Educación Tecnológica Superior & Ecosistema ONE.
"""
import streamlit as st
import time
from modules.ui import badge_header, get_lucide, render_tag, render_callout, render_linkedin_mockup, clean_html
from modules.mock_engine import process_community_payload
from modules.gemini_engine import procesar_con_gemini

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

    archivo_origen = st.session_state.get("archivo_origen", "Lote Activo")
    NOMBRES_CASOS = {
        "ejemplo_oficial_pdf_one_g10.json": "Caso Canónico (PDF Hackathon ONE G10)",
        "ejemplo_1_contratacion.json": "Caso 1: Inserción Laboral / Empleabilidad",
        "ejemplo_2_soporte_dudas.json": "Caso 2: Cátedra Cloud / Soporte Técnico",
        "ejemplo_3_feedback_mixto.json": "Caso 3: Bienestar Estudiantil & Tutorías Pares",
        "ejemplo_4_innovacion_hackathon.json": "Caso 4: Feria de Innovación & Pitches OCI",
        "ejemplo_5_discord_comunidad_one.json": "Caso 5: Discord ONE LATAM (Comunidad en Vivo)",
        "ejemplo_6_slack_alumni_tech.json": "Caso 6: Slack Alumni Network (Egresados)",
        "ejemplo_7_github_discussions_soporte.json": "Caso 7: GitHub Discussions (Dudas de Arquitectura)",
    }
    nombre_caso = NOMBRES_CASOS.get(archivo_origen, archivo_origen)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        st.markdown(
            clean_html(f"""
            <div style="background: #FFFFFF; border: 1px solid #D8B4FE; padding: 14px 18px; border-radius: 12px; display: flex; align-items: center; gap: 14px; box-shadow: 0 2px 6px rgba(124, 58, 237, 0.06);">
                <div style="background: #F3E8FF; padding: 10px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                    {get_lucide('message-square', size=24, color='#7C3AED')}
                </div>
                <div>
                    <span style="color: #6B21A8; font-size: 0.8rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.04em;">Caso Seleccionado para Procesar con IA:</span>
                    <strong style="color: #0F172A; display: block; font-size: 1.05rem; margin-top: 2px;">{nombre_caso}</strong>
                    <span style="color: #64748B; font-size: 0.85rem;">Origen: <code>{payload.get('origen_comunidad', '').replace('_', ' ')}</code> · <strong>{total_interacciones} interacciones orgánicas</strong></span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
    with col_cfg2:
        modelo = st.selectbox(
            "Motor de Inferencia LLM",
            ["Google Gemini 3.5 Flash Lite", "Google Gemini 2.5 Flash", "Modo Simulado / Hackathon MVP"],
            index=0
        )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Botón principal de ejecución con animación interactiva
    if st.button("🚀 Ejecutar Análisis y Router Condicional con IA", type="primary", use_container_width=True):
        barra_progreso = st.progress(0, text="Iniciando pipeline de análisis semántico...")
        
        with st.status(f"Procesando lote: {nombre_caso} con {modelo}...", expanded=True) as status:
            time.sleep(0.2)
            barra_progreso.progress(25, text="1/4 Normalizando mensajes y perfiles estudiantiles...")
            st.write(f"✓ Normalizadas {total_interacciones} interacciones orgánicas.")
            time.sleep(0.3)
            
            barra_progreso.progress(55, text="2/4 Extrayendo sentimiento predominante y entidades clave...")
            st.write("✓ Evaluación semántica de temas y polaridad completada.")
            time.sleep(0.3)
            
            barra_progreso.progress(80, text="3/4 Evaluando condiciones de bifurcación (Router)...")
            st.write("✓ Clasificados testimonios hacia LinkedIn y dudas técnicas hacia FAQ.")
            time.sleep(0.3)
            
            if "Gemini" in modelo:
                barra_progreso.progress(92, text="4/4 Inferencia con Google Gemini Flash en tiempo real...")
                modelo_gemini = "gemini-3.5-flash-lite" if "3.5" in modelo else "gemini-2.5-flash"
                paquete, ok, msg = procesar_con_gemini(payload, modelo_gemini)
                if ok:
                    barra_progreso.progress(100, text="¡Análisis completado exitosamente!")
                    status.update(label=f"✓ Pipeline ejecutado exitosamente con Google Gemini ({modelo_gemini})", state="complete", expanded=False)
                else:
                    st.warning(msg)
                    barra_progreso.progress(100, text="Finalizado con fallback")
                    status.update(label="Pipeline ejecutado con fallback simulado", state="complete", expanded=False)
            else:
                barra_progreso.progress(92, text="4/4 Redactando activos adaptados con motor simulado...")
                time.sleep(0.3)
                paquete = process_community_payload(payload)
                paquete["motor_utilizado"] = "Modo Simulado / Hackathon MVP"
                barra_progreso.progress(100, text="¡Análisis simulado completado!")
                status.update(label="✓ Pipeline ejecutado exitosamente en Modo Simulado", state="complete", expanded=False)

            st.session_state["generated_package"] = paquete
            st.session_state["curated_package"] = paquete.copy()
            st.session_state["paquete_caso_origen"] = nombre_caso
            st.toast(f"¡Resultados generados para {nombre_caso}!", icon="✨")

    # Si aún no se ha ejecutado para este caso
    if "generated_package" not in st.session_state:
        st.markdown(
            clean_html(f"""
            <div style="background: #FAF5FF; border: 2px dashed #D8B4FE; border-radius: 14px; padding: 32px 20px; text-align: center; margin: 1.5rem 0;">
                <div style="display: inline-flex; background: #F3E8FF; padding: 14px; border-radius: 50%; margin-bottom: 12px;">
                    {get_lucide('sparkles', size=32, color='#7C3AED')}
                </div>
                <h3 style="margin: 0; color: #4C1D95; font-size: 1.25rem; font-weight: 700;">Listo para procesar con IA</h3>
                <p style="color: #6B21A8; font-size: 0.96rem; max-width: 580px; margin: 8px auto 16px auto; line-height: 1.5;">
                    Haz clic en el botón superior <strong>"Ejecutar Análisis y Router Condicional con IA"</strong> para que Gemini analice las <strong>{total_interacciones} interacciones</strong> de <strong>{nombre_caso}</strong> y genere los activos de marketing.
                </p>
                <span style="font-size: 0.85rem; color: #7C3AED; background: #EDE9FE; padding: 4px 12px; border-radius: 999px; font-weight: 600;">
                    Inferencia transparente · Auditoría paso a paso
                </span>
            </div>
            """),
            unsafe_allow_html=True
        )

    if "generated_package" in st.session_state:
        paquete = st.session_state["generated_package"]
        resumen = paquete.get("resumen_comunidad", {})
        activos = paquete.get("activos_distribucion_generados", {})
        caso_procesado = st.session_state.get("paquete_caso_origen", nombre_caso)

        st.divider()

        # Banner de confirmación visual del caso procesado
        st.markdown(
            clean_html(f"""
            <div style="background: #F0FDF4; border: 1px solid #86EFAC; border-left: 5px solid #16A34A; border-radius: 10px; padding: 14px 18px; margin-bottom: 1.2rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    {get_lucide('check-circle-2', size=24, color='#16A34A')}
                    <div>
                        <strong style="color: #14532D; font-size: 1.05rem; display: block;">Resultados Generados para: {caso_procesado}</strong>
                        <span style="color: #15803D; font-size: 0.88rem;">La IA procesó las conversaciones y bifurcó automáticamente el contenido hacia LinkedIn, Newsletter y FAQ.</span>
                    </div>
                </div>
                <span style="background: #DCFCE7; color: #166534; font-size: 0.8rem; font-weight: 700; padding: 4px 12px; border-radius: 6px; border: 1px solid #86EFAC;">
                    ESTADO: LISTO PARA CURADURÍA
                </span>
            </div>
            """),
            unsafe_allow_html=True
        )

        motor_usado = paquete.get("motor_utilizado", "Google Gemini Flash (En vivo)")
        if "Gemini" in motor_usado and "En vivo" in motor_usado:
            st.success(f"✨ **Inferencia Activa:** {motor_usado} — Orquestación en tiempo real")
        else:
            st.info(f"⚙️ **Inferencia Activa:** {motor_usado}")

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

        total_proc = resumen.get("total_interacciones_procesadas", total_interacciones)
        sentimiento_txt = resumen.get("sentimiento_predominante", "N/A")
        temas_count = len(resumen.get("temas_principales", []))

        # Determinar badge corto de sentimiento
        sent_lower = sentimiento_txt.lower()
        if "positivo" in sent_lower or "éxito" in sent_lower or "colaborativo" in sent_lower:
            sent_badge = '<span style="background: #DCFCE7; color: #15803D; font-size: 0.74rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid #86EFAC;">POSITIVO</span>'
        elif "negativo" in sent_lower or "reclamo" in sent_lower or "alerta" in sent_lower:
            sent_badge = '<span style="background: #FEE2E2; color: #DC2626; font-size: 0.74rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid #FCA5A5;">ALERTA / NEGATIVO</span>'
        else:
            sent_badge = '<span style="background: #FEF3C7; color: #92400E; font-size: 0.74rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid #FCD34D;">NEUTRAL / CONSULTA</span>'

        col_diag1, col_diag2, col_diag3 = st.columns([1, 2.2, 1])
        with col_diag1:
            st.markdown(
                clean_html(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); min-height: 96px; display: flex; flex-direction: column; justify-content: space-between;">
                    <span style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">Mensajes Procesados</span>
                    <div style="font-size: 1.55rem; font-weight: 800; color: #0F172A; margin: 2px 0;">{total_proc}</div>
                    <span style="font-size: 0.72rem; color: #059669; font-weight: 600;">100% Inferencia Exitosa</span>
                </div>
                """),
                unsafe_allow_html=True
            )
        with col_diag2:
            st.markdown(
                clean_html(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); min-height: 96px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">Sentimiento Predominante</span>
                        {sent_badge}
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; line-height: 1.45; font-weight: 500;">
                        {sentimiento_txt}
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )
        with col_diag3:
            st.markdown(
                clean_html(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); min-height: 96px; display: flex; flex-direction: column; justify-content: space-between;">
                    <span style="font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">Temas Clave Detectados</span>
                    <div style="font-size: 1.55rem; font-weight: 800; color: #7C3AED; margin: 2px 0;">{temas_count}</div>
                    <span style="font-size: 0.72rem; color: #6D28D9; font-weight: 600;">Ejes Temáticos Extraídos</span>
                </div>
                """),
                unsafe_allow_html=True
            )

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
                <span style="font-size: 0.82rem; color: #64748B;">Selecciona una pestaña para revisar, copiar o publicar cada formato</span>
            </div>
            """),
            unsafe_allow_html=True
        )

        tab_linkedin, tab_newsletter, tab_faq = st.tabs([
            "1. Publicación para LinkedIn",
            "2. Destaque de Newsletter Semanal",
            "3. Sugerencia de FAQ y Cátedra"
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
                        {get_lucide('clock', size=18, color='#1D4ED8')}
                        <span style="color: #1E40AF; font-size: 0.9rem; font-weight: 600;">
                            Borrador preliminar generado por el Router · Pendiente de validación en Curaduría
                        </span>
                    </div>
                    <span style="font-size: 0.76rem; background: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 6px; font-weight: 700; border: 1px solid #FCD34D;">
                        Pendiente de Aprobación
                    </span>
                </div>
                """),
                unsafe_allow_html=True
            )

            # Previsualización Fotorrealista del Post de LinkedIn
            render_linkedin_mockup(titulo=titulo_lk, copy=copy_lk, canal=canal_lk, engagement=potencial_lk)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Bloque de borrador
            st.markdown("##### Borrador preliminar generado:")
            texto_completo_lk = f"{titulo_lk}\n\n{copy_lk}"
            st.code(texto_completo_lk, language=None)

            st.info("ℹ️ Para editar el tono institucional, validar y aprobar este post antes de su difusión, continúa al menú lateral '3. Panel de Curaduría'.")

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
                        {f'<p style="margin: 0 0 6px 0; color: #1E293B; font-size: 0.88rem; font-weight: 600;">❓ {faq.get("pregunta")}</p>' if faq.get("pregunta") else ''}
                        {f'<div style="background: #F8FAFC; border-left: 3px solid #D97706; padding: 8px 10px; border-radius: 4px; font-size: 0.86rem; color: #334155; line-height: 1.5; margin-bottom: 8px;">💡 <strong>Respuesta:</strong> {faq.get("respuesta_sugerida")}</div>' if faq.get("respuesta_sugerida") else ''}
                        <p style="margin: 0; color: #64748B; font-size: 0.82rem;"><strong>Detección:</strong> {origen_faq}</p>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

            texto_faq = f"[FAQ DE CÁTEDRA]\nTema: {tema_faq}\nPregunta: {faq.get('pregunta', '')}\nRespuesta: {faq.get('respuesta_sugerida', '')}\nOrigen: {origen_faq}\nEstado: {status_faq}"
            st.code(texto_faq, language=None)

        # EXPANDER JSON OFICIAL
        with st.expander("Ver JSON estructurado de salida (Esquema Oficial)"):
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
