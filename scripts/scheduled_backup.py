"""Trabajo del Programador de tareas. Sin terminal, sin contraseñas en argumentos."""
from pathlib import Path
import sys
import json
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.core.config import Settings
from app.operations.backups import backup,purge,directory
from app.operations.journal import atomic

def main():
    settings=Settings()
    status={'fecha_utc':datetime.now(timezone.utc).isoformat(),'aprobado':False,'b2_verificado':False}
    try:
        path=backup(settings,'entrenador_prompts')
        status['manifiesto']=path.name
        if settings.b2_enabled:
            from app.operations.b2 import B2Storage
            cloud=B2Storage(settings)
            try:
                status['carga_b2']=cloud.upload(path)
                status['purga_b2']=cloud.purge()
                status['b2_verificado']=True
            finally:cloud.close()
        status['retencion']=purge(settings)
        status['aprobado']=True
    except Exception:
        status['error']='No se completó el respaldo/verificación/purga. Revisar operación local sin divulgar secretos.'
    try: atomic(directory(settings)/'estado-tarea.json',json.dumps(status).encode())
    except Exception: return 1
    return 0 if status['aprobado'] else 1

if __name__=='__main__':raise SystemExit(main())
