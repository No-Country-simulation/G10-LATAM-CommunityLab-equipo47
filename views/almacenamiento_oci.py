"""
Vista 5: Almacenamiento en Oracle Cloud Infrastructure (OCI Object Storage).
Requisito obligatorio del MVP: Persistencia de paquetes de activos en un bucket de OCI Always Free.
Diseño modular y fácil de entender.
"""
import streamlit as st
import json
from modules.ui import badge_header, get_lucide
from modules.oci_client import guardar_en_oci, listar_activos_oci

def render_oci_storage_view():
    badge_header(
        icon_name="cloud",
        title="Almacenamiento OCI Object Storage",
        subtitle="Persistencia obligatoria de activos en un Bucket de Oracle Cloud (Capa Always Free)",
        color="#DC2626"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        bucket_name = st.text_input("Nombre del Bucket OCI Always Free", value="communitylab-activos-marketing")
    with col2:
        region = st.selectbox("Región OCI", ["sa-saopaulo-1", "sa-santiago-1", "us-ashburn-1", "us-phoenix-1"])

    st.caption("Cumplimiento estricto con las directrices de costo cero (Always Free) del programa ONE.")

    if "curated_package" not in st.session_state and "generated_package" not in st.session_state:
        st.info("Para persistir un paquete en OCI, primero procesa un lote en '2. Pipeline de IA & Router'.")
        return

    paquete_a_guardar = st.session_state.get("curated_package", st.session_state.get("generated_package"))
    ruta_sugerida = paquete_a_guardar.get("almacenamiento_oci", {}).get("ruta_objeto", "activos/paquete-distribucion.json")

    ruta_objeto = st.text_input("Ruta de destino del objeto (URI dentro del Bucket):", value=ruta_sugerida)

    if st.button("Persistir Paquete en OCI Object Storage", type="primary", use_container_width=True):
        resultado = guardar_en_oci(paquete_a_guardar, bucket_name=bucket_name, ruta_objeto=ruta_objeto)
        st.session_state["ultimo_guardado_oci"] = resultado
        st.success(f"Paquete persistido exitosamente en el Bucket {bucket_name}")

    if "ultimo_guardado_oci" in st.session_state:
        res = st.session_state["ultimo_guardado_oci"]
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
                    {get_lucide('check-circle-2', size=18, color='#059669')}
                    <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Confirmación de Almacenamiento (Esquema Oficial)</h4>
                </div>
                """,
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
                label="Descargar Paquete JSON Oficial para Evaluación",
                data=json_str,
                file_name=res.get("ruta_objeto").split("/")[-1],
                mime="application/json",
                use_container_width=True
            )

    st.divider()
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.8rem;">
            {get_lucide('file-text', size=18, color='#475569')}
            <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">Explorador de Objetos Persistidos en el Bucket</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    objetos = listar_activos_oci(bucket_name=bucket_name)

    if objetos:
        for obj in objetos:
            with st.expander(f"{obj['ruta_objeto']} ({obj['tamano_bytes']} bytes)"):
                st.caption(f"Archivo: {obj['nombre']}")
                if st.button(f"Visualizar contenido de {obj['nombre']}", key=obj['ruta_objeto']):
                    st.info(f"Visualizando objeto persistido: {obj['ruta_objeto']}")
    else:
        st.caption("Aún no se han persistido paquetes en este bucket durante la sesión.")
