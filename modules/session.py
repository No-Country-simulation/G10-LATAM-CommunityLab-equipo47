"""Estado compartido del lote, resultados y borradores editoriales."""
from copy import deepcopy
import streamlit as st

EDITOR_FIELDS = {
    'input_titulo_lk': ('post_linkedin', 'titulo'),
    'textarea_copy_lk': ('post_linkedin', 'copy'),
    'curaduria_lk_radio': ('post_linkedin', 'estado_curaduria'),
    'nl_sec_input': ('destaque_newsletter_semanal', 'seccion'),
    'nl_tit_input': ('destaque_newsletter_semanal', 'titular'),
    'nl_res_input': ('destaque_newsletter_semanal', 'resumen'),
    'curaduria_nl_radio': ('destaque_newsletter_semanal', 'estado_curaduria'),
    'faq_tema_input': ('sugerencia_contenido_faq', 'tema'),
    'faq_status_select': ('sugerencia_contenido_faq', 'status'),
}


def reset_results():
    for key in ('generated_package', 'curated_package', 'oci_save_result', 'ultimo_guardado_oci', *EDITOR_FIELDS):
        st.session_state.pop(key, None)


def load_payload(payload, filename):
    """Validar antes de reemplazar el lote; no borrar ediciones en un rerun."""
    if not isinstance(payload, dict) or not isinstance(payload.get('interacciones'), list):
        raise ValueError('El JSON debe ser un objeto con una lista interacciones.')
    normalized = deepcopy(payload)
    normalized.setdefault('origen_comunidad', 'Comunidad importada')
    normalized.setdefault('periodo_referencia', 'Reciente')
    for item in normalized['interacciones']:
        if not isinstance(item, dict) or not isinstance(item.get('texto'), str) or not item['texto'].strip():
            raise ValueError('Cada interacción debe tener un texto no vacío.')
        for key, default in {'autor': 'Miembro', 'pais': 'LATAM', 'canal': '#general', 'tipo': 'mensaje'}.items():
            if not isinstance(item.get(key), str) or not item[key].strip():
                item[key] = default
    changed = normalized != st.session_state.get('raw_payload') or filename != st.session_state.get('archivo_origen')
    if changed:
        reset_results()
        st.session_state.pop('filtro_canales_ingestion', None)
        st.session_state['raw_payload'] = normalized
        st.session_state['archivo_origen'] = filename
    return changed


def store_generated(package):
    reset_results()
    st.session_state['generated_package'] = deepcopy(package)
    st.session_state['curated_package'] = deepcopy(package)


def capture_editor():
    """Guardar cambios antes de que Streamlit elimine widgets al cambiar de vista."""
    package = deepcopy(st.session_state['curated_package'])
    assets = package.setdefault('activos_distribucion_generados', {})
    for key, (asset, field) in EDITOR_FIELDS.items():
        if key in st.session_state:
            assets.setdefault(asset, {})[field] = st.session_state[key]
    st.session_state['curated_package'] = package
    st.session_state.pop('oci_save_result', None)


def restore_editor():
    assets = st.session_state['curated_package'].get('activos_distribucion_generados', {})
    for key, (asset, field) in EDITOR_FIELDS.items():
        value = assets.get(asset, {}).get(field)
        if key not in st.session_state and value is not None:
            st.session_state[key] = value
