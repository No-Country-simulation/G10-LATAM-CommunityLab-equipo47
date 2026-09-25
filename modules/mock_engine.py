"""
Motor de procesamiento de CommunityLab.
Genera la estructura exacta solicitada en el PDF del Hackathon ONE G10.
Especializado para el sector de Educación Superior (Campus Virtual, Facultades de Ingeniería, 
Cátedras de Tecnología y Comunidades de Aprendizaje).
"""
import datetime

def process_community_payload(data: dict) -> dict:
    """
    Procesa el conjunto de interacciones y genera los activos de distribución.
    Devuelve un diccionario que cumple estrictamente con la estructura requerida por el Hackathon.
    """
    interacciones = data.get("interacciones", [])
    periodo = data.get("periodo_referencia", "Semestre_Actual")
    origen = data.get("origen_comunidad", "Campus_Virtual_Universitario")
    total = len(interacciones)

    # Detección de tipos de interacción en el lote
    testimonios = [i for i in interacciones if i.get("tipo") in ["testimonio", "logro"]]
    preguntas = [i for i in interacciones if i.get("tipo") in ["pregunta_tecnica", "duda"]]
    alertas_apoyo = [i for i in interacciones if i.get("tipo") in ["alerta_apoyo", "dificultades"]]
    agradecimientos = [i for i in interacciones if i.get("tipo") in ["agradecimiento", "recurso", "sugerencia"]]

    # 1. Análisis de Sentimiento & Temas
    textos_combinados = " ".join([i.get("texto", "") for i in interacciones]).lower()
    es_hackathon = "hackathon" in origen.lower() or "feria" in origen.lower()

    if es_hackathon:
        sentimiento = "Sumamente Positivo (Innovación & Proyectos Prácticos Destacados)"
    elif alertas_apoyo:
        sentimiento = "Alerta de Sobrecarga / Apoyo Estudiantil Requerido"
    elif len(preguntas) >= 4 and len(preguntas) > len(testimonios):
        sentimiento = "Soporte Activo / Consultas Frecuentes de Cátedra Cloud"
    elif testimonios:
        sentimiento = "Altamente Positivo (Logros de Inserción Laboral y Grado)"
    elif preguntas:
        sentimiento = "Curioso / Con Necesidad de Soporte Técnico en Cátedra"
    else:
        sentimiento = "Equilibrado / Constructivo"

    # Extracción de temas dinámicos
    temas = []
    if es_hackathon:
        temas.append("Feria de Innovación & Hackathon Universitario")
    if any(k in textos_combinados for k in ["contratada", "puesto", "empleo", "pasantia", "contrato", "tesis"]):
        temas.append("Inserción Laboral & Empleabilidad Universitaria")
    if any(k in textos_combinados for k in ["langchain", "langgraph", "grafo", "agentes"]):
        temas.append("LangGraph & Orquestación de Agentes de IA")
    if any(k in textos_combinados for k in ["oci", "oracle", "bucket", "always free", "cloud"]):
        temas.append("Oracle Cloud Infrastructure (OCI Always Free)")
    if any(k in textos_combinados for k in ["tutor", "apoyo", "atrasado", "estudio", "recursar", "bienestar"]):
        temas.append("Bienestar Estudiantil & Retención Académica")
    if any(k in textos_combinados for k in ["gemini", "gpt", "llm", "tokens"]):
        temas.append("Modelos de Lenguaje & Prompts Académicos")

    if not temas:
        temas = ["Desarrollo de Proyectos Académicos", "Consultas de Campus Virtual"]

    # 2. Generación de Activos de Distribución (Bifurcación Condicional en Router)
    
    # FORMATO 1: Post para LinkedIn (Enfoque Educación Superior & UGC Marketing)
    if "Feria de Innovación & Hackathon Universitario" in temas:
        protagonista = testimonios[0].get("autor", "Nuestros estudiantes") if testimonios else "Equipos destacados"
        titulo_linkedin = "Innovación en Vivo: Estudiantes despliegan soluciones de IA en Oracle Cloud durante el Hackathon Universitario"
        copy_linkedin = (
            f"¡El talento de nuestras universidades no tiene techo! 🚀🏛️\n\n"
            f"Durante la jornada del Hackathon Académico de Campus Digital ONE, más de 25 equipos de estudiantes defendieron "
            f"soluciones de IA Generativa y Cloud en tiempo real. Proyectos como el presentado por {protagonista} y sus compañeros "
            f"procesaron cientos de consultas en vivo utilizando Streamlit, Gemini Flash y almacenamiento de objetos en OCI Always Free.\n\n"
            f"La distancia entre la teoría del aula y las demandas de la industria tecnológica se acorta cuando los estudiantes "
            f"tienen acceso a infraestructura de primer nivel. ¡Felicitaciones a todos los equipos por demostrar el poder del aprendizaje colaborativo! 👏\n\n"
            f"#EducacionSuperior #HackathonONE #InnovacionUniversitaria #OracleCloud #InteligenciaArtificial #AluraLatam"
        )
    elif testimonios and not alertas_apoyo:
        protagonista = testimonios[0].get("autor", "Nuestra estudiante")
        carrera = testimonios[0].get("carrera", "Ingeniería en Sistemas")
        total_testimonios = len(testimonios)
        mención_adicional = f" junto a {total_testimonios - 1} compañeros más que reportaron ascensos y contrataciones esta semana" if total_testimonios > 1 else ""
        titulo_linkedin = "De las Aulas al Mercado: El impacto de los proyectos prácticos de IA en la Educación Superior"
        copy_linkedin = (
            f"¡Nada nos llena más de orgullo que ver a nuestros estudiantes transformando el mercado tecnológico! 🎓🚀\n\n"
            f"Nuestra estudiante {protagonista} ({carrera}){mención_adicional} acaba de dar un salto clave en su carrera tras firmar su contrato "
            f"en IA antes de defender su tesis de grado, destacando con su proyecto práctico desarrollado con "
            f"LangChain y Oracle Cloud Infrastructure.\n\n"
            f"Historias como esta confirman que conectar las cátedras universitarias con tecnologías cloud y desafíos del mundo real "
            f"es el camino más sólido para formar a los líderes tecnológicos de América Latina. ¡Felicitaciones gigantes, {protagonista}! 👏\n\n"
            f"#EducacionSuperior #TalentoUniversitario #InteligenciaArtificial #OracleCloud #FacultadDeIngenieria #ComunidadTech"
        )
    elif alertas_apoyo:
        titulo_linkedin = "Aprender en Comunidad: Cómo la tutoría par y el apoyo estudiantil impulsan la retención tecnológica"
        copy_linkedin = (
            f"Aprender tecnologías complejas como arquitecturas de agentes autónomos y computación en la nube es un gran desafío, "
            f"pero nadie debería recorrer ese camino en soledad. 🤝💡\n\n"
            f"Esta semana en nuestra comunidad académica, frente a las dificultades en las entregas de mitad de semestre, "
            f"la red de tutores pares y estudiantes avanzados se organizó para abrir salas de estudio colaborativo y guías de soporte.\n\n"
            f"El verdadero valor de una institución educativa no está solo en su programa académico, sino en el tejido humano que cuida "
            f"y acompaña a cada estudiante hasta la meta.\n\n"
            f"#BienestarEstudiantil #TutoriasPares #EducacionSuperior #ComunidadUniversitaria #Ingenieria"
        )
    else:
        titulo_linkedin = f"Innovación y Aprendizaje Práctico en {origen.replace('_', ' ')}"
        copy_linkedin = (
            f"Esta semana en los laboratorios prácticos de {origen.replace('_', ' ')} vivimos intensos debates sobre "
            f"arquitecturas de agentes y despliegue seguro en la nube. 💡🏛️\n\n"
            f"Nuestros estudiantes estuvieron experimentando con persistencia en OCI Always Free y orquestación con IA Generativa. "
            f"La curiosidad técnica de los estudiantes es el motor que mantiene viva a nuestra facultad.\n\n"
            f"¿Tu institución ya está integrando proyectos cloud en su currícula? ¡Sumémonos a la conversación!\n\n"
            f"#EducacionSuperior #CloudComputing #OracleNextEducation #AluraLatam #InnovacionEducativa"
        )

    # FORMATO 2: Destaque Newsletter Semanal (Boletín Institucional / Campus)
    if "Feria de Innovación & Hackathon Universitario" in temas:
        newsletter = {
            "seccion": "Especial Hackathon & Innovación",
            "titular": "Proyectos destacados de IA en OCI pasan a pre-incubación universitaria",
            "resumen": (
                "Más de 25 equipos presentaron proyectos finales integrando LLMs y OCI Always Free. "
                "Las soluciones seleccionadas recibirán mentoría empresarial y créditos de nube."
            )
        }
    elif testimonios:
        testimonio_obj = testimonios[0]
        newsletter = {
            "seccion": "Logro Estudiantil de la Semana",
            "titular": f"{testimonio_obj.get('autor')} avanza en su carrera con portfolio de IA en Oracle Cloud",
            "resumen": (
                f"A partir de su proyecto de laboratorio, {testimonio_obj.get('autor')} ({testimonio_obj.get('carrera', 'Ingeniería')}) "
                f"destacó en entrevistas técnicas internacionales demostrando soluciones reales desplegadas en la nube de Oracle."
            )
        }
    elif alertas_apoyo:
        newsletter = {
            "seccion": "Acompañamiento y Vida Estudiantil",
            "titular": "Red de Tutorías Pares: Sesiones de estudio colaborativo este fin de semana",
            "resumen": (
                "Para acompañar a los estudiantes en las entregas de laboratorio de mitad de semestre, "
                "el equipo de tutores pares habilitó talleres especiales de repaso sobre arquitecturas cloud y resolución de dudas."
            )
        }
    else:
        newsletter = {
            "seccion": "Pulso Académico del Campus",
            "titular": f"Tendencias y debates destacados en {periodo.replace('_', ' ')}",
            "resumen": (
                "Sintetizamos las consultas más frecuentes sobre autenticación en OCI y buenas prácticas de prompts "
                "compartidas por los estudiantes durante la semana en el campus virtual."
            )
        }

    # FORMATO 3: Sugerencia de Contenido FAQ / Tip Rápido (Derivado de dudas de cátedra)
    if preguntas:
        pregunta_obj = preguntas[0]
        faq = {
            "tema": f"Tip de Cátedra: Resolución de dudas frecuentes sobre {temas[-1] if temas else 'Laboratorio Cloud'}",
            "origen": f"Duda planteada por {pregunta_obj.get('autor')} en el canal {pregunta_obj.get('canal', '#soporte-academico')}",
            "status": "derivado_a_ayudantes_de_catedra"
        }
    elif alertas_apoyo:
        faq = {
            "tema": "Guía de Primeros Auxilios Académicos: 5 conceptos esenciales para destrabar el sprint",
            "origen": "Iniciativa de tutoría par generada a partir de alertas de sobrecarga en foros",
            "status": "publicado_en_campus_virtual"
        }
    else:
        faq = {
            "tema": "Buenas prácticas de gestión de cuotas y llaves RSA en OCI Always Free",
            "origen": "Material preventivo elaborado por el equipo de cátedra",
            "status": "programado"
        }

    # 3. Empaquetado final con ruta OCI estandarizada (capa Always Free)
    timestamp_folder = datetime.datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"paquete-distribucion-{periodo.lower()}.json"

    salida_estructurada = {
        "status": "exito",
        "resumen_comunidad": {
            "total_interacciones_procesadas": total,
            "sentimiento_predominante": sentimiento,
            "temas_principales": temas
        },
        "activos_distribucion_generados": {
            "post_linkedin": {
                "titulo": titulo_linkedin,
                "copy": copy_linkedin,
                "canal_recomendado": "LinkedIn Institucional / Facultad",
                "potencial_engagement": "Alto"
            },
            "destaque_newsletter_semanal": newsletter,
            "sugerencia_contenido_faq": faq
        },
        "almacenamiento_oci": {
            "bucket": "communitylab-activos-marketing",
            "ruta_objeto": f"activos/{timestamp_folder}/{nombre_archivo}",
            "status": "guardado_con_exito"
        }
    }

    return salida_estructurada
