# MEMORY.md — CommunityLab
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no
aporte.

## Estado actual
- Fase 1 (base del repositorio): paquete de archivos de desarrollo generado; falta
  `git init`/clonar el repo del equipo y copiarlo.
- Repo del equipo: `No-Country-simulation/G10-LATAM-CommunityLab-equipo47`; mi rama:
  `prot_rober`.
- Entregados: 3 lotes de ejemplo en `data/entrada/`, esquema del paquete en `docs/`.
- OCI listo: bucket `communitylab-activos-marketing` vacío, MCP funcionando en OpenCode.
- Sin código de la aplicación todavía.

## Decisiones (y por qué)
- Python + LangGraph + Streamlit: la bifurcación encaja con un grafo y todo vive en un
  lenguaje. Nodos como funciones normales para poder bajar a Python simple.
- Gemini (capa gratuita) vía LangChain: sin coste y cambiable a otro proveedor con
  configuración. n8n queda como diferencial opcional al final.
- La app sube a OCI con el SDK (perfil `DEFAULT`); el MCP es solo ayuda del agente.
- Trabajo en equipo: rama `prot_rober` → revisión de compañeros → `dev` → `main`. El agente
  nunca hace push a `dev` ni `main`.
- Formatos del MVP: post de LinkedIn + FAQ (confirmado). Newsletter opcional.
- `opencode.json` no se versiona (lleva rutas locales); se comparte `opencode.example.json`.

## Pendiente de decidir
- Cómo comparte el equipo OCI: cada persona con su bucket o uno común (el equipo avisará;
  afecta `.env`).
- Semana en `AAAA-semana-NN`: ISO (confirmado) vs número de `periodo_referencia` (lo usa el
  ejemplo de la consigna). Hoy: `periodo_referencia` y, si falta, ISO.
- Revisar con el equipo los campos "propuesta" del esquema del paquete.
- Qué cuenta como "duda recurrente" (MVP: `pregunta_tecnica`; después, tema repetido).
- Modelo de Gemini: `gemini-2.5-flash` (el que ya se usó); comprobar que siga gratuito.

## Aprendizajes y errores a evitar
- OpenCode no encuentra `uvx` en el PATH en Windows: usar la ruta completa en
  `opencode.json`.
- El token de sesión del MCP caduca en ~60 min: renovarlo antes de pedir tareas de OCI.
- Comprobar el código antes de fiarse de la documentación (lección de Diario de Estudio).

## Próximos pasos
- Fase 2: lector de los 3 lotes, modelos, `config.py` y módulo de subida a OCI con el SDK;
  prueba real con `list_objects` del MCP.
