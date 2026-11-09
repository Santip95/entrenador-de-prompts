from app.db.seed import seed_initial_data
from app.core.config import Settings
from sqlalchemy import create_engine


def main() -> None:
    engine = create_engine(Settings().resolved_migration_url())
    with engine.begin() as connection:
        counts = seed_initial_data(connection)
    print(
        "Precarga completada: "
        f"criterios={counts.criterios}, reglas={counts.reglas}, "
        f"desafios={counts.desafios}, desafio_criterios={counts.desafio_criterios}."
    )


if __name__ == "__main__":
    main()
