# AGENTS.md — CommunityLab (prototipo de Alex + pipeline real)

MVP del Hackathon ONE G10 (Oracle Next Education & Alura): recibe interacciones de una
comunidad digital, las analiza con un LLM y genera activos de marketing listos para
publicar, que guarda en OCI Object Storage.

Este repositorio (`dev_hackaton`) es la **BASE** del proyecto: el prototipo de Alex. La
lógica real se integra desde la rama `prot_rober` (`C:\CommunityLab`, de solo lectura para
esta tarea) **sin reescribir la UI ni la estructura de Alex**.

## Stack y estructura
- Python 3.11+ (verificar la versión real en Streamlit Cloud), Streamlit y pandas. LLM:
  Gemini vía LangChain (`langchain-google-genai`). Almacenamiento: OCI Object Storage con
  el SDK `oci`. Validación: Pydantic. Tests: pytest.
- `app.py`: entrypoint (login, navegación y despacho de vistas).
- `modules/`: `auth.py`, `ui.py`, `mock_engine.py` (a reemplazar por el pipeline real) y
  `oci_client.py` (adaptador delgado sobre `communitylab/almacenamiento_oci.py`).
- `views/`: una vista por archivo (`render_*_view`). Cambios **mínimos**: conectar el
  pipeline real y mostrar errores reales; el resto se coordina con Fullstack.
- `communitylab/`: lógica del proyecto (`modelos.py`, `config.py`, `ingesta.py`, `llm.py`,
  `analisis.py`, `router.py`, `generadores/`, `almacenamiento_oci.py`, `pipeline.py`). Es
  la **fuente de verdad**. `grafo.py` es **opcional**: el pipeline será de funciones
  simples y LangGraph solo se usará si sobra tiempo.
- `prompts/`: un archivo por canal.
- `data/samples/`: los 8 lotes de Alex. `docs/`: esquema y ejemplo del paquete.
- `tests/`: pruebas con pytest (LLM y OCI simulados).
- `oci_bucket_simulation/`: legado del prototipo. **No se escribe ahí por defecto.**

## Comandos (PowerShell)
- Instalar dependencias: `pip install -r requirements.txt` (preguntar antes).
- Interfaz: `streamlit run app.py`
- Tests: `pytest`

## LLM (Gemini)
- Modelo y clave desde `.env` o `.streamlit/secrets.toml`; nunca en el código.
- No pasar `temperature` a los modelos de muestreo fijo (`gemini-3.5-flash-lite`,
  `gemini-3.6-flash`); en el resto, `0`. La reproducibilidad la da la caché.
- Una llamada por operación (el análisis recibe el lote completo; cada generador, una
  interacción). Presupuesto y topes en `config.py`.
- Caché versionada por modelo + versión del prompt + hash de la entrada, también para los
  generadores. Los 3 lotes de la demo tendrán caché versionada.
- Reintentos acotados: cliente `max_retries=1` (sin reintentos ocultos); ante un 429 se
  respeta `retry_delay`; si la salida no valida o no cumple el canal, **una** reparación.
- Prompts en `prompts/`, no incrustados en el código. Defensa ante instrucciones
  inyectadas en el texto de la comunidad.
- **Modo simulado** claramente etiquetado (sin llamadas reales) para que la demo no dependa
  de la cuota de Gemini. Nunca presentarlo como si fuera el LLM real.

## Esquema del paquete (superconjunto compatible)
- **Conservar** las claves que ya usan las vistas de Alex: `resumen_comunidad`,
  `activos_distribucion_generados`, `almacenamiento_oci` y `estado_curaduria`.
- **Añadir como opcionales:** `analisis_interacciones[]`, `estado_aprobacion` y, en la FAQ,
  `pregunta` y `respuesta_sugerida`.
- **FAQ:** conservar `tema`, `origen` y `status` como en la consigna. `status` y
  `estado_aprobacion` **no se solapan**.
- Declarar el esquema **una sola vez** en `communitylab/modelos.py`; de ahí derivan las
  validaciones y el esquema que se pide al LLM. No cambiar el esquema sin preguntar.
- El contenido de los activos se basa **solo** en las interacciones: nada de cifras,
  nombres ni testimonios inventados.

## Router
- Tabla de tipos en `config.py`, incluidos los de Alex: `testimonio`/`logro` →
  `post_linkedin`; `pregunta_tecnica`/`duda` → `faq`; `alerta_apoyo`/`dificultades` →
  `apoyo`; el resto → `sin_activo`.
- "Duda recurrente" = `pregunta_tecnica` o `duda` en el MVP.
- Desempate de FAQ **determinista y documentado**. No ajustar pesos sin decisión.

## OCI Object Storage
- Credenciales **duales**: `st.secrets` con prioridad; perfil `DEFAULT` en local. El chequeo
  de `st.secrets` va dentro de `try/except`.
- Región, namespace y bucket por entorno o secretos, **validados**. No usar
  `sa-saopaulo-1` por defecto.
- Rutas `entradas|informes|activos/AAAA-semana-NN/`.
- **No sobrescribir sin confirmación explícita.** "Aprobar y Guardar" debe avisar si el
  objeto ya existe y pedir confirmación antes de reemplazarlo.
- Fallback local solo como **modo offline etiquetado** (`guardado_local`) y con aviso
  visible. **Nunca** mostrar éxito si no se subió a la nube.
- `modules/oci_client.py` conserva `guardar_en_oci` y `listar_activos_oci` como adaptador
  delgado, para no romper las vistas del compañero de Fullstack.
- No escribir en `oci_bucket_simulation/` por defecto. No tocar otros compartimentos
  (en especial `doguito-proyect`).

## Convenciones
- Todo en español: interfaz, prompts, documentación y comentarios.
- Funciones pequeñas, con tipos. Salidas del LLM validadas; si falla, reintento único y
  error claro (no un resultado a medias).
- Sin lógica de negocio en las vistas: la lógica vive en `communitylab/`.
- Ingesta JSON **y CSV** en `communitylab/ingesta.py`.
- Datos de prueba siempre simulados. Nunca datos personales reales.
- Los prompts viven en `prompts/`, no incrustados en el código.

## Forma de trabajar
- Pasos pequeños y enfocados; **esperar confirmación entre pasos**.
- No hacer push a `dev` ni a `main`, ni fusionar ramas. Rama de trabajo: `prot_rober_v2`.
- Commits pequeños con mensaje claro (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
  Proponer el mensaje y dejar que el usuario haga el commit.
- No leer ni mostrar secretos (`.env`, `.pem`, tokens). No llamar a Gemini ni subir a OCI
  sin confirmación previa. No instalar dependencias sin preguntar.
- Si no estás seguro de un dato (versiones, opciones, límites), dilo; no inventes.

## Verificación
- `pytest` para lo que no depende de red (ingesta, puntuación, router, validación, esquema).
  El LLM y OCI se simulan con mocks.
- Flujo completo con los 3 lotes de demo (caché versionada / modo simulado).
- Prueba manual de OCI solo con confirmación del usuario.
- Antes de dar algo por terminado: resumen de cambios y decisiones a revisar.
