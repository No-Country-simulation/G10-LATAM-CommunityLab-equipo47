# Rol

Actúa como desarrollador Python senior que escribe código simple, claro y bien probado, pensado para que otras personas del equipo puedan revisarlo y evaluarlo.

# Contexto

Estoy desarrollando "CommunityLab" para el Hackathon ONE G10 (Oracle Next Education & Alura): un MVP que recibe interacciones de una comunidad digital, las analiza con un LLM (Gemini vía LangChain) y genera activos de marketing listos para publicar, guardándolos en OCI Object Storage. El flujo será un grafo pequeño de LangGraph (ingesta → análisis → puntuación → router → generadores → subida a OCI) con interfaz en Streamlit.

Trabajo en equipo en mi rama personal. Lee antes `AGENTS.md`, `MEMORY.md` y `docs/esquema-paquete-distribucion.md`. El OCI ya está listo: bucket `communitylab-activos-marketing` vacío, y el MCP de OCI funciona en este proyecto.

# Tarea

Fase 2: datos y OCI. Antes de programar, preséntame un plan (como el comando `/feature`) y espera mi aprobación. Después:

1. Ya existen 3 lotes simulados en `data/entrada/` (contratación, dudas de soporte y feedback mixto). Escribe en `src/communitylab/ingesta.py` la lectura y validación de un lote JSON.
2. Lee `docs/esquema-paquete-distribucion.md` y crea los modelos de datos (entrada y paquete de salida) en `src/communitylab/modelos.py` y la lectura de configuración en `src/communitylab/config.py` (variables de `.env`).
3. Crea `src/communitylab/almacenamiento_oci.py` con el SDK de Python de OCI (perfil `DEFAULT`): subir un objeto y listar objetos, siguiendo la convención `entradas/`, `informes/`, `activos/` por `AAAA-semana-NN`.
4. Haz una prueba real: sube un lote de entrada y compruébalo con `list_objects` del MCP.
5. Añade tests con `pytest` para lo que no dependa de la red (nombres de objeto, lectura de los 3 lotes, validación del ejemplo `docs/ejemplo-paquete-distribucion.json`).

# Restricciones y reglas

- Solo recursos Always Free. No toques credenciales, claves ni otros compartimentos.
- Pregunta antes de subir o sobrescribir objetos en OCI y antes de añadir dependencias.
- No añadas nada que no aparezca en este mensaje: nada de LLM, grafo ni Streamlit todavía.
- Si no estás seguro de un nombre de paquete, una opción o un límite, dilo y verifícalo en la documentación oficial.
- Comandos para PowerShell en Windows. Textos y comentarios en español.

# Formato de salida

1. Primero, el plan y las dudas que debo decidir.
2. Tras mi aprobación, crea los archivos directamente en el proyecto.
3. Al terminar, responde con:
   - Un resumen de 3-4 líneas de lo que has creado.
   - Los pasos para probarlo en PowerShell.
   - Cualquier decisión que hayas tomado por tu cuenta y que yo deba revisar.
4. Actualiza `MEMORY.md`.
