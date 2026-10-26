"""
Vista 5: Almacenamiento en Oracle Cloud Infrastructure (OCI Object Storage).
Requisito obligatorio del MVP: Persistencia de paquetes de activos en un bucket de OCI Always Free.
Diseño transparente y usable para el usuario comun.
"""
import streamlit as st
import json
from pathlib import Path
from modules.ui import badge_header, get_lucide, render_kpi_card, render_callout, clean_html
from modules.oci_client import (
    guardar_en_oci,
    listar_activos_oci,
    verificar_estado_conexion_oci,
    guardar_configuracion_oci_local,
    obtener_contenido_objeto_oci,
    _obtener_config_entorno
)

def render_oci_storage_view():
    badge_header(
        icon_name="cloud",
        title="Almacenamiento OCI Object Storage",
        subtitle="Persistencia de activos en Bucket de Oracle Cloud (Namespace: axsui3upub83 · Capa Always Free)",
        color="#DC2626",
        target_pill="Infraestructura: Oracle Cloud Always Free"
    )

    estado_oci = verificar_estado_conexion_oci()
    cfg = _obtener_config_entorno()

    # DIAGNÓSTICO CLARO DE CONEXIÓN A ORACLE CLOUD
    if estado_oci["conectado_a_nube"]:
        render_callout(
            text=f"Conexión activa con Oracle Cloud. Los paquetes se guardan directamente en el Bucket '{estado_oci['bucket']}' del Namespace '{estado_oci['namespace']}' en la región '{estado_oci['region']}'.",
            title="Conectado a Oracle Cloud (Nube Real)",
            icon_name="check-circle",
            color="#059669"
        )
    else:
        render_callout(
            text=f"Atención: Actualmente estás en Modo Espejo Local (PC). Los paquetes se guardan en tu disco duro (carpeta oci_bucket_simulation) y NO en la consola web de Oracle Cloud, porque falta el archivo de credenciales '{estado_oci['ruta_config_esperada']}'.",
            title="Modo Respaldo Local (No conectado a la nube real)",
            icon_name="alert-triangle",
            color="#D97706"
        )

    # Tarjeta de Estado
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(render_kpi_card(
                "Namespace OCI",
                cfg.get("namespace", "axsui3upub83"),
                icon_name="database",
                color="#2563EB",
                igualar_altura=True,
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(render_kpi_card(
                "Bucket OCI",
                cfg.get("bucket", "communitylab-activos-marketing"),
                icon_name="layers",
                color="#D97706",
                variant="texto",
                igualar_altura=True,
            ), unsafe_allow_html=True)
        with c3:
            st.markdown(render_kpi_card(
                "Región OCI",
                cfg.get("region", "sa-santiago-1"),
                icon_name="cloud",
                color="#7C3AED",
                igualar_altura=True,
            ), unsafe_allow_html=True)
        with c4:
            st.markdown(render_kpi_card(
                "Destino Actual",
                "☁️ Nube OCI" if estado_oci["conectado_a_nube"] else "💾 Espejo Local",
                icon_name="server",
                color="#059669",
                igualar_altura=True,
            ), unsafe_allow_html=True)

    # ASISTENTE PARA CONECTAR A LA NUBE REAL SI TIENEN LAS CREDENCIALES
    if not estado_oci["conectado_a_nube"]:
        with st.expander("🔑 ¿Quieres que se suba directamente a Oracle Cloud (Namespace axsui3upub83)? Haz clic aquí"):
            st.markdown(
                """
                Para que los archivos aparezcan en la consola de Oracle Cloud de tu equipo, se necesita el archivo de autenticación OCI.
                Si tu compañero o tú tienen las credenciales de Oracle Cloud, puedes ingresarlas aquí:
                """
            )
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                user_ocid = st.text_input("User OCID:", placeholder="ocid1.user.oc1..aaaaaaa...")
                tenancy_ocid = st.text_input("Tenancy OCID:", placeholder="ocid1.tenancy.oc1..aaaaaaa...")
                fingerprint = st.text_input("Fingerprint:", placeholder="xx:xx:xx:xx:...")
            with col_c2:
                reg_sel = st.text_input("Región OCI:", value="sa-santiago-1")
                key_pem = st.text_area("Contenido de la Llave Privada (.pem):", placeholder="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----", height=130)

            if st.button("Guardar Credenciales y Conectar a Oracle Cloud", type="secondary"):
                if user_ocid and tenancy_ocid and fingerprint and key_pem:
                    ok, msg = guardar_configuracion_oci_local(user_ocid, tenancy_ocid, fingerprint, reg_sel, key_pem)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Por favor completa todos los campos para autenticar con Oracle Cloud.")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Verificación de paquete en sesión
    paquete_a_guardar = st.session_state.get("curated_package") or st.session_state.get("generated_package")

    if not paquete_a_guardar:
        render_callout(
            text="Para persistir un paquete en OCI, primero procesa un lote en '2. Pipeline de IA & Router'.",
            title="Sin paquete para persistir",
            icon_name="info",
            color="#2563EB"
        )
        return

    # Formulario de persistencia
    col1, col2 = st.columns([2, 1])
    with col1:
        bucket_name = st.text_input("Nombre del Bucket OCI Always Free:", value=cfg.get("bucket", "communitylab-activos-marketing"))
    with col2:
        periodo_actual = st.session_state.get("raw_payload", {}).get("periodo_referencia", "semana-04").lower()
        ruta_sugerida = f"activos/2026-{periodo_actual}/paquete-distribucion.json"

    ruta_objeto = st.text_input("Ruta de destino del objeto (URI dentro del Bucket):", value=ruta_sugerida)

    # BOTÓN PRINCIPAL DE PERSISTENCIA
    if st.button("🚀 Persistir Paquete en OCI Object Storage", type="primary", use_container_width=True):
        with st.spinner("Persistiendo en almacenamiento OCI..."):
            resultado = guardar_en_oci(paquete_a_guardar, bucket_name=bucket_name, ruta_objeto=ruta_objeto)
            st.session_state["ultimo_guardado_oci"] = resultado
            
            if resultado.get("nube_real"):
                st.success(f"✅ ¡Éxito! Paquete subido a la nube de Oracle Cloud en el namespace '{resultado.get('namespace')}'.")
            else:
                st.warning(f"💾 Paquete guardado en Espejo Local ({resultado.get('ruta_local_espejo')}). {resultado.get('estado_descripcion')}")

    # Mostrar confirmación del último guardado
    if "ultimo_guardado_oci" in st.session_state:
        res = st.session_state["ultimo_guardado_oci"]
        with st.container(border=True):
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        {get_lucide('check-circle', size=20, color='#059669')}
                        <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">Confirmación de Persistencia</h4>
                    </div>
                    <span style="background: #ECFDF5; color: #047857; font-size: 0.78rem; font-weight: 700; padding: 3px 10px; border-radius: 6px; border: 1px solid #A7F3D0;">
                        {res.get('modo')}
                    </span>
                </div>
                """),
                unsafe_allow_html=True
            )
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(f"**Bucket:** `{res.get('bucket')}`")
                st.markdown(f"**Namespace:** `{res.get('namespace')}`")
                st.markdown(f"**Ruta en Bucket:** `{res.get('ruta_objeto')}`")
            with col_d2:
                st.markdown(f"**Subido a Nube Real:** `{'Sí' if res.get('nube_real') else 'No (Espejo Local)'}`")
                st.markdown(f"**Ruta Local:** `{res.get('ruta_local_espejo')}`")
                if res.get("error_nube"):
                    st.caption(f"Detalle técnico: {res.get('error_nube')}")

    st.markdown("---")

    # LISTADO DE OBJETOS GUARDADOS
    st.markdown(
        clean_html(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            {get_lucide('folder', size=20, color='#DC2626')}
            <h4 style="margin: 0; font-size: 1.05rem; font-weight: 600; color: #1E293B;">
                Objetos Guardados en el Bucket ({bucket_name})
            </h4>
        </div>
        """),
        unsafe_allow_html=True
    )
    
    objetos = listar_activos_oci(bucket_name=bucket_name)

    if objetos:
        st.caption(f"Se encontraron **{len(objetos)} paquetes** disponibles:")
        for obj in objetos:
            peso_kb = round(obj.get("tamano_bytes", 0) / 1024, 2)
            origen_badge = obj.get("origen", "Espejo Local")
            with st.expander(f"{obj['ruta_objeto']} ({peso_kb} KB) — {origen_badge}"):
                st.caption(f"**Archivo:** {obj['nombre']} | **Ubicación:** {origen_badge}")
                contenido = obtener_contenido_objeto_oci(obj['ruta_objeto'], bucket_name=bucket_name)
                if contenido:
                    st.json(contenido)
                    st.download_button(
                        label=f"Descargar {obj['nombre']}",
                        data=json.dumps(contenido, indent=2, ensure_ascii=False),
                        file_name=obj['nombre'],
                        mime="application/json",
                        key=f"dl_{obj['ruta_objeto']}"
                    )
                else:
                    st.info(f"Objeto en nube OCI: {obj['ruta_objeto']}")
    else:
        st.info("Aún no se han persistido paquetes en este bucket durante la sesión.")