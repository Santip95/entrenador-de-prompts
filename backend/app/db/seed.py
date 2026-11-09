from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import MetaData, Table, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection


ROOT_DIR = Path(__file__).resolve().parents[3]
SEEDS_DIR = ROOT_DIR / "seeds"
SEED_NAMESPACE = uuid.UUID("47ad2e07-204e-4d91-a3fe-dab20f6c4746")


@dataclass(frozen=True)
class SeedCounts:
    criterios: int
    reglas: int
    desafios: int
    desafio_criterios: int


def _load_seed(name: str) -> dict:
    with (SEEDS_DIR / name).open(encoding="utf-8") as source:
        return json.load(source)


def _id(kind: str, code: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NAMESPACE, f"{kind}:{code}")


def seed_initial_data(connection: Connection) -> SeedCounts:
    """Inserta la precarga sin modificar filas existentes ni duplicarlas."""
    metadata = MetaData()
    criterio = Table("criterio", metadata, autoload_with=connection)
    regla = Table("regla", metadata, autoload_with=connection)
    desafio = Table("desafio", metadata, autoload_with=connection)
    desafio_criterio = Table("desafio_criterio", metadata, autoload_with=connection)

    criteria_data = _load_seed("criteria.json")["criterios"]
    rules_data = _load_seed("rules.json")["reglas"]
    challenges_data = _load_seed("challenges.json")["desafios"]

    for item in criteria_data:
        connection.execute(
            insert(criterio)
            .values(
                id=_id("criterio", item["codigo"]),
                codigo=item["codigo"],
                nombre=item["nombre"],
                descripcion=item["descripcion"],
            )
            .on_conflict_do_nothing(index_elements=["codigo"])
        )

    for item in rules_data:
        criterion_id = connection.scalar(
            select(criterio.c.id).where(criterio.c.codigo == item["criterio_codigo"])
        )
        existing = connection.scalar(select(regla.c.id).where(
            regla.c.criterio_id == criterion_id, regla.c.version == item["version"]
        ))
        if existing is not None:
            continue
        connection.execute(
            insert(regla)
            .values(
                id=_id("regla", item["codigo"]),
                criterio_id=criterion_id,
                tipo=item["tipo"],
                parametros=item["parametros"],
                mensajes=item["mensajes"],
                version=item["version"],
                activa=item["activa"],
                creada_por=None,
            )
            .on_conflict_do_nothing(index_elements=["criterio_id", "version"])
        )

    for item in challenges_data:
        challenge_id = _id("desafio", item["codigo"])
        existing = connection.scalar(select(desafio.c.id).where(desafio.c.codigo == item["codigo"]))
        if existing is not None:
            continue
        connection.execute(
            insert(desafio)
            .values(
                id=challenge_id,
                codigo=item["codigo"],
                titulo=item["titulo"],
                consigna=item["consigna"],
                estado=item["estado"],
                activo=item["estado"] == "publicado",
                revision=item["revision"],
            )
            .on_conflict_do_nothing(index_elements=["codigo"])
        )
        for criterion_code, configuration in item["configuracion"].items():
            connection.execute(
                insert(desafio_criterio)
                .values(
                    desafio_id=challenge_id,
                    criterio_id=connection.scalar(
                        select(criterio.c.id).where(criterio.c.codigo == criterion_code)
                    ),
                    obligatorio=configuration["obligatorio"],
                    configuracion={
                        "aplica": configuration["aplica"],
                        "parametros": configuration["parametros"],
                    },
                )
                .on_conflict_do_nothing(index_elements=["desafio_id", "criterio_id"])
            )

    return SeedCounts(
        criterios=connection.scalar(select(func.count()).select_from(criterio)) or 0,
        reglas=connection.scalar(select(func.count()).select_from(regla)) or 0,
        desafios=connection.scalar(select(func.count()).select_from(desafio)) or 0,
        desafio_criterios=connection.scalar(
            select(func.count()).select_from(desafio_criterio)
        )
        or 0,
    )
