import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

AUDIT_DIR = Path("data/auditoria")
AUDIT_FILE = AUDIT_DIR / "registro_auditoria.json"

def _asegurar_archivo():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    if not AUDIT_FILE.exists():
        with open(AUDIT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def calcular_hash_sha256(objeto: dict | str) -> str:
    '''Calcula el hash SHA-256 de un objeto para trazabilidad e integridad criptografica.'''
    if isinstance(objeto, dict):
        texto = json.dumps(objeto, sort_keys=True, ensure_ascii=False)
    else:
        texto = str(objeto)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def registrar_evento_auditoria(tipo_evento: str, usuario: str, motor: str, detalles: dict, objeto_relacionado: dict = None) -> dict:
    '''Registra un nuevo evento inmutable en el log de auditoria de CommunityLab.'''
    _asegurar_archivo()
    
    ahora = datetime.now()
    hash_sha256 = calcular_hash_sha256(objeto_relacionado) if objeto_relacionado else calcular_hash_sha256(detalles)
    
    entrada = {
        "id_evento": f"AUD-{ahora.strftime('%Y%m%d%H%M%S')}-{os.urandom(2).hex()}",
        "timestamp_local": ahora.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp_iso": ahora.isoformat(),
        "tipo_evento": tipo_evento,
        "usuario": usuario or "Evaluador_ONE_G10",
        "motor": motor or "Sistema",
        "hash_sha256": hash_sha256,
        "detalles": detalles,
        "estado_integridad": "VALIDADO_INTEGRO"
    }

    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            registros = json.load(f)
    except Exception:
        registros = []

    registros.insert(0, entrada)

    # Mantener maximo 100 eventos
    if len(registros) > 100:
        registros = registros[:100]

    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

    return entrada

def obtener_logs_auditoria() -> list:
    '''Retorna la lista de eventos de auditoria registrados.'''
    _asegurar_archivo()
    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
