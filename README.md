# CommunityLab — Motor Inteligente de Transformación y Distribución para Comunidades Digitales

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://proyectohackathon-vmuqmx28sqeyagkyoebamt.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Oracle Cloud](https://img.shields.io/badge/Oracle_Cloud-OCI_Always_Free-F80000?logo=oracle&logoColor=white)](https://cloud.oracle.com)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Proyecto desarrollado en el marco del **Hackathon ONE – No Country G10**  
> **Oracle Next Education & Alura LATAM** · **Equipo 47**  
> Sector: **MarTech / Gestión de Comunidades Digitales / Educación Superior Tecnológica**  
> Demo Day: **29/10/2026**

---

## 🚀 Demostración en Vivo (Acceso Directo)

La aplicación se encuentra desplegada y operativa en producción en **Streamlit Cloud**:

👉 **[Abrir CommunityLab | Equipo 47 ONE LATAM · Streamlit](https://proyectohackathon-vmuqmx28sqeyagkyoebamt.streamlit.app/)** 👈

- **Usuario de evaluación:** `admin`
- **Contraseña:** `admin`
- **Repositorio oficial:** [GitHub: G10-LATAM-CommunityLab-equipo47](https://github.com/No-Country-simulation/G10-LATAM-CommunityLab-equipo47)

---

## 📌 El Problema

Las comunidades digitales activas (servidores de Discord, canales de Slack, foros académicos de Moodle, GitHub Discussions y formularios de retroalimentación) generan diariamente decenas de testimonios de inserción laboral, consultas técnicas enriquecedoras e ideas de proyectos.

Sin embargo, **el 85% de este contenido de alto valor se pierde en el historial de los canales**. Curar, resumir y redactar manualmente publicaciones adaptadas a diferentes redes sociales (LinkedIn, boletines informativos por correo, FAQs y tutoriales) consume entre **10 y 15 horas semanales** a los equipos de Community Management, Prensa y Admisiones.

---

## 💡 La Solución: CommunityLab

**CommunityLab** es una plataforma inteligente que ingesta en lote o en tiempo real las conversaciones orgánicas de una comunidad digital, las analiza semánticamente mediante Modelos de Lenguaje (LLMs) y, a través de un **Router Condicional automatizado**, bifurca la información para generar simultáneamente activos de marketing listos para publicar:

1. **Detector de Historias de Éxito & UGC Marketing:** Identifica contrataciones, ascensos y proyectos destacados para redactar posts persuasivos para **LinkedIn** y redes sociales.
2. **Resumen y Síntesis de Comunidad:** Extrae el pulso semanal y los temas en tendencia para generar el bloque principal de la **Newsletter**.
3. **Motor de FAQ Dinámico & Tips de Cátedra:** Detecta dudas técnicas recurrentes sobre laboratorios o herramientas para derivarlas a mentoría par o material de ayuda rápida.
4. **Dashboard de Salud y Sentimiento:** Monitorea el clima comunitario en tiempo real, detectando alertas tempranas de sobrecarga o estudiantes que requieren apoyo.
5. **Persistencia en la Nube:** Almacena todos los paquetes de activos generados en **Oracle Cloud Infrastructure (OCI) Object Storage** bajo la capa gratuita **Always Free**.

---

## 🏗️ Arquitectura del Sistema

```mermaid
flowchart TD
    subgraph INGESTA["1. Capa de Ingestión"]
        A1["Discord (Canales de Soporte y Wins)"] --> INGEST["Módulo de Ingestión & Limpieza"]
        A2["Slack / Foros de Cátedra"] --> INGEST
        A3["Datasets JSON / CSV (Samples)"] --> INGEST
    end

    subgraph IA_ROUTER["2. Motor de IA & Router Condicional"]
        INGEST --> LLM["Análisis Semántico & Extracción de Entidades<br/>(Google Gemini / OpenAI / Heurística)"]
        LLM --> ROUTER{"Router Condicional<br/>(Bifurcación por Intención)"}
        ROUTER -->|"Testimonio / Empleo"| LNK["Generación Copy LinkedIn<br/>(Tono UGC Persuasivo + Hashtags)"]
        ROUTER -->|"Pulso General / Logros"| NWS["Destaque Newsletter Semanal<br/>(Titular + Resumen Editorial)"]
        ROUTER -->|"Duda Técnica Frecuente"| FAQ["Sugerencia FAQ / Tip de Cátedra<br/>(Derivado a Mentoría / Soporte)"]
    end

    subgraph CURADURIA["3. Panel de Curaduría (Human-in-the-Loop)"]
        LNK --> EDIT["Edición en Vivo (st.text_area)"]
        NWS --> EDIT
        FAQ --> EDIT
        EDIT --> APROB["Aprobación y Visto Bueno Institucional"]
    end

    subgraph OCI["4. Persistencia en la Nube (Always Free)"]
        APROB --> SDK["OCI Object Storage Client<br/>(oci.object_storage.ObjectStorageClient)"]
        SDK --> BUCKET[("Bucket OCI Always Free<br/>communitylab-activos-marketing")]
    end

    subgraph METRICAS["5. Dashboard & Salud Comunitaria"]
        LLM --> DASH["Métricas de Sentimiento & Alertas Tempranas"]
    end
```

---

## 📋 Contrato de Salida Requerido (JSON Schema Oficial)

El motor de CommunityLab entrega y persiste los datos cumpliendo estrictamente la especificación requerida:

```json
{
  "status": "exito",
  "resumen_comunidad": {
    "total_interacciones_procesadas": 2,
    "sentimiento_predominante": "Altamente Positivo",
    "temas_principales": ["Contratacion / Logros", "LangGraph / Nodos Condicionales"]
  },
  "activos_distribucion_generados": {
    "post_linkedin": {
      "titulo": "De la Comunidad al Mercado: El impacto de los proyectos practicos de IA",
      "copy": "Nada nos da mas orgullo que ver a nuestros talentos conquistando el mercado de tecnologia! 🚀\n\nNuestra estudiante Mariana Souza acaba de ser contratada como Desarrolladora Junior de IA tras destacar sus proyectos practicos desarrollados con LangChain y Oracle Cloud Infrastructure.\n\nHistorias como la de Mariana demuestran que construir soluciones reales es el mejor camino para impulsar la carrera tech. Felicitaciones, Mariana! 👏\n\n#TalentosTech #InteligenciaArtificial #OracleCloud #CarreraDev",
      "canal_recomendado": "LinkedIn Oficial",
      "potencial_engagement": "Alto"
    },
    "destaque_newsletter_semanal": {
      "seccion": "Logro de la Semana",
      "titular": "Estudiante consigue empleo dev con portfolio de IA en Oracle Cloud",
      "resumen": "Mariana Souza obtuvo su primera oportunidad como Dev Jr de IA destacando proyectos desarrollados durante la formacion."
    },
    "sugerencia_contenido_faq": {
      "tema": "Tip Rapido: Como crear nodos de reintento en LangGraph",
      "origen": "Duda frecuente planteada por Lucas Albuquerque en el canal de soporte",
      "status": "derivado_a_mentoria"
    }
  },
  "almacenamiento_oci": {
    "bucket": "communitylab-activos-marketing",
    "ruta_objeto": "activos/2026-semana-04/paquete-distribucion.json",
    "status": "guardado_con_exito"
  }
}
```

---

## 🗂️ Datasets y Casos de Estudio Incluidos (`data/samples/`)

Para facilitar la evaluación técnica y la demostración en vivo a un solo clic, se incluyeron conjuntos de datos representativos con lenguaje natural y situaciones verosímiles de la comunidad tech:

| Archivo | Origen | Mensajes | Foco Temático / Escenario |
|---|---|:---:|---|
| `ejemplo_oficial_pdf_one_g10.json` | Discord ONE G10 | 4 | **Demostración Canónica Oficial del PDF** (Mariana Souza y Lucas Albuquerque) |
| `ejemplo_1_contratacion.json` | Campus ONE | 12 | Testimonios de inserción laboral en Cloud & IA antes de defender tesis |
| `ejemplo_2_soporte_dudas.json` | Foros Académicos | 12 | Soporte de Cátedra Cloud OCI Always Free, llaves RSA PEM y variables |
| `ejemplo_3_feedback_mixto.json` | Tutorías Pares | 14 | Alertas de sobrecarga académica, retención estudiantil y red de apoyo |
| `ejemplo_4_innovacion_hackathon.json` | Feria de Innovación | 12 | Pitches de proyectos finales desplegados en OCI y pre-incubación |
| `ejemplo_5_discord_comunidad_one.json` | Servidor Discord | 14 | Conversaciones reales de Discord: contrataciones en Globant/MeLi y dudas de SDK |
| `ejemplo_6_slack_alumni_tech.json` | Slack Alumni Network | 6 | Red de graduados en la industria: Tech Leads, buenas prácticas OCI y mentorías |
| `ejemplo_7_github_discussions_soporte.json` | GitHub Discussions | 6 | Troubleshooting técnico: buffers en memoria vs persistencia OCI, Structured Outputs |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Justificación y Rol en la Solución |
|---|---|---|
| **Frontend / UI** | `Streamlit 1.35+` + `Lucide Icons` | Interfaz web interactiva, responsiva y táctil con diseño SaaS y previsualización fotorrealista de LinkedIn. |
| **Modelos de IA** | `Google Gemini 2.5 Flash` / `OpenAI GPT-4o` | Inferencia de polaridad de sentimiento, extracción de temas y generación de copys persuasivos. |
| **Procesamiento de Datos** | `Python 3.11+` / `Pandas` | Normalización de payloads, agregación estadística y validación de esquemas JSON. |
| **Almacenamiento Cloud** | `Oracle Cloud Infrastructure (OCI) Object Storage` | Persistencia en bucket Always Free mediante `oci.object_storage.ObjectStorageClient`. |
| **Respaldo Local** | `Emulación de Bucket Espejo` | Permite la ejecución fluida en entornos sin credenciales OCI configuradas sin interrumpir la demo. |
| **Control de Versiones** | `Git` / `GitHub` | Trabajo colaborativo del Equipo 47 ONE LATAM. |
| **Despliegue** | `Streamlit Cloud` | Alojamiento en la nube conectado a la rama `main` del repositorio oficial. |

---

## ⚙️ Cómo Ejecutar el Proyecto Localmente

### 1. Clonar el repositorio
```bash
git clone https://github.com/No-Country-simulation/G10-LATAM-CommunityLab-equipo47.git
cd G10-LATAM-CommunityLab-equipo47
```

### 2. Crear y activar entorno virtual
```bash
# En Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# En Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

*(Opcional: Si vas a conectar credenciales reales de Oracle Cloud, instala el SDK oficial: `pip install oci`)*

### 4. Configurar secretos (Opcional)
Si deseas persistir en un bucket real de OCI o usar la API de Google Gemini en lugar del motor simulado, crea el archivo `.streamlit/secrets.toml`:

```toml
# Configuración opcional de Gemini
GEMINI_API_KEY = "tu-api-key-de-gemini"

# Configuración opcional de Oracle Cloud Infrastructure (Always Free)
[oci]
user = "ocid1.user.oc1..aaaaaaa..."
fingerprint = "20:3b:97:..."
tenancy = "ocid1.tenancy.oc1..aaaaaaa..."
region = "sa-saopaulo-1"
key_content = """-----BEGIN RSA PRIVATE KEY-----
... tu llave pem ...
-----END RSA PRIVATE KEY-----"""
namespace = "tu-namespace-oci"
bucket_name = "communitylab-activos-marketing"
```

> **Nota:** Si no se configuran credenciales, CommunityLab activa automáticamente su **motor de emulación local Always Free**, garantizando que el flujo de revisión y guardado funcione al 100% sin caídas.

### 5. Iniciar la aplicación
```bash
streamlit run app.py
```
Abre en tu navegador: `http://localhost:8501` e inicia sesión con `admin` / `admin`.

---

## ✅ Checklist de Evaluación del Hackathon

- [x] **Ingestión funcional de interacciones:** Soporta carga de archivos JSON, CSV o selección de datasets prediseñados a un clic.
- [x] **Análisis de sentimiento y extracción de temas con LLM:** Diagnóstico de polaridad y categorización temática automática.
- [x] **Generación de al menos 2 formatos de marketing:** Genera 3 formatos simultáneos (Post LinkedIn, Newsletter y FAQ/Tips).
- [x] **Orquestación de flujo con router condicional:** Bifurca hacia LinkedIn si detecta logros/empleo, hacia Newsletter para resumen de actividad, y hacia FAQ/Tips para dudas técnicas.
- [x] **Integración con OCI Object Storage (Always Free):** Persistencia autenticada con SDK oficial y fallback local compatible.
- [x] **Mínimo 3 ejemplos de demostración:** 7 datasets completos disponibles en `data/samples/`, incluyendo el caso oficial del PDF.
- [x] **Repositorio en GitHub con documentación y arquitectura:** README detallado, esquemas Mermaid y especificación técnica.

---

## 🌟 Diferenciales Implementados

- **Panel de Curaduría Humana (Human-in-the-Loop):** Edición en vivo mediante `st.text_area` antes de persistir, evitando alucinaciones o errores de tono.
- **Previsualización Fotorrealista de LinkedIn:** Maqueta interactiva visual que simula con precisión la publicación final en redes.
- **Doble Modo OCI (Cloud SDK + Emulación Segura):** Resiliencia garantizada para evaluadores sin cuenta de nube activa.
- **Alertas Tempranas de Retención:** Algoritmo que detecta signos de sobrecarga académica o deserción para alertar a tutores pares.
- **Despliegue Continuo en Streamlit Cloud:** Aplicación pública en vivo con SSL y alta disponibilidad.

---

## 👥 Equipo — G10 Equipo 47 (ONE LATAM)

Desarrollado con dedicación para el **Hackathon ONE (Oracle Next Education & Alura)** en simulación con **No Country**.

| Nombre | Rol | Especialidad |
|---|---|---|
| **Equipo 47** | Team Leader & Backend | Arquitectura del pipeline, FastAPI/Python y despliegue |
| **Equipo 47** | IA & Prompt Engineering | Orquestación LLM, Router condicional y Structured Outputs |
| **Equipo 47** | Frontend & UX/UI | Streamlit, maquetación fotorrealista y componentes Lucide |
| **Equipo 47** | Cloud & OCI | Integración Object Storage Always Free y políticas IAM |

---

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más información.
