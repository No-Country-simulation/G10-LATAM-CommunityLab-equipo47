# CommunityLab — Motor Inteligente de Transformación y Distribución para Comunidades Digitales

> Proyecto desarrollado en el marco del **Hackathon ONE – No Country G10** (Oracle Next Education & Alura LATAM)
> Demo Day: **29/10/2026**

## 📌 Problema

Las comunidades digitales (Discord, Slack, foros, GitHub, formularios) generan a diario testimonios, dudas técnicas y logros valiosos, pero ese contenido se pierde en el historial de los canales porque curarlo y transformarlo en material de marketing consume demasiadas horas de los equipos de Community Management.

## 💡 Solución

CommunityLab ingiere la actividad orgánica de una comunidad, la analiza con LLMs (sentimiento, temas, relevancia) y genera automáticamente activos de distribución listos para publicar: posts para LinkedIn, resúmenes semanales, contenido de FAQ y casos de éxito — todo sin intervención manual.

**Enfoque elegido por el equipo:** _[definir cuál de los 4 frentes prioriza el MVP — Generador de contenido para redes, Detector de historias de éxito, Motor de FAQ dinámico, o Dashboard de sentimiento — y describir en 2-3 líneas]_

## 🎯 Funcionalidades del MVP

- [ ] Ingesta de interacciones de la comunidad (JSON, CSV, webhook o integración directa)
- [ ] Análisis de sentimiento y extracción de temas con LLM (Gemini / OpenAI / Claude / equivalente)
- [ ] Generación automatizada de al menos **2 formatos** de activos de marketing (ej. Post LinkedIn + Newsletter, o Caso de Éxito + FAQ)
- [ ] Orquestación del flujo con n8n o Python (LangChain / LangGraph) o equivalente
- [ ] Interfaz de curaduría/visualización en Streamlit o Gradio
- [ ] Persistencia de los activos generados en **OCI Object Storage** (capa Always Free) — requisito obligatorio
- [ ] Demostración de al menos 3 ejemplos de transformación interacción → activo publicable

## 🏗️ Arquitectura

```
[Fuente de datos: Discord/Slack/CSV/Webhook]
            │
            ▼
   [Ingesta y limpieza de datos]
            │
            ▼
   [Análisis con LLM: sentimiento + temas]
            │
            ▼
 [Orquestación: n8n / LangChain-LangGraph]
   (bifurcación según tipo de interacción)
            │
     ┌──────┴──────┐
     ▼             ▼
[Generación de   [Generación de
 copy: LinkedIn,  FAQ / Tips /
 Newsletter, etc] Casos de éxito]
     │             │
     └──────┬──────┘
            ▼
 [OCI Object Storage – Always Free]
            │
            ▼
  [Interfaz Streamlit/Gradio: revisión y aprobación]
```

_Reemplazar por el diagrama real del pipeline una vez definida la arquitectura final del equipo._

## 🛠️ Stack

| Capa | Tecnología |
|---|---|
| LLM / IA Generativa | |
| Orquestación de flujos | n8n / LangChain / LangGraph |
| Interfaz | Streamlit / Gradio |
| Almacenamiento | OCI Object Storage (Always Free) |
| Backend | |
| Despliegue (opcional) | OCI Compute Instance (Always Free) |

## ⚙️ Cómo ejecutarlo localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/No-Country-simulation/G10-LATAM-CommunityLab-equipo47.git
cd G10-LATAM-CommunityLab-equipo47

# 2. Instalar dependencias
# ...

# 3. Variables de entorno (claves de LLM, credenciales OCI)
cp .env.example .env

# 4. Ejecutar
# ...
```

## 📥 Ejemplo de entrada / salida

**Entrada:** lote de interacciones de la comunidad (autor, canal, tipo, texto).

**Salida:** resumen de sentimiento y temas + activos generados (post LinkedIn, destaque de newsletter, sugerencia de FAQ) + confirmación de guardado en el bucket de OCI.

_Ver la especificación completa del formato de entrada/salida en `/docs` (agregar cuando esté definida)._

## ✅ Checklist de evaluación del hackathon

- [ ] Ingestión funcional de interacciones (mensajes, CSV o JSON simulando canales)
- [ ] Análisis de sentimiento y extracción de temas con LLM
- [ ] Generación de al menos 2 formatos de activos de marketing
- [ ] Orquestación del flujo (n8n / LangChain / LangGraph o equivalente)
- [ ] Integración activa con OCI Object Storage
- [ ] Demostración de mínimo 3 ejemplos de transformación
- [ ] Repositorio en GitHub con documentación y diagrama de la línea de distribución

## 🌟 Diferenciales (opcional)

- [ ] Despliegue completo en OCI Compute (VM Always Free)
- [ ] Flujo n8n con webhook directo a Discord/formularios
- [ ] Bot interactivo de comunidad (Discord/Telegram)
- [ ] Panel de curaduría en Streamlit con aprobación de publicaciones
- [ ] Generación de imágenes/banners para los posts

## 🚀 Demo

- Aplicación desplegada: _[URL]_
- Video de presentación: _[URL]_

## 👥 Equipo — G10 Equipo 47

| Nombre | Rol | GitHub | LinkedIn |
|---|---|---|---|
| | Team Leader | | |
| | IA / LLM | | |
| | Automatización (n8n/LangChain) | | |
| | Backend | | |
| | Frontend / Streamlit | | |
| | OCI / Cloud | | |
| | QA / Testing | | |
| | UX/UI | | |
| | Data | | |

## 🤝 Contribuir

Las reglas de trabajo del equipo (ramas, commits, pull requests) están en [CONTRIBUTING.md](CONTRIBUTING.md). Léelo antes de tu primer commit.

## 📄 Licencia

Distribuido bajo licencia MIT. Ver `LICENSE`.
