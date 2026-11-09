"""Política y contratos sin conexión a PostgreSQL ni SMTP."""
import secrets
import time

from argon2 import PasswordHasher, Type
import pytest

from app.application.access import AccessError, password_policy
from app.core.config import ConfigurationError, Settings
from app.main import create_app


@pytest.mark.parametrize("length,allowed", [(14,False),(15,True),(128,True),(129,False)])
def test_sec03_lengths(length, allowed):
    password = "Á " + "z"*(length-2)
    if allowed:
        password_policy(password)
    else:
        with pytest.raises(AccessError):
            password_policy(password)


@pytest.mark.parametrize("password", ["passwordpassword", "contraseña123456", "aaaaaaaaaaaaaaa"])
def test_common_list(password):
    with pytest.raises(AccessError):
        password_policy(password)


def test_argon2_id_parameters_and_unique_salt():
    hasher = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=1, type=Type.ID)
    password = "Frase ficticia á con espacios 28"
    first, second = hasher.hash(password), hasher.hash(password)
    assert first != second
    assert first.startswith("$argon2id$v=19$m=65536,t=3,p=1$")
    assert hasher.verify(first, password)
    assert not hasher.check_needs_rehash(first)


@pytest.mark.parametrize("changes", [
    {"csrf_signing_key": None}, {"csrf_signing_key": "corta"},
    {"password_min_length": 8}, {"password_max_length": 63},
    {"argon2_memory_kib": 1000}, {"log_request_bodies": True},
    {"session_idle_minutes": 60}, {"login_max_failures": 9}, {"session_cookie_samesite": "none"},
    {"smtp_host": "otro-servidor"}, {"smtp_port": 25},
    {"app_env": "production"}, {"app_env": "production", "session_cookie_secure": True, "public_origin": "https://example.invalid", "seed_demo_data": True},
])
def test_unsafe_configuration_rejected(changes):
    values = {"postgres_password": "ficticia-no-conexion", "csrf_signing_key": secrets.token_urlsafe(48)}
    values.update(changes)
    settings = Settings(_env_file=None, **values)
    with pytest.raises(ConfigurationError):
        settings.validate_access()


def test_openapi_access_only():
    paths = create_app(Settings(_env_file=None)).openapi()["paths"]
    assert "/api/v1/auth/registro" in paths
    assert "/api/v1/auth/csrf" in paths
    assert "/api/v1/admin/cuentas/{user_id}/estado" in paths
    assert "/api/v1/practicas" in paths
    assert "/api/v1/versiones/{vid}" in paths
