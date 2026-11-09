"""Consulta de diagnóstico sin mostrar URLs ni credenciales."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import ConfigurationError, Settings


def main():
    settings = Settings()
    settings.validate_runtime()
    for url in (settings.resolved_database_url(), settings.resolved_test_database_url()):
        engine = create_engine(url, hide_parameters=True)
        try:
            with engine.connect() as connection:
                print(dict(connection.execute(text(
                    "SELECT current_database() AS base, current_user AS usuario, "
                    "current_setting('server_version') AS version"
                )).mappings().one()))
                print(dict(connection.execute(text(
                    "SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname=current_user"
                )).mappings().one()))
                print("Tablas:", inspect(connection).get_table_names(schema="public"))
        except SQLAlchemyError:
            raise SystemExit("No se pudo consultar la base del proyecto; revisá conexión y credenciales.") from None
        finally:
            engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except ConfigurationError as error:
        raise SystemExit(str(error)) from None
