# MEMORY.md — CommunityLab (dev_hackaton)

## Estado actual
- Base del proyecto: **prototipo de Alex** en `dev_hackaton` (rama `prot_rober_v2`).
- `C:\CommunityLab` (rama `prot_rober`, respaldado) es la **fuente** de piezas ya hechas.
- **Paso 0 hecho:** `AGENTS.md`, `MEMORY.md`, `docs/` (esquema + ejemplo) y `prompts/`.
- Entrega funcional: **lunes 19-oct antes de las 17:00 (hora Chile)**. Demo Day: **martes
  27-oct**.
- Pendiente: integrar `communitylab/` (lógica real) sin reescribir la UI de Alex.

## Decisiones
- Paquete `communitylab/` en la raíz de `dev_hackaton`.
- Esquema **superconjunto compatible**: se conservan las claves de Alex; `analisis_interacciones`,
  `estado_aprobacion` y `pregunta`/`respuesta_sugerida` son opcionales; la FAQ conserva
  `tema`/`origen`/`status`; `status` y `estado_aprobacion` no se solapan.
- Credenciales OCI **duales**: `st.secrets` (prioridad) y perfil `DEFAULT` local; región,
  namespace y bucket validados por entorno/secretos.
- Fallback OCI local solo offline, etiquetado `guardado_local` y con aviso; nunca éxito falso.
- `modules/oci_client.py` mantiene su API pública como adaptador delgado.
- Newsletter opcional; las vistas toleran su ausencia; no generarla por ahora.
- CSV en `communitylab/ingesta.py`: **después del lunes** (junto con newsletter y LangGraph).
- Router con los tipos de Alex (`logro`, `duda`, `dificultades`) y tabla en `config.py`.
- "Duda recurrente" = `pregunta_tecnica` o `duda`. Desempate FAQ determinista; pesos sin cambios.
- Caché versionada para los 3 lotes de demo + modo simulado etiquetado.
- No escribir en `oci_bucket_simulation/` por defecto.

## Pendiente de decidir / coordinar
- Esquema definitivo (campos "propuesta") y FAQ con respuesta.
- Despliegue y promoción a `main` (lo ve el equipo).
- Cambios de vistas no imprescindibles (coordinar con Fullstack).
- `oci_bucket_simulation/` en git (el usuario lo consulta con Alex).

## Errores a evitar
- `mock_engine.py` es heurístico, **NO** un LLM; no presentarlo como IA.
- No reportar éxito OCI si solo se escribió el espejo local.
- No pasar `temperature` a los modelos de muestreo fijo.
- Token del MCP caduca ~60 min; el CLI `oci` está en `%USERPROFILE%\.local\bin\oci.exe`.
- Verificar el código antes de fiarse de la documentación.

## Próximos pasos (orden)
1. Copiar `communitylab/` y pasar los tests.
2. OCI real.
3. Pipeline y router reales.
4. "Aprobar y Guardar".
5. README veraz.
- Después del lunes: CSV en `communitylab/`, newsletter y LangGraph.
