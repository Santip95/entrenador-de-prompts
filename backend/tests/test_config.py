import pytest
from sqlalchemy.engine import make_url

from app.core.config import ConfigurationError, Settings


def test_builds_postgresql_url_without_exposing_password() -> None:
    settings = Settings(
        _env_file=None,
        postgres_user="entrenador_app",
        postgres_password="contraseña de prueba",
        postgres_db="entrenador_prompts",
    )

    url = settings.resolved_database_url()

    assert url.startswith("postgresql+psycopg://entrenador_app:")
    assert make_url(url).password == "contraseña de prueba"
    assert url.endswith("@127.0.0.1:5432/entrenador_prompts")


def test_requires_database_secret_without_echoing_its_value() -> None:
    settings = Settings(_env_file=None, postgres_password=None)

    with pytest.raises(ConfigurationError, match="POSTGRES_PASSWORD"):
        settings.validate_runtime()


def test_builds_an_independent_test_database_url() -> None:
    settings = Settings(
        _env_file=None,
        postgres_password="clave de prueba",
        postgres_test_db="entrenador_prompts_test",
    )

    assert settings.resolved_test_database_url().endswith(
        "@127.0.0.1:5432/entrenador_prompts_test"
    )


@pytest.mark.parametrize("url", [
    "postgresql+psycopg://entrenador_app:ficticia@127.0.0.1:5432/entrenador_prompts",
    "postgresql+psycopg://postgres:ficticia@127.0.0.1:5432/entrenador_prompts_test",
    "postgresql+psycopg://entrenador_app:ficticia@otro-host:5432/entrenador_prompts_test",
])
def test_rejects_unsafe_test_targets(url):
    settings = Settings(_env_file=None, TEST_DATABASE_URL=url)
    with pytest.raises(ConfigurationError):
        settings.resolved_test_database_url()


def test_special_password_roundtrip():
    password = "ficticia + @:/%#?"
    settings = Settings(_env_file=None, postgres_password=password)
    assert make_url(settings.resolved_database_url()).password == password
