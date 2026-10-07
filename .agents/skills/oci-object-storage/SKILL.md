---
name: oci-object-storage
description: Úsala siempre que escribas, modifiques o revises código o comandos que lean o escriban en OCI Object Storage, o cuando uses el MCP de OCI en CommunityLab.
---

# OCI Object Storage en CommunityLab

La integración con OCI es requisito obligatorio de la consigna. Sigue esta guía siempre que la toques.

## Reglas
- La aplicación usa el SDK de Python (`oci`) con el perfil `DEFAULT` (clave de API). El MCP (perfil `communitylab`, token de sesión) es solo para el agente de desarrollo.
- Namespace, bucket, región y perfil salen de variables de entorno (`config.py`). Nunca los escribas fijos en el código.
- Convención de claves: `entradas/AAAA-semana-NN/`, `informes/AAAA-semana-NN/`, `activos/AAAA-semana-NN/`. Construye el nombre en una sola función reutilizable.
- Los objetos se suben como texto/JSON UTF-8 con el tipo de contenido correcto.
- Captura los errores del SDK (credenciales, permisos, red) y devuelve mensajes claros sin mostrar claves ni rutas de `.pem`.
- Solo Always Free: no crees buckets, políticas ni recursos nuevos sin preguntar. Límite gratuito: 20 GiB combinados con Archive (verifícalo en la documentación oficial si dudas).
- Antes de subir o sobrescribir un objeto, avisa al usuario. El MCP no puede borrar.
- Si el MCP falla con un error de autenticación, el token de sesión probablemente caducó: `oci session refresh --profile communitylab`.

## Checklist de revisión
- [ ] ¿Hay namespace, bucket u OCID escritos a mano?
- [ ] ¿Se lee algo de `~/.oci` o de un `.pem` en el código o en la salida?
- [ ] ¿Qué pasa si el bucket no existe o no hay permisos?
- [ ] ¿Qué pasa si el objeto ya existe (se sobrescribe)?
- [ ] ¿Los tests usan un simulacro y no la red?

## Al terminar
Indica qué puntos del checklist has comprobado y cómo.
