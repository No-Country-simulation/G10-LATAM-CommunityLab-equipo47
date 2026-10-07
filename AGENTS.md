# AGENTS.md — CommunityLab

MVP del Hackathon ONE G10 (Oracle Next Education & Alura): recibe interacciones de una
comunidad digital, las analiza con un LLM y genera activos de marketing listos para
publicar, que guarda en OCI Object Storage. Proyecto de equipo: el código debe ser claro
para que otras personas lo revisen y lo evalúen.

## Stack y estructura
- Python + LangGraph (grafo corto) + Streamlit. LLM: Gemini vía LangChain
  (`langchain-google-genai`). Almacenamiento: OCI Object Storage con el SDK `oci`.
- Gestor de entorno: `uv`. Dependencias en `requirements.txt`.
- `src/communitylab/`: lógica (`modelos.py`, `config.py`, `ingesta.py`, `analisis.py`,
  `puntuacion.py`, `router.py`, `generadores/`, `almacenamiento_oci.py`, `grafo.py`).
- `app/streamlit_app.py`: interfaz (ver datos, aprobar posts). Sin lógica de negocio.
- `prompts/`: un archivo por canal (LinkedIn, X, FAQ, newsletter, caso de éxito).
- `data/entrada/`: datos simulados. `data/salida/`: resultados locales (no se versiona).
- `tests/`, `docs/`, `.agents/skills/`, `.opencode/commands/`.
- Flujo del grafo: ingesta → análisis → puntuación → router → generadores por canal →
  subida a OCI. Cada nodo es una función normal que recibe y devuelve el estado, para
  poder bajar a Python simple sin reescribir la lógica.

## Comandos (PowerShell, Windows)
- Crear entorno: `uv venv` y `.venv\Scripts\Activate.ps1`
- Instalar: `uv pip install -r requirements.txt`
- Interfaz: `streamlit run app/streamlit_app.py`
- Tests: `pytest`
- Config local: copiar `.env.example` a `.env` y `opencode.example.json` a `opencode.json`.

## LLM (Gemini)
- Modelo y clave vienen de `.env` (`GEMINI_MODEL`, `GEMINI_API_KEY`); nunca en el código.
- Análisis: `temperature=0`. Generación de copys: algo más alta si se necesita variedad.
- Respeta las cuotas de la capa gratuita: pocas llamadas por lote (una por interacción para
  el análisis y una por activo), reintentos con espera y mensaje claro ante un error 429.
- Verifica en la documentación oficial el nombre del parámetro de la clave en
  `langchain-google-genai` antes de usarlo.

## Convenciones
- Todo en español: interfaz, prompts, documentación y comentarios. Nombres de código
  descriptivos y, por coherencia con el equipo, en español o inglés pero sin mezclar en un
  mismo módulo.
- Funciones pequeñas, con tipos. Las salidas del LLM se validan con Pydantic; si falla la
  validación, reintenta una vez y devuelve un error claro (no un resultado a medias).
- Sin lógica de negocio en Streamlit y sin llamadas al LLM fuera de `analisis.py` y
  `generadores/`.
- Los prompts viven en `prompts/`, no incrustados en el código.

## Reglas de dominio
- Entrada: lote de interacciones (JSON o CSV simulando canales). Hay 3 lotes de ejemplo en
  `data/entrada/`. Salida: análisis consolidado (sentimiento y temas) + activos generados
  + `paquete-distribucion.json`. El esquema está en `docs/esquema-paquete-distribucion.md`
  (parte de la consigna, parte propuesta del equipo) y un ejemplo en
  `docs/ejemplo-paquete-distribucion.json`. No cambies el esquema sin preguntar.
- Formatos del MVP (confirmado): `post_linkedin` + `sugerencia_contenido_faq`. El
  `destaque_newsletter_semanal` es opcional.
- Bifurcación del router (campo `ruta`): sentimiento muy positivo o testimonio →
  `post_linkedin` (el caso de éxito del MVP); duda técnica → `faq`; `alerta_apoyo` →
  `apoyo` (solo se marca, sin activo); el resto → `sin_activo`. Los umbrales viven en
  `config.py`, no dispersos por el código.
- Puntuación de relevancia: número explicable (por qué sube o baja) para elegir los
  mejores momentos de la comunidad.
- Prompts por canal con ejemplos (few-shot): LinkedIn inspirador, X conciso, FAQ didáctico.
- Datos de prueba siempre simulados. Nunca datos personales reales (la capa gratuita de
  Gemini puede usar el contenido enviado para mejorar productos de Google).

