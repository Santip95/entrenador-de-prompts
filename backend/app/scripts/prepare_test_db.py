"""Migra y precarga exclusivamente la base de pruebas; no borra tablas."""

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import ConfigurationError, ROOT_DIR, Settings
from app.db.seed import seed_initial_data


def main() -> None:
    try:
        settings = Settings()
        engine = create_engine(settings.resolved_migration_url(test=True))
        with engine.begin() as connection:
            if connection.scalar(text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")):
                raise ConfigurationError("Las pruebas requieren un rol sin superusuario.")
            config = Config(str(ROOT_DIR / "backend" / "alembic.ini"))
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
            print(seed_initial_data(connection))
        engine.dispose()
    except ConfigurationError as error:
        raise SystemExit(str(error)) from None
    except SQLAlchemyError:
        raise SystemExit("No se pudo preparar la base de pruebas. Revisá conexión y migraciones.") from None


if __name__ == "__main__":
    main()
