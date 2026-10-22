"""
Modulo de almacenamiento y auditoria para OCI Object Storage (Capa Always Free).
Soporta persistencia real mediante el SDK oci de Oracle Cloud (usando ~/.oci/config, st.secrets o variables de entorno)
y emulacion local transparente para pruebas de desarrollo sin interrumpir el flujo del evaluador.
Conforme al documento oficial: Hackathon ONE G10 - Oracle Next Education & Alura.
"""
import os
import json
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

LOCAL_OCI_STORAGE_DIR = Path("oci_bucket_simulation")

def _obtener_config_entorno():
    """Lee las variables de configuracion de OCI desde el entorno o st.secrets."""
    oci_secrets = None
    if hasattr(st, "secrets") and "oci" in st.secrets:
        oci_secrets = st.secrets["oci"]
    
    config_file = (oci_secrets.get("config_file") if oci_secrets else None) or os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
    profile = (oci_secrets.get("config_profile") if oci_secrets else None) or os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
    region = (oci_secrets.get("region") if oci_secrets else None) or os.getenv("OCI_REGION", "sa-santiago-1")
    namespace = (oci_secrets.get("namespace") if oci_secrets else None) or os.getenv("OCI_NAMESPACE", "axsui3upub83")
    bucket = (oci_secrets.get("bucket") if oci_secrets else None) or os.getenv("OCI_BUCKET", "communitylab-activos-marketing")
    
    return {
        "config_file": config_file,
        "profile": profile,
        "region": region,
        "namespace": namespace,
        "bucket": bucket,
        "secrets": oci_secrets
    }

def verificar_estado_conexion_oci():
    """
    Verifica el estado detallado de conexion con Oracle Cloud.
    Devuelve un diccionario con el diagnostico para que el usuario comun entienda el estado.
    """
    cfg = _obtener_config_entorno()
    ruta_cfg = Path(cfg["config_file"]).expanduser() if cfg.get("config_file") else None
    
    sdk_instalado = False
    try:
        import oci
        sdk_instalado = True
    except ImportError:
        pass

    tiene_archivo_config = ruta_cfg.exists() if ruta_cfg else False
    cliente, ns, bucket, region, err = _obtener_cliente_oci_real()
    
    conectado_a_nube = cliente is not None
    
    if conectado_a_nube:
        mensaje = f"Conectado exitosamente a Oracle Cloud (Namespace: {ns}, Bucket: {bucket}, Región: {region})"
        tipo = "nube_real"
    elif not tiene_archivo_config and not (cfg.get("secrets") and (cfg["secrets"].get("key_content") or cfg["secrets"].get("key_file"))):
        mensaje = f"Modo Espejo Local Activo: No se encontraron credenciales OCI configuradas. Los archivos se guardan localmente y NO en el namespace '{ns}' de Oracle Cloud."
        tipo = "falta_config"
    elif not sdk_instalado:
        mensaje = "Modo Espejo Local Activo: SDK 'oci' no disponible."
        tipo = "falta_sdk"
    else:
        mensaje = f"Modo Espejo Local Activo: Error al autenticar con OCI ({err}). Guardando en respaldo local."
        tipo = "error_auth"

    return {
        "conectado_a_nube": conectado_a_nube,
        "tipo": tipo,
        "mensaje": mensaje,
        "sdk_instalado": sdk_instalado,
        "tiene_archivo_config": tiene_archivo_config,
        "ruta_config_esperada": str(ruta_cfg) if ruta_cfg else "st.secrets['oci']",
        "namespace": ns or cfg["namespace"],
        "bucket": bucket or cfg["bucket"],
        "region": region or cfg["region"],
        "error_detalle": err
    }

