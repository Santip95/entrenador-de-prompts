from io import StringIO
from pathlib import Path

from alembic import command
from alembic.config import Config


def test_migration_generates_postgresql_sql(monkeypatch):
    """Compila SQL, sin equivaler a ejecutarlo en PostgreSQL."""
    monkeypatch.setenv("POSTGRES_PASSWORD", "ficticia-solo-compilacion")
    monkeypatch.setenv("MIGRATION_PASSWORD", "ficticia-solo-compilacion")
    monkeypatch.setenv("DATABASE_URL", "")
    output = StringIO()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"), output_buffer=output)
    command.upgrade(config, "head", sql=True)
    sql = output.getvalue()
    assert "CREATE TABLE version_prompt" in sql
    assert "CREATE TABLE recuperacion_acceso" in sql
    assert "fk_resultado_regla_criterio" in sql
    assert "ck_resultado_regla_aplicabilidad" in sql
    assert "objetivo IS NOT NULL" in sql
    assert "CREATE TRIGGER tr_resultado_estado" in sql
