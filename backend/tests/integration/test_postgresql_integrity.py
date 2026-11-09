from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from app.core.config import ConfigurationError, Settings
from app.db.seed import seed_initial_data

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def connection():
    try:
        database_url = Settings().resolved_migration_url(test=True)
    except ConfigurationError as error:
        if str(error).startswith("Falta configurar"):
            pytest.skip("Configurá POSTGRES_PASSWORD o TEST_DATABASE_URL en .env.")
        pytest.fail(str(error))
    engine = create_engine(database_url, future=True)
    with engine.begin() as database_connection:
        assert database_connection.scalar(text("SELECT current_database()")) == "entrenador_prompts_test"
        assert not database_connection.scalar(text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user"))
        yield database_connection
    engine.dispose()


def test_seed_is_idempotent(connection) -> None:
    first = seed_initial_data(connection)
    second = seed_initial_data(connection)

    assert first.criterios == second.criterios == 6
    assert first.reglas == second.reglas == 6
    assert first.desafios == second.desafios == 4
    assert first.desafio_criterios == second.desafio_criterios == 24


def test_rejects_duplicate_criterion_code(connection) -> None:
    with pytest.raises(IntegrityError):
        with connection.begin_nested():
            connection.execute(
                text(
                    "INSERT INTO criterio (id, codigo, nombre, descripcion) "
                    "VALUES (:id, 'C1', 'Duplicado', 'No debe insertarse')"
                ),
                {"id": uuid.uuid4()},
            )


def test_rejects_relation_to_missing_challenge(connection) -> None:
    criterion_id = connection.scalar(text("SELECT id FROM criterio WHERE codigo = 'C1'"))
    with pytest.raises(IntegrityError):
        with connection.begin_nested():
            connection.execute(
                text(
                    "INSERT INTO desafio_criterio (desafio_id, criterio_id, obligatorio, configuracion) "
                    "VALUES (:challenge_id, :criterion_id, true, '{\"aplica\": true, \"parametros\": {}}'::jsonb)"
                ),
                {"challenge_id": uuid.uuid4(), "criterion_id": criterion_id},
            )


def test_rejects_two_active_rules_for_one_criterion(connection) -> None:
    criterion_id = connection.scalar(text("SELECT id FROM criterio WHERE codigo = 'C1'"))
    with pytest.raises(IntegrityError):
        with connection.begin_nested():
            connection.execute(
                text(
                    "INSERT INTO regla (id, criterio_id, tipo, parametros, mensajes, version, activa) "
                    "VALUES (:id, :criterion_id, 'tarea_declarada', '{}'::jsonb, '{}'::jsonb, 2, true)"
                ),
                {"id": uuid.uuid4(), "criterion_id": criterion_id},
            )


def test_seed_does_not_overwrite_existing_rows(connection):
    with connection.begin_nested() as transaction:
        connection.execute(text("UPDATE criterio SET nombre = 'Edición ficticia' WHERE codigo = 'C1'"))
        connection.execute(text("UPDATE desafio SET titulo = 'Revisión ficticia' WHERE codigo = 'D01_CORREO_REUNION'"))
        connection.execute(text("UPDATE regla SET mensajes = mensajes || '{\"nota_prueba\":\"conservar\"}'::jsonb WHERE criterio_id = (SELECT id FROM criterio WHERE codigo='C1')"))
        before = connection.execute(text("SELECT id, parametros, mensajes FROM regla ORDER BY id")).all()
        seed_initial_data(connection)
        assert connection.scalar(text("SELECT nombre FROM criterio WHERE codigo = 'C1'")) == "Edición ficticia"
        assert connection.scalar(text("SELECT titulo FROM desafio WHERE codigo = 'D01_CORREO_REUNION'")) == "Revisión ficticia"
        assert before == connection.execute(text("SELECT id, parametros, mensajes FROM regla ORDER BY id")).all()
        transaction.rollback()


def _practice_graph(connection):
    ids = {key: uuid.uuid4() for key in ("usuario", "practica", "version", "evaluacion")}
    connection.execute(text(
        "INSERT INTO usuario(id,correo,clave_hash) VALUES (:usuario,:correo,'ficticio-no-autenticable')"
    ), {**ids, "correo": f"{ids['usuario']}@example.invalid"})
    connection.execute(text(
        "INSERT INTO practica(id,usuario_id,objetivo,modo,configuracion_propia,request_id,entrada_hash) "
        "VALUES (:practica,:usuario,'Objetivo ficticio','guiado','{}',:practica,'hash-ficticio')"
    ), ids)
    connection.execute(text(
        "INSERT INTO version_prompt(id,practica_id,numero,componentes,texto,request_id,contenido_hash) "
        "VALUES (:version,:practica,1,'{}','Texto ficticio',:version,'hash-ficticio')"
    ), ids)
    connection.execute(text(
        "INSERT INTO evaluacion(id,version_id,snapshot,firma_comparacion,motor_version,cumplidos,aplicables) "
        "VALUES (:evaluacion,:version,'{}','firma-ficticia','prueba',0,6)"
    ), ids)
    return ids


def test_rejects_null_own_goal(connection):
    with connection.begin_nested() as outer:
        ids = _practice_graph(connection)
        with pytest.raises(IntegrityError):
            with connection.begin_nested():
                connection.execute(text("UPDATE practica SET objetivo=NULL WHERE id=:practica"), ids)
        outer.rollback()


def test_rejects_duplicate_version_number(connection):
    with connection.begin_nested() as outer:
        ids = _practice_graph(connection)
        with pytest.raises(IntegrityError):
            with connection.begin_nested():
                connection.execute(text(
                    "INSERT INTO version_prompt(id,practica_id,numero,componentes,texto,request_id,contenido_hash) "
                    "VALUES (:nuevo,:practica,1,'{}','Otro texto ficticio',:nuevo,'hash-ficticio')"
                ), {**ids, "nuevo": uuid.uuid4()})
        outer.rollback()


@pytest.mark.parametrize("criterion,rule,state", [
    ("C1", "C2", "cumple"),
    ("C1", None, "no_aplica"),
    ("C1", "C1", "advertencia"),
    ("C2", None, "cumple"),
])
def test_rejects_inconsistent_result(connection, criterion, rule, state):
    with connection.begin_nested() as outer:
        ids = _practice_graph(connection)
        criterion_id = connection.scalar(text("SELECT id FROM criterio WHERE codigo=:codigo"), {"codigo": criterion})
        rule_id = connection.scalar(text(
            "SELECT r.id FROM regla r JOIN criterio c ON c.id=r.criterio_id WHERE c.codigo=:codigo"
        ), {"codigo": rule}) if rule else None
        with pytest.raises(IntegrityError):
            with connection.begin_nested():
                connection.execute(text(
                    "INSERT INTO resultado(evaluacion_id,criterio_id,regla_id,estado,evidencia,condicion_esperada,mensaje,accion_sugerida) "
                    "VALUES (:evaluacion,:criterio,:regla,:estado,'{}','Prueba','Prueba','Prueba')"
                ), {**ids, "criterio": criterion_id, "regla": rule_id, "estado": state})
        outer.rollback()


def test_practice_delete_cascades_without_orphans(connection):
    with connection.begin_nested() as outer:
        ids = _practice_graph(connection)
        connection.execute(text("DELETE FROM practica WHERE id=:practica"), ids)
        assert connection.scalar(text("SELECT count(*) FROM version_prompt WHERE id=:version"), ids) == 0
        assert connection.scalar(text("SELECT count(*) FROM evaluacion WHERE id=:evaluacion"), ids) == 0
        assert connection.scalar(text("SELECT count(*) FROM usuario WHERE id=:usuario"), ids) == 1
        outer.rollback()
