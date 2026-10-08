# MEMORY.md — CommunityLab
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no
aporte.

## Estado actual
- Fase 2 completada: `modelos.py`, `config.py`, `ingesta.py`, `almacenamiento_oci.py` y
  tests. Objeto subido con el SDK y verificado con el MCP:
  `entradas/2026-semana-04/ejemplo_1_contratacion.json`.
- Fase 3 completada: `analisis.py`, `prompts/analisis.md` y tests (44 en verde). Análisis
  con Gemini `gemini-3.5-flash-lite`, salida validada y puntuación calculada por el código.
  Prueba real con `ejemplo_1_contratacion.json`: 1 llamada y segunda pasada desde caché.
- Repo del equipo: `No-Country-simulation/G10-LATAM-CommunityLab-equipo47`; mi rama:
  `prot_rober`. Entregados: 3 lotes en `data/entrada/` y esquema en `docs/`.

## Decisiones (y por qué)
- Python + LangGraph + Streamlit; nodos como funciones normales. Gemini gratis vía
  LangChain. La app sube a OCI con el SDK (perfil `DEFAULT`); el MCP es ayuda del agente.
- Rutas `AAAA-semana-NN`: número de `periodo_referencia` con el año actual; si falta, semana
  ISO (año ISO). En `construir_nombre_objeto()` y en `AGENTS.md`.
- `subir_objeto()` no sobrescribe por defecto (`sobrescribir=False`).
- `tipo` es texto libre; `sentimiento`, `ruta` y `estado_aprobacion` son enums estrictos.
- Modelo `gemini-3.5-flash-lite` (estable). No se le pasa `temperature` (muestreo fijo, lo
  ignora); la reproducibilidad la da la caché, no la temperatura.
- Análisis: 1 llamada por lote + caché `sha256(modelo + versión prompt + hash entrada)` en
  `data/salida/cache/`. Reintentos: cliente `max_retries=1`, 429 propio respetando
  `retry_delay`, 1 reparación, tope 4 llamadas/lote (`config.py`).
- Puntuación: sub-puntuaciones del LLM y pesos en `config.py` (0.4/0.3/0.2/0.1).
- Trabajo en equipo: rama `prot_rober` → revisión → `dev` → `main`. Nunca push a `dev`/`main`.
- Formatos del MVP: post de LinkedIn + FAQ. `opencode.json` no se versiona.

## Pendiente de decidir
- Cómo comparte el equipo OCI: cada persona con su bucket o uno común (afecta `.env`).
- Revisar con el equipo los campos "propuesta" del esquema del paquete.
- Qué cuenta como "duda recurrente" (MVP: `pregunta_tecnica`; después, tema repetido).

## Aprendizajes y errores a evitar
- OpenCode no encuentra `uvx` en el PATH en Windows: usar la ruta completa en `opencode.json`.
- El token del MCP caduca en ~60 min. Si `oci session refresh` dice que no se puede refrescar,
  toca `oci session authenticate` (navegador).
- El CLI `oci` no está en el PATH del shell del agente; está en
  `%USERPROFILE%\.local\bin\oci.exe` (instalado con `uv tool`).
- Comprobar el código antes de fiarse de la documentación.

## Próximos pasos
- Fase 4 (Generación): 2 formatos (LinkedIn + FAQ) con prompts few-shot por canal.