def _obtener_cliente_oci_real():
    """
    Intenta instanciar un cliente real de OCI Object Storage a partir de:
    1. Archivo ~/.oci/config (perfil DEFAULT) o carpeta oci/.oci/config en el proyecto
    2. st.secrets o variables de entorno directas.
    Retorna (client, namespace, bucket, region, error_msg).
    """
    cfg = _obtener_config_entorno()
    namespace = cfg["namespace"]
    bucket = cfg["bucket"]
    region = cfg["region"]

    try:
        import oci
        
        # 1. Intentar PRIMERO desde st.secrets o variables de entorno directas (Prioridad en la nube)
        oci_secrets = cfg["secrets"]
        user = (oci_secrets.get("user") if oci_secrets else None) or os.getenv("OCI_USER")
        fingerprint = (oci_secrets.get("fingerprint") if oci_secrets else None) or os.getenv("OCI_FINGERPRINT")
        tenancy = (oci_secrets.get("tenancy") if oci_secrets else None) or os.getenv("OCI_TENANCY")
        key_content = (oci_secrets.get("key_content") if oci_secrets else None) or os.getenv("OCI_KEY_CONTENT")
        key_file = (oci_secrets.get("key_file") if oci_secrets else None) or os.getenv("OCI_KEY_FILE")

        if user and fingerprint and tenancy and (key_content or key_file):
            try:
                config = {
                    "user": user.strip(),
                    "fingerprint": fingerprint.strip(),
                    "tenancy": tenancy.strip(),
                    "region": region.strip(),
                }
                if key_content:
                    config["key_content"] = key_content.strip()
                elif key_file:
                    config["key_file"] = key_file.strip()

                oci.config.validate_config(config)
                client = oci.object_storage.ObjectStorageClient(config)
                
                try:
                    ns_real = client.get_namespace().data
                    if ns_real:
                        namespace = ns_real
                except Exception:
                    pass

                return client, namespace, bucket, region, None
            except Exception as e:
                return None, namespace, bucket, region, f"Error autenticando con st.secrets: {str(e)}"

        # 2. Intentar desde archivos de configuración disponibles (~/.oci/config o proyecto)
        rutas_a_probar = []
        if cfg.get("config_file"):
            rutas_a_probar.append(Path(cfg["config_file"]).expanduser())
            
        # Carpeta local del proyecto oci/.oci/config
        ruta_proyecto = Path(__file__).resolve().parent.parent / "oci" / ".oci" / "config"
        if ruta_proyecto not in rutas_a_probar:
            rutas_a_probar.append(ruta_proyecto)
            
        ruta_home = Path.home() / ".oci" / "config"
        if ruta_home not in rutas_a_probar:
            rutas_a_probar.append(ruta_home)

        ultimo_error = None
        for ruta_cfg in rutas_a_probar:
            if not ruta_cfg or not ruta_cfg.exists():
                continue
            try:
                datos_config = oci.config.from_file(
                    file_location=str(ruta_cfg),
                    profile_name=cfg["profile"]
                )
                
                # Auto-recuperación de ruta de key_file si cambió de máquina o usuario
                kf = Path(datos_config.get("key_file", "")).expanduser()
                if not kf.exists():
                    candidato_dir = ruta_cfg.parent / "oci_api_key.pem"
                    candidato_home = Path.home() / ".oci" / "oci_api_key.pem"
                    if candidato_dir.exists():
                        datos_config["key_file"] = str(candidato_dir)
                    elif candidato_home.exists():
                        datos_config["key_file"] = str(candidato_home)

                if region:
                    datos_config["region"] = region
                    
                client = oci.object_storage.ObjectStorageClient(datos_config)
                
                try:
                    ns_real = client.get_namespace().data
                    if ns_real:
                        namespace = ns_real
                except Exception:
                    pass

                return client, namespace, bucket, datos_config.get("region", region), None
            except Exception as e:
                ultimo_error = f"Error leyendo {ruta_cfg}: {str(e)}"

        return None, namespace, bucket, region, ultimo_error or "No se encontraron credenciales OCI válidas"

    except ImportError:
        return None, namespace, bucket, region, "El SDK de Python 'oci' no esta instalado"
    except Exception as exc:
        return None, namespace, bucket, region, str(exc)

def guardar_configuracion_oci_local(user_ocid: str, tenancy_ocid: str, fingerprint: str, region: str, key_content: str) -> tuple[bool, str]:
    """
    Guarda las credenciales de Oracle Cloud en ~/.oci/config y ~/.oci/oci_api_key.pem.
    Permite al usuario activar la conexion real a Oracle Cloud desde la propia interfaz web.
    """
    try:
        dir_oci = Path.home() / ".oci"
        dir_oci.mkdir(parents=True, exist_ok=True)
        
        pem_path = dir_oci / "oci_api_key.pem"
        with open(pem_path, "w", encoding="utf-8") as f:
            f.write(key_content.strip() + "\n")
            
        config_path = dir_oci / "config"
        contenido_config = f"""[DEFAULT]
user={user_ocid.strip()}
fingerprint={fingerprint.strip()}
tenancy={tenancy_ocid.strip()}
region={region.strip()}
key_file={str(pem_path).replace("\\", "/")}
"""
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(contenido_config)
            
        return True, f"Credenciales guardadas exitosamente en {config_path}"
    except Exception as e:
        return False, f"Error al guardar credenciales: {str(e)}"

