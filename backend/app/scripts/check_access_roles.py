"""Comprueba ambas conexiones sin modificar estructuras ni imprimir secretos."""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import ConfigurationError, Settings


def main():
    try:
        settings = Settings()
        for test in (False, True):
            urls = [("ejecucion", settings.resolved_test_database_url() if test else settings.resolved_database_url()),
                    ("migracion", settings.resolved_migration_url(test=test))]
            for kind, url in urls:
                engine = create_engine(url, hide_parameters=True)
                with engine.connect() as c:
                    row = c.execute(text("SELECT current_database() AS base,current_user AS rol,has_schema_privilege(current_user,'public','CREATE') AS ddl,has_database_privilege(current_user,current_database(),'TEMP') AS temporal,(SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tableowner=current_user) AS propias, (SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls FROM pg_roles WHERE rolname=current_user) AS elevado, EXISTS(SELECT FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=current_user)) AS membresia")).mappings().one()
                    valid = not row["elevado"] and (row["ddl"] if kind == "migracion" else not (row["ddl"] or row["temporal"] or row["propias"] or row["membresia"]))
                    print(f"{row['base']} | {kind} | {row['rol']} | DDL={row['ddl']} | tablas_propias={row['propias']} | correcto={valid}")
                    if not valid:
                        raise ConfigurationError("Permisos incompatibles con la separación requerida.")
                engine.dispose()
    except ConfigurationError as error:
        raise SystemExit(str(error)) from None
    except SQLAlchemyError:
        raise SystemExit("No se pudo comprobar la conexión; revisar credenciales locales.") from None


if __name__ == "__main__":
    main()
