# Plan por fases

Obligatorio primero; lo esperado después; los diferenciales solo si sobra tiempo.

| Fase | Objetivo | Hecho cuando |
|---|---|---|
| 1. Base | Repo, estructura, `.gitignore`, `.env.example`, `AGENTS.md`, `MEMORY.md`, README inicial | Primer commit en tu rama y el agente lee `AGENTS.md` y `MEMORY.md` |
| 2. Datos y OCI | 3 lotes simulados, modelos, `config.py`, módulo OCI con el SDK | Un objeto subido por código y verificado con `list_objects` del MCP |
| 3. Análisis | Sentimiento y temas con Gemini, salida validada, puntuación de relevancia | Un lote devuelve informe consolidado con puntuaciones explicables |
| 4. Generación | 2 formatos (propuesta: LinkedIn + FAQ), prompts por canal con few-shot | Cada formato genera un activo válido a partir de un lote |
| 5. Grafo | Router con bifurcación, `paquete-distribucion.json`, subida a OCI | Los 3 lotes recorren el grafo y quedan guardados en el bucket |
| 6. Interfaz | Streamlit: ver datos y aprobar posts | Se puede revisar y aprobar un activo desde el navegador |
| 7. Entrega | 3 ejemplos de demo, diagrama final, guía de despliegue, historial limpio | Un compañero lo instala siguiendo el README |
| 8. Diferenciales | OCI Compute, n8n, bot de Telegram/Discord, curaduría, imágenes | Solo con las fases 1 a 7 cerradas |

Las fases 1 a 5 cubren lo obligatorio. La 6 es funcionalidad esperada: protégela por
encima de cualquier diferencial.
