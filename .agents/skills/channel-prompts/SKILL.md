---
name: channel-prompts
description: Úsala siempre que escribas, modifiques o revises prompts o plantillas de generación de contenido por canal (LinkedIn, X, FAQ, newsletter, caso de éxito) en CommunityLab.
---

# Prompts por canal

Cada canal tiene su tono y formato. Los prompts viven en `prompts/`, un archivo por canal.

## Reglas
- Tono por canal: LinkedIn inspirador y profesional; X conciso (respeta el límite de caracteres vigente, verifícalo); FAQ didáctico y claro; newsletter cercano; caso de éxito narrativo con un resultado concreto.
- Cada prompt incluye: rol, objetivo, tono, formato de salida, restricciones y 2 o 3 ejemplos (few-shot) de entrada y salida.
- Pide siempre salida estructurada (JSON validable) con los campos del activo, no texto libre.
- El contenido debe basarse solo en las interacciones recibidas: no inventes cifras, nombres ni testimonios. Si falta información, el activo lo indica.
- Textos en español. Sin datos personales reales: usa nombres o alias simulados.
- Si cambias un prompt, vuelve a ejecutar los 3 ejemplos de demo y compara el resultado.

## Checklist de revisión
- [ ] ¿El tono corresponde al canal?
- [ ] ¿Hay ejemplos few-shot y son coherentes con el formato de salida?
- [ ] ¿El activo cita algo que no está en las interacciones?
- [ ] ¿Cabe en el límite del canal?
- [ ] ¿La salida pasa la validación de Pydantic?

## Al terminar
Indica qué puntos del checklist has comprobado y cómo.