## OCI Object Storage
- Región `sa-santiago-1`. Compartimento `communitylab`. Bucket
  `communitylab-activos-marketing` (Standard, privado). Solo recursos Always Free.
- **La aplicación** sube con el SDK de Python y el perfil `DEFAULT` (clave de API). El
  **MCP** (`oci-object-storage`, perfil `communitylab`, token de sesión) es solo ayuda
  para el agente de desarrollo: la consigna exige la integración dentro de la aplicación.
- Convención de objetos: `entradas/AAAA-semana-NN/`, `informes/AAAA-semana-NN/`,
  `activos/AAAA-semana-NN/` (incluye `paquete-distribucion.json`). Ejemplo:
  `activos/2026-semana-04/paquete-distribucion.json`. El número de semana sale de
  `periodo_referencia` (p. ej. `Semana_04_Sprints`) con el año actual; si no trae número, se
  usa la semana ISO de `isocalendar()` (con el año ISO, no el del calendario). La construye
  `construir_nombre_objeto()` en `almacenamiento_oci.py`. No cambiar sin preguntar.
- Namespace, bucket y región vienen de variables de entorno, no de constantes en el código.
- El MCP no tiene herramienta para borrar. Si hay que borrar o sobrescribir, avisa al
  usuario.
- `subir_objeto()` no sobrescribe por defecto (`sobrescribir=False`): si el objeto ya
  existe, lanza error. Solo se usa `sobrescribir=True` cuando el equipo lo decida, y se
  avisa siempre antes de subir.
- Token de sesión caducado (~60 min): `oci session refresh --profile communitylab`.
  Si ya pasó el máximo: `oci session authenticate --region sa-santiago-1 --tenancy-name lonkonueo --profile-name communitylab`.
- Usa las herramientas del MCP en lugar de leer el sistema de archivos para consultar OCI.
- No toques credenciales ni otros compartimentos (en especial `doguito-proyect`).

## Forma de trabajar
- Haz solo lo que se pide: no añadas funcionalidades por tu cuenta.
- Para funcionalidades nuevas, planifica antes con `/feature` y espera aprobación.
- Cambios pequeños y enfocados; no reescribas lo que ya funciona.
- Git: repo del equipo `No-Country-simulation/G10-LATAM-CommunityLab-equipo47`. El
  usuario trabaja en su rama `prot_rober`. Nunca hagas push a `dev` ni `main`, ni
  fusiones ramas. Commits pequeños con mensaje claro (`feat:`, `fix:`, `docs:`, `test:`,
  `chore:`). Propón el mensaje y deja que el usuario haga el commit si no lo pide.
- Si no estás seguro de un dato (nombres de paquetes, versiones, opciones de comandos,
  límites de OCI o de Gemini), dilo y verifícalo en la documentación oficial. No inventes.
- Al terminar, resume qué has cambiado y cualquier decisión que deba revisar.

## Memoria
- Al empezar, lee `MEMORY.md` para conocer el estado y las decisiones tomadas.
- Al terminar una tarea, actualízalo: estado, decisiones (con su porqué) y errores a evitar.
- Máximo ~50 líneas: resume o elimina lo que ya no aporte.
- Si algo se vuelve regla permanente, propón moverlo a `AGENTS.md`.
- Nunca guardes datos sensibles (claves, tokens, `.pem`, datos personales).

## Límites
- ✅ Siempre: textos en español, secretos solo en `.env`, actualizar `MEMORY.md`.
- ✅ Siempre: validar las salidas del LLM y manejar errores de red/cuotas con mensajes claros.
- ⚠️ Pregunta antes: subir o sobrescribir objetos en OCI, crear archivos nuevos fuera de la
  estructura, añadir dependencias, cambiar el esquema del JSON de salida.
- 🚫 Nunca: crear recursos de pago, leer o mostrar claves/`.pem`/tokens, buscar en la web
  sin que se pida, tocar otros compartimentos, hacer push a `dev`/`main`.

## Verificación
- `pytest` para lo que no depende de red (ingesta, puntuación, router, validación). El LLM
  y OCI se simulan (mocks) en los tests.
- Prueba manual de OCI: subir un objeto de prueba y comprobarlo con `list_objects` del MCP.
- Prueba manual de la interfaz: `streamlit run app/streamlit_app.py`.
- Antes de dar algo por terminado, ejecuta el flujo completo con los 3 ejemplos de demo.