def guardar_en_oci(paquete: dict, bucket_name: str = None, ruta_objeto: str = None) -> dict:
    """
    Persiste el paquete estructurado de activos en OCI Object Storage.
    Si se detecta conexion OCI activa a la nube de Oracle, sube el objeto al Bucket real.
    En caso contrario, persiste en el espejo local estructurado como respaldo.
    """
    cfg = _obtener_config_entorno()
    if not bucket_name:
        bucket_name = cfg["bucket"]
        
    if not ruta_objeto:
        ruta_objeto = paquete.get("almacenamiento_oci", {}).get("ruta_objeto", "activos/2026-semana-04/paquete-distribucion.json")

    json_str = json.dumps(paquete, indent=2, ensure_ascii=False)
    
    # Intentar conexion real a OCI
    client, namespace, _, region, error_cfg = _obtener_cliente_oci_real()
    subido_a_nube = False
    error_nube = None

    if client and namespace:
        try:
            client.put_object(
                namespace_name=namespace,
                bucket_name=bucket_name,
                object_name=ruta_objeto,
                put_object_body=json_str.encode("utf-8"),
                content_type="application/json"
            )
            subido_a_nube = True
        except Exception as e:
            error_nube = str(e)

    # Persistencia espejo local para garantizar que siempre haya registro visible y descargable
    destino_local = LOCAL_OCI_STORAGE_DIR / bucket_name / ruta_objeto
    destino_local.parent.mkdir(parents=True, exist_ok=True)
    with open(destino_local, "w", encoding="utf-8") as f:
        f.write(json_str)

    if subido_a_nube:
        modo = "Nube_Oracle_Cloud_Real (Cloud SDK)"
        estado_desc = f"Persistido en Nube Oracle Cloud (Namespace: {namespace})"
    elif error_nube:
        modo = "Espejo_Local (Fallback por error de nube)"
        estado_desc = f"Guardado localmente en PC. Error en nube: {error_nube}"
    else:
        modo = "Espejo_Local (Offline / Sin credenciales OCI)"
        estado_desc = f"Guardado en PC (Falta ~/.oci/config para subir al namespace {namespace})"

    return {
        "bucket": bucket_name,
        "namespace": namespace or cfg["namespace"],
        "region": region or cfg["region"],
        "ruta_objeto": ruta_objeto,
        "status": "guardado_con_exito",
        "modo": modo,
        "nube_real": subido_a_nube,
        "estado_descripcion": estado_desc,
        "ruta_local_espejo": str(destino_local).replace("\\", "/"),
        "error_nube": error_nube or error_cfg
    }

def listar_activos_oci(bucket_name: str = None) -> list:
    """Devuelve la lista de archivos guardados en el bucket (nube u espejo local)."""
    cfg = _obtener_config_entorno()
    if not bucket_name:
        bucket_name = cfg["bucket"]
        
    archivos = []
    
    # 1. Intentar listar desde OCI real si hay cliente
    client, namespace, _, _, _ = _obtener_cliente_oci_real()
    if client and namespace:
        try:
            res = client.list_objects(
                namespace_name=namespace,
                bucket_name=bucket_name,
                fields="name,size,timeModified,timeCreated"
            )
            for obj in res.data.objects:
                archivos.append({
                    "nombre": obj.name.split("/")[-1],
                    "ruta_objeto": obj.name,
                    "tamano_bytes": obj.size or 0,
                    "origen": f"Nube Oracle Cloud ({namespace})",
                    "nube_real": True,
                    "fecha_modificacion": str(obj.time_modified) if hasattr(obj, "time_modified") and obj.time_modified else "Cloud OCI"
                })
            if archivos:
                return archivos
        except Exception:
            pass

    # 2. Listar desde el almacenamiento espejo local
    bucket_path = LOCAL_OCI_STORAGE_DIR / bucket_name
    if not bucket_path.exists():
        return []

    for root, _, files in os.walk(bucket_path):
        for file in files:
            if file.endswith(".json"):
                full_p = Path(root) / file
                rel_p = full_p.relative_to(bucket_path)
                archivos.append({
                    "nombre": file,
                    "ruta_objeto": str(rel_p).replace("\\", "/"),
                    "tamano_bytes": full_p.stat().st_size,
                    "origen": "Espejo Local (PC)",
                    "nube_real": False,
                    "fecha_modificacion": full_p.stat().st_mtime
                })
    return archivos

