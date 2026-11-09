"""Activar una nueva C6 local con credencial de migración, nunca secretos en salida."""
import argparse
import json
from sqlalchemy import create_engine, text
from app.core.config import Settings
from app.application.numeric_detector import activate_numeric_detector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--entorno', choices=['desarrollo', 'pruebas'], required=True)
    args = parser.parse_args()
    settings = Settings()
    test = args.entorno == 'pruebas'
    expected = 'entrenador_prompts_test' if test else 'entrenador_prompts'
    engine = create_engine(settings.resolved_migration_url(test=test), hide_parameters=True)
    try:
        with engine.begin() as c:
            if c.scalar(text('SELECT current_database()')) != expected:
                raise ValueError('Destino incorrecto')
            if c.scalar(text('SELECT current_user')) != 'entrenador_migracion':
                raise ValueError('Usar el rol de migración separado')
            result = activate_numeric_detector(c, settings)
        print(json.dumps({'base': expected, **result, 'historicos_recalculados': False}))
    except Exception:
        raise SystemExit('Publicación no completada; transacción revertida. Revisar C6 activa, permisos y configuraciones específicas sin divulgar secretos.') from None
    finally:
        engine.dispose()


if __name__ == '__main__':
    main()
