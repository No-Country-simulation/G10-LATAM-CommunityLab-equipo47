# Integración UI y servicios

El lote activo vive en `raw_payload` y su nombre en `archivo_origen`.
Al cambiar el lote se eliminan resultados, borradores y confirmaciones anteriores.
Los reruns con el mismo archivo conservan las ediciones. Se aceptan JSON con
una lista `interacciones` y CSV con una columna `texto`. Cada texto debe ser
una cadena no vacía. Los campos de autor, país, canal y tipo tienen valores
por defecto. La carga inválida conserva el último lote válido.

El pipeline guarda copias independientes en `generated_package` y
`curated_package`. Los callbacks editoriales conservan los cambios antes de
salir de la vista. Aprobar y Guardar reúne todos los campos y decisiones
actuales y llama a `modules.oci_client.guardar_en_oci`, usando el bucket y
la ruta del paquete. Los estados de rechazo/omisión elegidos por el curador
se conservan; guardar no publica en redes sociales.

El cliente usa OCI cuando hay SDK y credenciales disponibles; de lo contrario
usa almacenamiento local. La UI diferencia ambos resultados. La integración
cloud necesita credenciales y bucket existentes; no se validó contra una
cuenta OCI real.

## Contrato actual de salida

- `resumen_comunidad.total_interacciones_procesadas`: entero.
- `resumen_comunidad.sentimiento_predominante`: cadena.
- `resumen_comunidad.temas_principales`: lista de cadenas.
- `activos_distribucion_generados.post_linkedin`: titulo, copy y metadatos.
- `activos_distribucion_generados.destaque_newsletter_semanal`: seccion, titular, resumen.
- `activos_distribucion_generados.sugerencia_contenido_faq`: tema, origen, status.
- `almacenamiento_oci`: bucket, ruta_objeto.

## Dato a coordinar con Backend

El mock actual no calcula distribución de sentimiento. La UI admite el campo
opcional `resumen_comunidad.distribucion_sentimiento` como un objeto de conteos
(por ejemplo, `{"positivo": 8, "neutral": 3, "negativo": 1}`). Alternativamente,
puede contar `sentimiento` en cada interacción de entrada, indicando si sólo
hay clasificación parcial. Si no hay conteos, presenta un aviso y el sentimiento
predominante disponible, sin inferir polaridad a partir del tipo de mensaje.
Este campo opcional es una propuesta de integración, pendiente de confirmación.

El pipeline sigue usando `modules.mock_engine.process_community_payload`.
El selector de proveedor existente no conecta por sí solo a un LLM real.

## Verificación

`python -m unittest discover -s tests -v`

Las pruebas con Streamlit AppTest cubren cargar la demo, procesar, editar,
viajar entre vistas, guardar los textos revisados, preservar el original,
cambiar el lote y manejar un fallo del servicio sin confirmar éxito.