def obtener_contenido_objeto_oci(ruta_objeto: str, bucket_name: str = None) -> dict:
    """
    Obtiene el contenido JSON de un objeto guardado en el bucket.
    Primero busca en la simulación local; si no existe y hay conexión con la nube,
    descarga el objeto desde OCI y lo sincroniza en el espejo local.
    """
    cfg = _obtener_config_entorno()
    if not bucket_name:
        bucket_name = cfg["bucket"]
        
    ruta_local = LOCAL_OCI_STORAGE_DIR / bucket_name / ruta_objeto
    if ruta_local.exists():
        try:
            with open(ruta_local, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    # Intentar descargar de la nube real
    client, namespace, _, _, _ = _obtener_cliente_oci_real()
    if client and namespace:
        try:
            res_obj = client.get_object(namespace_name=namespace, bucket_name=bucket_name, object_name=ruta_objeto)
            contenido = json.loads(res_obj.data.content.decode("utf-8"))
            try:
                ruta_local.parent.mkdir(parents=True, exist_ok=True)
                with open(ruta_local, "w", encoding="utf-8") as f:
                    json.dump(contenido, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
            return contenido
        except Exception:
            pass
            
    return {}

def consultar_tabla_auditoria_oci(bucket_name: str = None) -> list:
    """
    Consulta detallada de auditoria sobre los paquetes guardados en OCI.
    Retorna una lista de registros planos para mostrar directamente en una tabla Streamlit.
    """
    cfg = _obtener_config_entorno()
    if not bucket_name:
        bucket_name = cfg["bucket"]
        
    objetos = listar_activos_oci(bucket_name)
    registros = []
    
    for obj in objetos:
        ruta_obj = obj.get("ruta_objeto", "")
        nombre = obj.get("nombre", "")
        tamano_kb = round(obj.get("tamano_bytes", 0) / 1024, 2)
        origen_almacenamiento = obj.get("origen", "Espejo Local (PC)")
        es_nube = obj.get("nube_real", False)
        
        # Leer el contenido para extraer metadatos de auditoria
        contenido_dict = obtener_contenido_objeto_oci(ruta_obj, bucket_name)
                
        resumen = contenido_dict.get("resumen_comunidad", {})
        activos = contenido_dict.get("activos_distribucion_generados", {})
        post_lk = activos.get("post_linkedin", {})
        newsletter = activos.get("destaque_newsletter_semanal", {})
        faq = activos.get("sugerencia_contenido_faq", {})
        
        # Manejo de metadatos según sea un paquete generado o un lote de entrada
        if "resumen_comunidad" in contenido_dict or "activos_distribucion_generados" in contenido_dict:
            sentimiento = resumen.get("sentimiento_predominante", "N/A")
            temas = ", ".join(resumen.get("temas_principales", [])) or "N/A"
            titulo_lk = post_lk.get("titulo", "N/A")
            titular_news = newsletter.get("titular", "N/A")
            tema_faq = faq.get("tema", "N/A")
        elif "interacciones" in contenido_dict:
            sentimiento = "Lote de Entrada"
            total_msgs = len(contenido_dict.get("interacciones", []))
            temas = f"{total_msgs} mensajes comunitarios"
            titulo_lk = "(Archivo de Ingestión)"
            titular_news = "N/A"
            tema_faq = "N/A"
        else:
            sentimiento = "Archivo JSON"
            temas = "N/A"
            titulo_lk = "N/A"
            titular_news = "N/A"
            tema_faq = "N/A"
        
        # Extraer fecha o semana desde la ruta
        partes = ruta_obj.split("/")
        fecha_lote = partes[1] if len(partes) > 1 else "N/A"
        
        registros.append({
            "Archivo": nombre,
            "Ruta en OCI Bucket": ruta_obj,
            "Ubicación": "☁️ Nube OCI" if es_nube else "💾 Espejo Local",
            "Namespace OCI": cfg["namespace"],
            "Fecha / Periodo": fecha_lote,
            "Tamaño (KB)": tamano_kb,
            "Sentimiento Detectado": sentimiento[:35] + ("..." if len(sentimiento) > 35 else ""),
            "Temas Principales": temas[:40] + ("..." if len(temas) > 40 else ""),
            "Título Post LinkedIn": titulo_lk[:45] + ("..." if len(titulo_lk) > 45 else ""),
            "Titular Newsletter": titular_news[:40] + ("..." if len(titular_news) > 40 else ""),
            "Tema FAQ / Tip": tema_faq[:35] + ("..." if len(tema_faq) > 35 else ""),
            "_contenido_completo": contenido_dict
        })
        
    return registros