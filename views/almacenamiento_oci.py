"""
Vista 5: Almacenamiento en Oracle Cloud Infrastructure (OCI Object Storage).
Requisito obligatorio del MVP: Persistencia de paquetes de activos en un bucket de OCI Always Free.
Diseño modular adaptado a la infraestructura del Hackathon ONE G10.
"""
import streamlit as st
import json
from pathlib import Path
from modules.ui import badge_header, get_lucide, render_callout, clean_html
from modules.oci_client import (
    configuracion_oci_publica,
    guardar_en_oci,
    listar_activos_oci,
    preparar_paquete_para_guardar,
    ruta_sugerida_para_paquete,
)

def render_oci_storage_view():
    badge_header(
        icon_name="cloud",
        title="Almacenamiento OCI Object Storage",
        subtitle="Persistencia obligatoria de activos en un Bucket de Oracle Cloud (Capa Always Free)",
        color="#DC2626",
        target_pill="Infraestructura: Oracle Cloud Always Free"
    )

    render_callout(
        text="Requisito mandatorio del Hackathon ONE: Todos los paquetes generados (JSON estructurado con copys, resumen semántico y decisiones de curaduría) "
             "deben quedar persistidos en un Bucket de OCI Object Storage dentro de la capa gratuita Always Free.",
        title="Conformidad con Oracle Cloud",
        icon_name="shield-check",
        color="#DC2626"
    )

    # Tarjeta de estado de conectividad OCI
    with st.container(border=True):
        col_st1, col_st2 = st.columns([3, 1])
        with col_st1:
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #10B981;"></span>
                    <strong style="color: #0F172A; font-size: 0.95rem;">Almacenamiento: OCI Object Storage (offline si no hay credenciales)</strong>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 0.84rem; color: #64748B; line-height: 1.4;">
                    El sistema serializa los paquetes en la estructura estándar de OCI Object Storage (<code>bucket/activos/AAAA-semana-NN/paquete-distribucion.json</code>)
                    y mantiene un espejo local solo como modo offline cuando no hay credenciales.
                </p>
                """),
                unsafe_allow_html=True
            )
        with col_st2:
            st.markdown(
                clean_html(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 6px 12px; border-radius: 8px; text-align: center; margin-top: 4px;">
                    <span style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Cuota OCI</span>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #059669;">20 GB Free</div>
                </div>
                """),
                unsafe_allow_html=True
            )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    config_publica = configuracion_oci_publica()
    bucket_config = config_publica.get("bucket") or ""
    region_config = config_publica.get("region") or ""

    col1, col2 = st.columns([2, 1])
    with col1:
        st.text_input(
            "Bucket OCI (desde configuración)",
            value=bucket_config or "(sin configurar)",
            disabled=True,
        )
    with col2:
        st.text_input(
            "Región OCI (desde configuración)",
            value=region_config or "(sin configurar)",
            disabled=True,
        )

    st.caption("Cumplimiento estricto con las directrices de costo cero (Always Free) del programa social ONE.")

    if "curated_package" not in st.session_state and "generated_package" not in st.session_state:
        render_callout(
            text="Para persistir un paquete en OCI, primero procesa un lote en '2. Pipeline de IA & Router'.",
            title="Sin paquete para persistir",
            icon_name="info",
            color="#2563EB"
        )
        return

    paquete_a_guardar = st.session_state.get("curated_package", st.session_state.get("generated_package"))
    ruta_sugerida = ruta_sugerida_para_paquete(paquete_a_guardar)

    ruta_objeto = st.text_input("Ruta de destino del objeto (URI dentro del Bucket):", value=ruta_sugerida)
    st.caption(f"Ruta resultante: `{ruta_objeto}`")

    sobrescribir = st.checkbox("Sobrescribir si el objeto ya existe", value=False)

    if st.session_state.get("paquete_simulado"):
        st.warning("Este paquete es SIMULADO: no fue generado por IA")

    if st.button("Persistir Paquete en OCI Object Storage", type="primary", use_container_width=True):
        resultado = guardar_en_oci(
            paquete_a_guardar,
            bucket_name=bucket_config or None,
            ruta_objeto=ruta_objeto,
            sobrescribir=sobrescribir,
        )
        st.session_state["ultimo_guardado_oci"] = resultado
        estado = resultado.get("status")
        if estado == "guardado_con_exito":
            st.success(f"Paquete guardado en OCI en el Bucket '{resultado.get('bucket')}' ({resultado.get('modo')})")
        elif estado == "ya_existe":
            st.warning("El objeto ya existe en el bucket. Marca 'Sobrescribir si el objeto ya existe' y vuelve a intentarlo.")
        elif estado == "guardado_local":
            st.warning(resultado.get("aviso") or "Modo offline: guardado solo en local.")
        else:
            st.error(resultado.get("error_nube") or "No se pudo guardar en OCI.")

    if "ultimo_guardado_oci" in st.session_state:
        res = st.session_state["ultimo_guardado_oci"]
        with st.container(border=True):
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        {get_lucide('check-circle-2', size=20, color='#059669')}
                        <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Confirmación de Almacenamiento (Esquema Oficial)</h4>
                    </div>
                    <span style="background: #ECFDF5; color: #047857; font-size: 0.78rem; font-weight: 700; padding: 3px 10px; border-radius: 6px; border: 1px solid #A7F3D0;">
                        {res.get('modo')}
                    </span>
                </div>
                """),
                unsafe_allow_html=True
            )
            confirmacion = {
                "almacenamiento_oci": {
                    "bucket": res.get("bucket"),
                    "ruta_objeto": res.get("ruta_objeto"),
                    "status": res.get("status")
                }
            }
            st.json(confirmacion)

            # Botón de descarga directa: mismo contenido que el paquete subido.
            bucket_guardado = res.get("bucket") or bucket_config
            ruta_guardada = res.get("ruta_objeto") or ruta_objeto
            paquete_descarga = preparar_paquete_para_guardar(
                paquete_a_guardar,
                bucket_guardado,
                ruta_guardada,
            )
            json_str = json.dumps(paquete_descarga, indent=2, ensure_ascii=False)
            st.download_button(
                label="Descargar Paquete JSON Oficial para Evaluación",
                data=json_str,
                file_name=res.get("ruta_objeto").split("/")[-1],
                mime="application/json",
                use_container_width=True
            )

    st.divider()
    st.markdown(
        clean_html(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
            <div style="display: flex; align-items: center; gap: 8px;">
                {get_lucide('database', size=19, color='#475569')}
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Explorador de Objetos Persistidos en el Bucket</h4>
            </div>
            <span style="font-size: 0.8rem; color: #64748B;">Bucket: <code>{bucket_config or "(sin configurar)"}</code></span>
        </div>
        """),
        unsafe_allow_html=True
    )
    objetos = listar_activos_oci(bucket_name=bucket_config or None)

    if objetos:
        st.caption(f"Se encontraron **{len(objetos)} paquetes** almacenados en el bucket:")
        for obj in objetos:
            peso_kb = round(obj.get("tamano_bytes", 0) / 1024, 2)
            with st.expander(f"{obj['ruta_objeto']} ({peso_kb} KB)"):
                st.caption(f"**Archivo:** {obj['nombre']}")
                ruta_local = Path(obj.get("ruta_local") or (
                    Path("oci_bucket_simulation") / (bucket_config or "sin-bucket") / obj["ruta_objeto"]
                ))
                if ruta_local.exists():
                    try:
                        with open(ruta_local, "r", encoding="utf-8") as f:
                            contenido = json.load(f)
                        st.json(contenido)
                        st.download_button(
                            label=f"Descargar {obj['nombre']}",
                            data=json.dumps(contenido, indent=2, ensure_ascii=False),
                            file_name=obj['nombre'],
                            mime="application/json",
                            key=f"dl_{obj['ruta_objeto']}"
                        )
                    except Exception as e:
                        st.error(f"Error al leer el objeto: {e}")
                else:
                    st.info(f"Objeto en nube OCI: {obj['ruta_objeto']}")
    else:
        st.info("Aún no se han persistido paquetes en este bucket durante la sesión. Haz clic en 'Persistir Paquete' arriba.")
