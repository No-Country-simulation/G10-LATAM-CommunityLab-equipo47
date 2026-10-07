---
name: langgraph-flow
description: Úsala siempre que escribas, modifiques o revises el grafo de LangGraph, sus nodos, el estado o la lógica de bifurcación (router) de CommunityLab.
---

# Grafo de CommunityLab

El grafo debe ser corto y fácil de explicar en la demo: ingesta → análisis → puntuación → router → generadores por canal → subida a OCI.

## Reglas
- Cada nodo es una función normal que recibe el estado y devuelve solo las claves que cambia. La lógica vive en los módulos; `grafo.py` solo conecta nodos.
- El estado es un tipo definido (`TypedDict` o modelo Pydantic) en `modelos.py`. No metas claves sueltas.
- El router decide con reglas simples y explicables, con umbrales en `config.py`: sentimiento muy positivo → caso de éxito; duda recurrente → tip o FAQ. Toda decisión deja un motivo en el estado.
- Las salidas del LLM se validan con Pydantic. Si falla, reintenta una vez y deja el error en el estado; nunca sigas con datos a medias.
- Los nodos con LLM u OCI reciben el cliente como parámetro para poder simularlo en los tests.
- Si LangGraph complica algo, baja a Python simple: los nodos no deben depender de LangGraph.
- Si no estás seguro de una API de LangGraph o LangChain, verifícala en la documentación oficial antes de usarla.

## Checklist de revisión
- [ ] ¿Algún nodo hace más de una cosa?
- [ ] ¿Qué pasa con un lote vacío o con una interacción sin texto?
- [ ] ¿Qué pasa si el LLM devuelve JSON inválido o llega el límite de cuota (429)?
- [ ] ¿Hay un test por rama del router?
- [ ] ¿El diagrama del README sigue coincidiendo con el grafo?

## Al terminar
Indica qué puntos del checklist has comprobado y cómo.
