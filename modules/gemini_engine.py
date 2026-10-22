import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env si existe
load_dotenv()

def obtener_api_key():
    # 1. Intentar desde streamlit secrets si existe
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
    except Exception:
        pass
    
    # 2. Intentar desde variable de entorno o .env
    return os.getenv('GEMINI_API_KEY', '')

def procesar_con_gemini(payload: dict, modelo_nombre: str = 'gemini-2.5-flash') -> tuple[dict, bool, str]:
    '''
    Procesa el payload utilizando la API real de Google Gemini.
    Devuelve (paquete_estructurado, fue_exitoso, mensaje_estado).
    Si falla o no hay clave, hace fallback seguro al motor simulado.
    '''
    api_key = obtener_api_key()
    if not api_key:
        from modules.mock_engine import process_community_payload
        paquete = process_community_payload(payload)
        paquete['motor_utilizado'] = 'Modo Simulado / Fallback (Falta API Key)'
        return paquete, False, 'No se encontro GEMINI_API_KEY configurada. Se utilizo el Modo Simulado.'

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        interacciones = payload.get('interacciones', [])
        periodo = payload.get('periodo_referencia', 'Semestre_Actual')
        origen = payload.get('origen_comunidad', 'Campus_Virtual')
        total = len(interacciones)

        prompt = f'''Eres un analista de comunidades y redactor especializado en educacion tecnologica superior (Hackathon ONE G10 / Oracle Cloud / Alura).
Analiza este lote de interacciones de la comunidad digital:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Genera un activo de distribucion de marketing adaptado a las reglas del Hackathon ONE:
1. Resumen de sentimiento y temas clave.
2. Post de LinkedIn: inspirador, profesional, enfocado en logros reales, estudiantes contratados o avances de proyectos (300 a 1000 caracteres, cerrando con 3 a 5 hashtags pertinentes como #OracleCloud #ComunidadONE #EducacionSuperior).
3. Destaque de Newsletter Semanal: seccion, titular atractivo y resumen (3-4 frases).
4. Sugerencia de Contenido FAQ / Tip Rapido: tema tecnico abordado, origen de la consulta y status ("derivado_a_mentoria" o similar).

Devuelve UNICAMENTE un objeto JSON valido con la siguiente estructura:
{{
  "sentimiento_predominante": "string descriptivo del sentimiento general",
  "temas_principales": ["tema1", "tema2", "tema3"],
  "post_linkedin": {{
    "titulo": "titulo llamativo para el post",
    "copy": "texto completo del post listo para publicar en LinkedIn con hashtags al final",
    "canal_recomendado": "LinkedIn Oficial / Red Alumni",
    "potencial_engagement": "Alto"
  }},
  "destaque_newsletter_semanal": {{
    "seccion": "Logro Estudiantil / Pulso de la Comunidad",
    "titular": "titular del boletin",
    "resumen": "resumen sintetico para el newsletter"
  }},
  "sugerencia_contenido_faq": {{
    "tema": "Tip Rapido o Resolucion de duda tecnica frecuente",
    "origen": "Canal o estudiante de donde surge la consulta",
    "status": "derivado_a_mentoria"
  }}
}}
'''

        res = client.models.generate_content(
            model=modelo_nombre,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )

        datos_ia = json.loads(res.text)
        timestamp_folder = datetime.datetime.now().strftime('%Y-%m-%d')
        periodo_norm = periodo.lower().replace("_", "-")
        nombre_archivo = "paquete-distribucion.json"

        paquete_final = {
            'status': 'exito',
            'motor_utilizado': f'Google Gemini ({modelo_nombre}) [En vivo]',
            'resumen_comunidad': {
                'total_interacciones_procesadas': total,
                'sentimiento_predominante': datos_ia.get('sentimiento_predominante', 'Positivo'),
                'temas_principales': datos_ia.get('temas_principales', ['Educacion', 'Tecnologia'])
            },
            'activos_distribucion_generados': {
                'post_linkedin': datos_ia.get('post_linkedin', {}),
                'destaque_newsletter_semanal': datos_ia.get('destaque_newsletter_semanal', {}),
                'sugerencia_contenido_faq': datos_ia.get('sugerencia_contenido_faq', {})
            },
            'almacenamiento_oci': {
                'bucket': 'communitylab-activos-marketing',
                'ruta_objeto': f'activos/2026-{periodo_norm}/{nombre_archivo}',
                'status': 'guardado_con_exito'
            }
        }
        return paquete_final, True, f'Procesado exitosamente con {modelo_nombre} en vivo.'

    except Exception as e:
        from modules.mock_engine import process_community_payload
        paquete = process_community_payload(payload)
        paquete['motor_utilizado'] = f'Modo Simulado / Fallback (Error Gemini: {str(e)[:60]})'
        return paquete, False, f'Error al conectar con Gemini: {str(e)}'
