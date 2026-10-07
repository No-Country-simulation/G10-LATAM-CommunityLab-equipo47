---
description: Planifica una nueva funcionalidad antes de tocar código
agent: plan
---
Quiero añadir esta funcionalidad: $ARGUMENTS

Antes de escribir código, prepárame un plan con:
1. Cómo la vas a implementar, respetando las reglas de AGENTS.md y las skills que apliquen.
2. Qué archivos vas a crear o modificar y qué cambia en cada uno.
3. Qué nodo del grafo o módulo afecta, y si toca OCI, el LLM o el esquema del JSON de salida.
4. Los casos límite, los costes o límites de cuota (Gemini, OCI) y las dudas que debo decidir yo antes de empezar.
5. Cómo lo vamos a probar (tests y prueba manual).
6. Qué actualizarías en AGENTS.md y en MEMORY.md.

Ten en cuenta el estado actual del proyecto: @MEMORY.md

No modifiques ningún archivo hasta que apruebe el plan.
