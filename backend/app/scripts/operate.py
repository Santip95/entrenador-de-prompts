"""CLI técnica. Nunca imprime conexión, contraseñas ni contenido de copias."""
import argparse
import json
from app.core.config import Settings,ConfigurationError
from app.operations.backups import backup,restore,purge,migrate_isolated
from app.operations.journal import JournalError

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['backup','restore','purge','preparar-pruebas','b2-upload','b2-purge'])
    parser.add_argument('--database',default='entrenador_prompts')
    parser.add_argument('--manifest')
    args=parser.parse_args()
    try:
        settings=Settings()
        if args.action=='backup': print('Copia cifrada verificada. Manifiesto:',backup(settings,args.database))
        elif args.action=='restore':
            if not args.manifest: raise ConfigurationError('Indicar --manifest.')
            print(json.dumps(restore(settings,args.manifest,args.database),ensure_ascii=True))
        elif args.action=='purge': print(json.dumps(purge(settings)))
        elif args.action=='preparar-pruebas': migrate_isolated(settings,args.database);print('Base de pruebas migrada y precargada.')
        else:
            from app.operations.b2 import B2Storage
            storage=B2Storage(settings)
            try:
                if args.action=='b2-upload':
                    if not args.manifest:raise ConfigurationError('Indicar --manifest.')
                    print(json.dumps(storage.upload(args.manifest)))
                else:print(json.dumps(storage.purge()))
            finally:storage.close()
    except (ConfigurationError,JournalError) as error:
        raise SystemExit(str(error)) from None
    except Exception:
        raise SystemExit('Operación no completada. Revisar configuración, permisos, diario y destino. No se muestra información privada ni se habilita acceso tras una restauración fallida.') from None

if __name__=='__main__': main()
