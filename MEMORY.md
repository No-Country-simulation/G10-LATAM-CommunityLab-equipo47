# MEMORY.md — CommunityLab
Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no
aporte.

## Estado actual
- Fases 2 y 3 hechas: `modelos.py`, `config.py`, `ingesta.py`, `almacenamiento_oci.py`,
  `llm.py` y `analisis.py`. Objeto subido con el SDK y verificado con el MCP
  (`entradas/2026-semana-04/ejemplo_1_contratacion.json`).
- Fase 4 completada: generadores de LinkedIn y FAQ (prompts `linkedin.md`/`faq.md` y caché
  por activo). **75 tests en verde** y 3 pruebas reales (LinkedIn con `ejemplo_1`; análisis
  y FAQ con `ejemplo_2`).
- Repo del equipo: `No-Country-simulation/G10-LATAM-CommunityLab-equipo47`; rama `prot_rober`.

## Decisiones (y por qué)
- Python + LangGraph + Streamlit; nodos como funciones normales. Gemini gratis vía
  LangChain. La app sube a OCI con el SDK (perfil `DEFAULT`); el MCP es ayuda del agente.
- Rutas `AAAA-semana-NN`: número de `periodo_referencia` con el año actual; si falta, semana
  ISO (año ISO). En `construir_nombre_objeto()` y en `AGENTS.md`.
- `subir_objeto()` no sobrescribe por defecto (`sobrescribir=False`).
- `tipo` es texto libre; `sentimiento`, `ruta` y `estado_aprobacion` son enums estrictos.
- Modelo `gemini-3.5-flash-lite` (estable). No se le pasa `temperature` (muestreo fijo, lo
  ignora); la reproducibilidad la da la caché, no la temperatura.
- Análisis y generadores: 1 llamada por operación + caché `sha256(modelo + versión prompt +
  hash de la entrada)` en `data/salida/cache/`. Reintentos: cliente `max_retries=1`, 429
  propio respetando `retry_delay`, 1 reparación; topes 4 por operación y 12 por lote.
- Puntuación: sub-puntuaciones del LLM y pesos en `config.py` (0.4/0.3/0.2/0.1).
- Trabajo en equipo: rama `prot_rober` → revisión → `dev` → `main`. Nunca push a `dev`/`main`.
- Formatos del MVP: post de LinkedIn + FAQ. `opencode.json` no se versiona.
- Equipo: bucket OCI común; clave de Gemini compartida por ahora (500/día y 15/min entre
  todos). Por eso: 1 llamada por operación + caché + espera.

## Pendiente de decidir (reunión del 9-oct)
- FAQ: ¿respuesta generada por el LLM o solo tema y pregunta?
- Solapamiento entre `status` y `estado_aprobacion` de la FAQ.
- Empate casi técnico en la elección de la FAQ (Carlos 80.5 vs Valeria 79.8): revisar pesos.
- Qué cuenta como "duda recurrente" (MVP: `pregunta_tecnica`; después, tema repetido).

## Aprendizajes y errores a evitar
- OpenCode no encuentra `uvx` en el PATH en Windows: usar la ruta completa en `opencode.json`.
- El token del MCP caduca en ~60 min. Si `oci session refresh` dice que no se puede refrescar,
  toca `oci session authenticate` (navegador).
- El CLI `oci` no está en el PATH del shell del agente; está en
  `%USERPROFILE%\.local\bin\oci.exe` (instalado con `uv tool`).
- Comprobar el código antes de fiarse de la documentación.

## Próximos pasos
- Fase 5: router con bifurcación, aplicar el tope global de 12 llamadas por lote y la espera
  entre operaciones, armar `paquete-distribucion.json` y subirlo a OCI (`activos/AAAA-semana-NN/`).
