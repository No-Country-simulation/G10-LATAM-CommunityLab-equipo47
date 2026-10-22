# MEMORY.md — CommunityLab (dev_hackaton)

## Estado actual
- Base del proyecto: **prototipo de Alex** en `dev_hackaton` (rama `prot_rober_v2`).
- `C:\CommunityLab` (rama `prot_rober`, respaldado) es la **fuente** de piezas ya hechas.
- **Paso 0 hecho:** `AGENTS.md`, `MEMORY.md`, `docs/` (esquema + ejemplo) y `prompts/`.
- Paso 3 (pipeline real) implementado: `router.py`, `pipeline.py` y `modules/pipeline_client.py`;
  tests nuevos pendientes de ejecutar.
- Entrega funcional: **lunes 19-oct antes de las 17:00 (hora Chile)**. Demo Day: **martes
  27-oct**.
- Pendiente: integrar `communitylab/` (lógica real) sin reescribir la UI de Alex.

## Decisiones
- Paquete `communitylab/` en la raíz.
- Esquema superconjunto compatible: claves de Alex + `analisis_interacciones`, `estado_aprobacion`
  y `pregunta`/`respuesta_sugerida` opcionales; FAQ conserva `tema`/`origen`/`status`.
- `resumen_comunidad.sentimiento_predominante` usa etiqueta humana (`SENTIMIENTO_ETIQUETAS`);
  `analisis_interacciones` conserva el enum.
- Router: apoyo primero; testimonio/logro → LinkedIn con positivo/muy positivo; otros tipos solo
  con muy positivo; pregunta_tecnica/duda → FAQ. Tabla en `config.py`.
- Credenciales OCI duales (`st.secrets` y `DEFAULT`); offline etiquetado `guardado_local`; nunca
  éxito falso. `oci_client` limpia activos vacíos antes de guardar.
- Newsletter opcional; no se genera. La marca `paquete_simulado` avisa en la vista OCI.
- "Duda recurrente" = `pregunta_tecnica`/`duda`; desempate FAQ determinista.
- Tope global 12 = 3 operaciones × 4, sin contador global. Timeout LLM 120 s.
- Caché versionada para los 3 lotes de demo; modo simulado etiquetado.
- CSV, newsletter generada y LangGraph: después del lunes.
- No escribir en `oci_bucket_simulation/` por defecto.

## Pendiente de decidir / coordinar
- Esquema definitivo (campos "propuesta") y FAQ con respuesta.
- Selección: `_mejor_por_ruta`/`_puntuacion_faq` coinciden en fórmula y desempate con
  `seleccion.py`, pero el conjunto LinkedIn difiere por el umbral del router (pendiente).
- Despliegue/promoción a `main`; cambios de vistas no imprescindibles (Fullstack).
- `oci_bucket_simulation/` en git (lo consulta el usuario con Alex).

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
