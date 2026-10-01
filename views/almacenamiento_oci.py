"""
Vista 5: Almacenamiento en Oracle Cloud Infrastructure (OCI Object Storage).
Requisito obligatorio del MVP: Persistencia de paquetes de activos en un bucket de OCI Always Free.
Diseño modular adaptado a la infraestructura del Hackathon ONE G10.
"""
import streamlit as st
import json
from pathlib import Path
from modules.ui import badge_header, get_lucide, render_callout, clean_html
from modules.oci_client import guardar_en_oci, listar_activos_oci

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
                    <strong style="color: #0F172A; font-size: 0.95rem;">Modo de Almacenamiento Activo: OCI Always Free Mirror</strong>
                </div>
                <p style="margin: 4px 0 0 0; font-size: 0.84rem; color: #64748B; line-height: 1.4;">
                    El sistema serializa los paquetes en la estructura estándar de OCI Object Storage (<code>bucket/activos/YYYY-MM-DD/objeto.json</code>) 
                    y mantiene un espejo local persistente para garantizar una demo fluida sin interrupciones por tokens o cuotas.
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

    col1, col2 = st.columns([2, 1])
    with col1:
        bucket_name = st.text_input("Nombre del Bucket OCI Always Free", value="communitylab-activos-marketing")
    with col2:
        region = st.selectbox("Región OCI", ["sa-saopaulo-1", "sa-santiago-1", "us-ashburn-1", "us-phoenix-1"])

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
    ruta_sugerida = paquete_a_guardar.get("almacenamiento_oci", {}).get("ruta_objeto", "activos/paquete-distribucion.json")

    ruta_objeto = st.text_input("Ruta de destino del objeto (URI dentro del Bucket):", value=ruta_sugerida)

    if st.button("Persistir Paquete en OCI Object Storage", type="primary", use_container_width=True):
        resultado = guardar_en_oci(paquete_a_guardar, bucket_name=bucket_name, ruta_objeto=ruta_objeto)
        st.session_state["ultimo_guardado_oci"] = resultado
        st.success(f"Paquete persistido exitosamente en el Bucket '{bucket_name}' ({resultado.get('modo')})")

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

            # Botón de descarga directa
            json_str = json.dumps(paquete_a_guardar, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Descargar Paquete JSON Oficial para Evaluación",
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
            <span style="font-size: 0.8rem; color: #64748B;">Bucket: <code>{bucket_name}</code></span>
        </div>
        """),
        unsafe_allow_html=True
    )
    objetos = listar_activos_oci(bucket_name=bucket_name)

    if objetos:
        st.caption(f"Se encontraron **{len(objetos)} paquetes** almacenados en el bucket:")
        for obj in objetos:
            peso_kb = round(obj.get("tamano_bytes", 0) / 1024, 2)
            with st.expander(f"📦 {obj['ruta_objeto']} — {peso_kb} KB"):
                st.caption(f"**Archivo:** {obj['nombre']}")
                ruta_local = Path("oci_bucket_simulation") / bucket_name / obj['ruta_objeto']
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
