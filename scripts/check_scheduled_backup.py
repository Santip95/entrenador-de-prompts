"""Verificar la copia referida por el trabajo, sin restaurar ni imprimir datos."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.core.config import Settings
from app.operations.backups import AGE, CLIENT, directory, pipeline, verify_manifest


def main():
    try:
        settings = Settings()
        root = directory(settings)
        status = json.loads((root / 'estado-tarea.json').read_text(encoding='utf-8'))
        if status.get('aprobado') is not True:
            raise ValueError('Trabajo no aprobado')
        name = status['manifiesto']
        if Path(name).name != name:
            raise ValueError('Ruta inválida')
        info, archive = verify_manifest(settings, root / name)
        if info['origen'] != 'entrenador_prompts':
            raise ValueError('Origen incorrecto')
        pipeline([str(AGE), '-d', '-i', settings.backup_identity_file, str(archive)],
                 [str(CLIENT / 'pg_restore.exe'), '--file=' + os.devnull])
        # Detectar reemplazo del estado mientras se verificaba la copia.
        if json.loads((root / 'estado-tarea.json').read_text(encoding='utf-8')) != status:
            raise ValueError('El trabajo cambió; repetir comprobación')
        report = {'verificacion_utc': datetime.now(timezone.utc).isoformat(),
                  'trabajo_utc': status['fecha_utc'], 'manifiesto': name,
                  'copia_utc': info['fecha_utc'], 'bytes': info['bytes'],
                  'schema': info['schema_version'], 'autenticidad_sha256': True,
                  'descifrado_completo_pg_restore': True, 'restauracion_ejecutada': False,
                  'b2_verificado': status.get('b2_verificado', False),
                  'retencion': status.get('retencion'),
                  'limite': 'No acredita disparador, sesión cerrada ni restauración SQL de esta copia.'}
        target = ROOT / 'local-data/etapa06'
        target.mkdir(parents=True, exist_ok=True)
        path = target / ('respaldo-verificado-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception:
        print('No se verificó la copia. Revisar permisos/configuración/estado sin divulgar secretos.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
