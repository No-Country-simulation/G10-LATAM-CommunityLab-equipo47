# Esquema de `paquete-distribucion.json`

Base: el ejemplo de salida de la consigna (`proyecto_hackaton.pdf`). Los campos marcados
**(propuesta)** los añadió el equipo y no están en la consigna: revísalos antes de fijarlos.
Ejemplo completo: `docs/ejemplo-paquete-distribucion.json` (construido con
`data/entrada/ejemplo_1_contratacion.json`; el texto de los activos es ilustrativo).

## Entrada (lote)
Igual que la consigna: `origen_comunidad`, `periodo_referencia`, `interacciones[]` con
`autor`, `canal`, `tipo`, `texto`. Los ejemplos añaden `pais` (opcional). Tipos vistos:
`testimonio`, `pregunta_tecnica`, `agradecimiento`, `sugerencia`, `alerta_apoyo`, `recurso`.

## Salida

| Campo | Obligatorio | Origen | Notas |
|---|---|---|---|
| `status` | sí | consigna | `"exito"` o `"error"` |
| `mensaje_error` | solo si hay error | propuesta | texto claro, sin claves ni rutas de `.pem` |
| `resumen_comunidad.origen_comunidad` | sí | propuesta | copia de la entrada |
| `resumen_comunidad.periodo_referencia` | sí | propuesta | copia de la entrada |
| `resumen_comunidad.total_interacciones_procesadas` | sí | consigna | entero |
| `resumen_comunidad.sentimiento_predominante` | sí | consigna | p. ej. `Altamente Positivo`, `Positivo`, `Mixto`, `Negativo` |
| `resumen_comunidad.temas_principales` | sí | consigna | lista de textos cortos |
| `analisis_interacciones[]` | sí | propuesta | una entrada por interacción (ver abajo) |
| `activos_distribucion_generados.post_linkedin` | sí (MVP) | consigna | `titulo`, `copy`, `canal_recomendado`, `potencial_engagement` |
| `activos_distribucion_generados.sugerencia_contenido_faq` | sí (MVP) | consigna + propuesta | `tema`, `origen`, `status` (consigna) + `pregunta`, `respuesta_sugerida` (propuesta) |
| `activos_distribucion_generados.destaque_newsletter_semanal` | no | consigna | `seccion`, `titular`, `resumen`; formato extra opcional |
| `<activo>.estado_aprobacion` | sí | propuesta | `pendiente`, `aprobado` o `rechazado`; lo cambia la interfaz Streamlit |
| `almacenamiento_oci.bucket` | sí | consigna | |
| `almacenamiento_oci.ruta_objeto` | sí | consigna | `activos/AAAA-semana-NN/paquete-distribucion.json` |
| `almacenamiento_oci.status` | sí | consigna | `guardado_con_exito` o `error_al_guardar` |

### `analisis_interacciones[]` (propuesta)
- `autor`, `canal`, `tipo`: copia de la entrada.
- `sentimiento`: `muy_positivo`, `positivo`, `neutro`, `negativo`.
- `temas`: lista de textos cortos.
- `puntuacion_relevancia`: entero de 0 a 100.
- `motivo_puntuacion`: una frase que explica la puntuación.
- `ruta`: decisión del router: `post_linkedin`, `faq`, `apoyo` o `sin_activo`.

## Puntos que conviene revisar
1. **Estado de OCI dentro del propio archivo.** El paquete se guarda en OCI con
   `almacenamiento_oci` ya incluido, pero el resultado de la subida solo se conoce después.
   Propuesta: el archivo guardado lleva `bucket` y `ruta_objeto`, y la respuesta que devuelve
   la acción (y la interfaz) lleva el `status` final.
2. **Caso de éxito.** En el ejemplo de la consigna, un testimonio muy positivo produce
   `post_linkedin`. En el MVP el "caso de éxito" se materializa como ese post; un
   `caso_exito` más largo queda como mejora.
3. **Ruta `apoyo`.** `ejemplo_3` incluye una `alerta_apoyo`. El MVP solo la marca en
   `analisis_interacciones`; generar un activo para ella es un diferencial.
4. **Semana en el nombre del objeto.** Ver `AGENTS.md` (sección OCI).
