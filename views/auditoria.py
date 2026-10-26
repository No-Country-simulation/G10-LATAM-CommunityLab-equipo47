"""
Vista 6: Auditoria y Consulta de OCI Object Storage.
Conforme a los requerimientos del Hackathon ONE G10 (Oracle Next Education & Alura).
Permite auditar en una tabla estructurada todos los paquetes persistidos en OCI,
con diagnostico transparente entre Nube Oracle Cloud y Espejo Local.
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from modules.ui import badge_header, get_lucide, render_callout, clean_html
from modules.oci_client import (
    consultar_tabla_auditoria_oci,
    verificar_estado_conexion_oci,
    _obtener_config_entorno
)

def render_auditing_view():
    badge_header(
        icon_name="shield-check",
        title="Auditoría & Consulta OCI Object Storage",
        subtitle="Fiscalización y consulta de paquetes persistidos (Conforme a Requisitos del Hackathon ONE G10)",
        color="#059669",
        target_pill="Auditoría Cloud & Trazabilidad"
    )

    cfg = _obtener_config_entorno()
    estado_oci = verificar_estado_conexion_oci()

    # DIAGNÓSTICO CLARO DE DONDE ESTÁN LOS ARCHIVOS
    if estado_oci["conectado_a_nube"]:
        render_callout(
            text=f"Auditoría conectada en vivo a Oracle Cloud (Namespace: {estado_oci['namespace']}, Bucket: {estado_oci['bucket']}). Los paquetes visualizados están persistidos en la infraestructura de OCI.",
            title="Conectado a Oracle Cloud (Nube Real)",
            icon_name="check-circle",
            color="#059669"
        )
    else:
        render_callout(
            text=f"Diagnóstico de Auditoría: Actualmente se están auditando los paquetes del Espejo Local (PC). En la consola web de Oracle Cloud (Namespace '{estado_oci['namespace']}') no aparecerán hasta que se configure el archivo de credenciales '{estado_oci['ruta_config_esperada']}'.",
            title="Auditoría en Modo Respaldo Local (Offline)",
            icon_name="info",
            color="#2563EB"
        )

    # Tarjetas Métricas
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Namespace OCI", cfg.get("namespace", "axsui3upub83"))
        c2.metric("Bucket OCI", cfg.get("bucket", "communitylab-activos-marketing"))
        c3.metric("Región OCI", cfg.get("region", "sa-santiago-1"))
        c4.metric("Origen Auditoría", "☁️ Nube OCI" if estado_oci["conectado_a_nube"] else "💾 Espejo Local")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Consulta a la tabla de OCI
    registros = consultar_tabla_auditoria_oci(bucket_name=cfg.get("bucket"))

    if not registros:
        render_callout(
            text="Aún no se registran paquetes en el almacenamiento. Ve al menú '5. OCI Object Storage' y presiona 'Persistir Paquete'.",
            title="Bucket Sin Registros",
            icon_name="info",
            color="#2563EB"
        )
        return

    # Preparar DataFrame para visualización tabular
    df_completo = pd.DataFrame(registros)
    columnas_tabla = [
        "Archivo",
        "Ruta en OCI Bucket",
        "Ubicación",
        "Namespace OCI",
        "Fecha / Periodo",
        "Tamaño (KB)",
        "Estado Curaduría",
        "Sentimiento Detectado",
        "Temas Principales",
        "Título Post LinkedIn"
    ]
    
    df_mostrar = df_completo[[col for col in columnas_tabla if col in df_completo.columns]]

    st.markdown(
        clean_html(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                {get_lucide('table', size=20, color='#059669')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">
                    Tabla de Consulta de Objetos OCI ({len(registros)} paquetes auditados)
                </h4>
            </div>
            <span style="font-size: 0.78rem; font-weight: 700; color: #047857; background: #ECFDF5; padding: 4px 10px; border-radius: 6px; border: 1px solid #A7F3D0;">
                {'☁️ Nube Oracle Cloud' if estado_oci['conectado_a_nube'] else '💾 Respaldo Local (PC)'}
            </span>
        </div>
        """),
        unsafe_allow_html=True
    )

    # Filtro interactivo de búsqueda
    col_filtro1, col_filtro2 = st.columns([2, 1])
    with col_filtro1:
        busqueda = st.text_input("🔍 Filtrar tabla por nombre, tema o sentimiento:", placeholder="Ej: semana_04, contratacion, Positivo...")
    with col_filtro2:
        fechas_disponibles = ["Todas las fechas"] + sorted(list(set(df_completo["Fecha / Periodo"].dropna())))
        filtro_fecha = st.selectbox("Filtrar por Periodo:", fechas_disponibles)

    df_filtrado = df_mostrar.copy()
    if busqueda:
        mascara = df_filtrado.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)
        df_filtrado = df_filtrado[mascara]
    if filtro_fecha != "Todas las fechas":
        df_filtrado = df_filtrado[df_filtrado["Fecha / Periodo"] == filtro_fecha]

    # TABLA PRINCIPAL DE AUDITORÍA
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # INSPECTOR DE RESPUESTAS OFICIALES SEGÚN HACKATHON_PROYECTO.PDF
    st.markdown(
        clean_html(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            {get_lucide('file-text', size=20, color='#059669')}
            <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">
                Inspección de Respuesta Guardada (Esquema Oficial ONE G10)
            </h4>
        </div>
        """),
        unsafe_allow_html=True
    )

    opciones_archivos = [r["Ruta en OCI Bucket"] for r in registros]
    archivo_seleccionado = st.selectbox(
        "Selecciona el paquete de OCI que deseas auditar y visualizar en detalle:",
        opciones_archivos
    )

    registro_sel = next((r for r in registros if r["Ruta en OCI Bucket"] == archivo_seleccionado), None)
    
    if registro_sel:
        paquete_data = registro_sel.get("_contenido_completo", {})
        resumen_data = paquete_data.get("resumen_comunidad", {})
        activos_data = paquete_data.get("activos_distribucion_generados", {})
        oci_data = paquete_data.get("almacenamiento_oci", {})
        
        tab1, tab2, tab3 = st.tabs(["📊 Resumen de la Auditoría", "📝 Activos Generados (Copys)", "🔍 JSON Oficial de OCI"])

        with tab1:
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown(f"**Archivo:** `{registro_sel.get('Archivo')}`")
                st.markdown(f"**Ruta OCI:** `{registro_sel.get('Ruta en OCI Bucket')}`")
                st.markdown(f"**Ubicación:** `{registro_sel.get('Ubicación')}`")
                st.markdown(f"**Tamaño:** `{registro_sel.get('Tamaño (KB)')} KB`")
            with col_res2:
                sentimiento_val = resumen_data.get('sentimiento_predominante') or registro_sel.get('Sentimiento Detectado', 'N/A')
                total_interacciones = resumen_data.get('total_interacciones_procesadas') or (len(paquete_data.get('interacciones', [])) if 'interacciones' in paquete_data else 'N/A')
                temas_val = ', '.join(resumen_data.get('temas_principales', [])) or registro_sel.get('Temas Principales', 'N/A')
                st.markdown(f"**Sentimiento Predominante:** `{sentimiento_val}`")
                st.markdown(f"**Mensajes / Interacciones:** `{total_interacciones}`")
                st.markdown(f"**Temas Clave:** `{temas_val}`")

        with tab2:
            if not activos_data and "interacciones" in paquete_data:
                st.info(f"ℹ️ Este archivo en OCI es un lote de entrada con {len(paquete_data.get('interacciones', []))} interacciones comunitarias. Los activos de marketing derivados se visualizan en los paquetes almacenados en la carpeta `activos/`.")
            else:
                post_lk = activos_data.get("post_linkedin", {})
                st.markdown("##### 💼 Post de LinkedIn Oficial:")
                st.markdown(f"**Título:** {post_lk.get('titulo', 'N/A')}")
                st.info(post_lk.get("copy", "N/A"))

                col_sub1, col_sub2 = st.columns(2)
                with col_sub1:
                    news = activos_data.get("destaque_newsletter_semanal", {})
                    st.markdown("##### 📰 Destaque Newsletter Semanal:")
                    st.markdown(f"**Sección:** {news.get('seccion', 'N/A')}")
                    st.markdown(f"**Titular:** {news.get('titular', 'N/A')}")
                    st.caption(news.get("resumen", "N/A"))
                with col_sub2:
                    faq_item = activos_data.get("sugerencia_contenido_faq", {})
                    st.markdown("##### ❓ Sugerencia Contenido FAQ:")
                    st.markdown(f"**Tema:** {faq_item.get('tema', 'N/A')}")
                    if faq_item.get("pregunta"):
                        st.markdown(f"**Pregunta:** `{faq_item.get('pregunta')}`")
                    if faq_item.get("respuesta_sugerida"):
                        st.caption(f"💡 **Respuesta:** {faq_item.get('respuesta_sugerida')}")
                    st.markdown(f"**Origen:** {faq_item.get('origen', 'N/A')}")
                    st.caption(f"Status: {faq_item.get('status', 'N/A')}")

        with tab3:
            st.caption("Estructura exacta devuelta y almacenada conforme a la Página 4 y 5 del documento del proyecto.")
            st.json(paquete_data)
            st.download_button(
                label=f"📥 Descargar JSON de {registro_sel.get('Archivo')}",
                data=json.dumps(paquete_data, indent=2, ensure_ascii=False),
                file_name=registro_sel.get("Archivo"),
                mime="application/json",
                key=f"audit_dl_{archivo_seleccionado}"
            )