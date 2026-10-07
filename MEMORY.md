# MEMORY.md — CommunityLab
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no
aporte.

## Estado actual
- Fase 2 completada: `config.py`, `modelos.py`, `ingesta.py`, `almacenamiento_oci.py`,
  `pytest.ini` y tests (30 en verde con `pytest`). Sin LLM, grafo ni Streamlit todavía.
- Objeto subido con el SDK (perfil `DEFAULT`) y verificado con el MCP:
  `entradas/2026-semana-04/ejemplo_1_contratacion.json`.
- Repo del equipo: `No-Country-simulation/G10-LATAM-CommunityLab-equipo47`; mi rama:
  `prot_rober`. Entregados: 3 lotes en `data/entrada/` y esquema del paquete en `docs/`.

## Decisiones (y por qué)
- Python + LangGraph + Streamlit: la bifurcación encaja con un grafo y todo vive en un
  lenguaje. Nodos como funciones normales para poder bajar a Python simple.
- Gemini (capa gratuita) vía LangChain: sin coste y cambiable a otro proveedor con
  configuración. n8n queda como diferencial opcional al final.
- La app sube a OCI con el SDK (perfil `DEFAULT`); el MCP es solo ayuda del agente.
- Rutas `AAAA-semana-NN`: número de `periodo_referencia` con el año actual; si no trae
  número, semana ISO (año ISO). En `construir_nombre_objeto()` y en `AGENTS.md`.
- `subir_objeto()` no sobrescribe por defecto (`sobrescribir=False`); avisar antes de subir.
- `tipo` es texto libre (no rompe la ingesta); `sentimiento`, `ruta` y `estado_aprobacion`
  son enums estrictos.
- Trabajo en equipo: rama `prot_rober` → revisión de compañeros → `dev` → `main`. El agente
  nunca hace push a `dev` ni `main`.
- Formatos del MVP: post de LinkedIn + FAQ (confirmado). Newsletter opcional.
- `opencode.json` no se versiona (lleva rutas locales); se comparte `opencode.example.json`.

## Pendiente de decidir
- Cómo comparte el equipo OCI: cada persona con su bucket o uno común (el equipo avisará;
  afecta `.env`).
- Revisar con el equipo los campos "propuesta" del esquema del paquete.
- Qué cuenta como "duda recurrente" (MVP: `pregunta_tecnica`; después, tema repetido).
- Modelo de Gemini: `gemini-2.5-flash` (el que ya se usó); comprobar que siga gratuito.

## Aprendizajes y errores a evitar
- OpenCode no encuentra `uvx` en el PATH en Windows: usar la ruta completa en
  `opencode.json`.
- El token del MCP caduca en ~60 min. Si `oci session refresh` responde que la sesión ya no
  se puede refrescar, toca `oci session authenticate` (abre el navegador).
- El CLI `oci` no está en el PATH del shell del agente; está en
  `%USERPROFILE%\.local\bin\oci.exe` (instalado con `uv tool`).
- Comprobar el código antes de fiarse de la documentación (lección de Diario de Estudio).

## Próximos pasos
- Fase 3 (Análisis): sentimiento y temas con Gemini, salida validada con Pydantic y
  puntuación de relevancia explicable.
