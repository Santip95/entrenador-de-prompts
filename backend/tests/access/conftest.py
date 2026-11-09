from contextlib import contextmanager
import hashlib
import hmac
from pathlib import Path
import secrets
import socket
import subprocess
import time
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from app.core.config import ConfigurationError, ROOT_DIR, Settings
from app.main import create_app


@pytest.fixture(scope="session")
def mailpit():
    binary = ROOT_DIR / "local-data" / "mailpit" / "mailpit.exe"
    if not binary.exists():
        pytest.skip("Mailpit oficial no instalado: ejecutar scripts/install_mailpit.py")
    # Si ya está iniciado, usarlo sin vaciar ni borrar correos ajenos a las pruebas.
    process = None
    with socket.socket() as probe:
        busy = probe.connect_ex(("127.0.0.1", 8025)) == 0
    if not busy:
        process = subprocess.Popen([str(binary), "--listen", "127.0.0.1:8025", "--smtp", "127.0.0.1:1025", "--disable-version-check", "--smtp-disable-rdns", "--quiet"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
    for _ in range(60):
        try:
            if httpx.get("http://127.0.0.1:8025/api/v1/info").status_code == 200:
                break
        except httpx.HTTPError:
            pass
        time.sleep(.1)
    else:
        if process:
            process.terminate()
        pytest.fail("Mailpit no responde en 127.0.0.1:8025")
    yield
    if process:
        process.terminate()
        process.wait(timeout=10)


@pytest.fixture
def env(mailpit):
    local = Settings()
    try:
        migration_url = local.resolved_migration_url(test=True)
    except ConfigurationError:
        pytest.skip("Falta MIGRATION_PASSWORD: separación administrativa pendiente")
    owner = create_engine(migration_url, hide_parameters=True)
    runtime = create_engine(local.resolved_test_database_url(), hide_parameters=True)
    key = secrets.token_urlsafe(48)
    settings = Settings(_env_file=None, postgres_password=local.postgres_password,
                        DATABASE_URL=local.resolved_test_database_url(), app_env="test",
                        csrf_signing_key=key, review_signing_key=secrets.token_urlsafe(48),
                        alert_fingerprint_key=secrets.token_urlsafe(48))
    application = create_app(settings, runtime)
    users = []
    keys = []
    with TestClient(application, raise_server_exceptions=False) as client:
        service = application.state.access
        original = service.rate

        def rate(scope, value, maximum):
            keys.append(hmac.new(key.encode(), (scope+":"+value).encode(), hashlib.sha256).hexdigest())
            return original(scope, value, maximum)

        service.rate = rate

        class Environment:
            app = application
            api = client
            db = owner
            access = service
            engine = runtime
            origin = settings.public_origin
            created_users = users

            def post(self, path, data=None, csrf=None, browser=None):
                headers = {"Origin": self.origin}
                if csrf is not None:
                    headers["X-CSRF-Token"] = csrf
                return (browser or self.api).post("/api/v1"+path, json=data or {}, headers=headers)

            def account(self, role="usuario", password="Una frase ficticia á número 71"):
                email = f"t03-{uuid4()}@example.invalid"
                self.access.register(email, password)
                with self.db.begin() as c:
                    uid = c.scalar(text("SELECT id FROM usuario WHERE correo=:email"), {"email": email})
                    if role != "usuario":
                        c.execute(text("UPDATE usuario SET rol=:role WHERE id=:id"), {"role": role, "id": uid})
                users.append(uid)
                return uid, email, password

            def login(self, account, browser=None):
                result = self.post("/auth/login", {"correo": account[1], "password": account[2]}, browser=browser)
                assert result.status_code == 200
                return (browser or self.api).cookies.get("ep_session")

            def csrf(self, browser=None):
                result = (browser or self.api).get("/api/v1/auth/csrf")
                assert result.status_code == 200
                return result.json()["csrf_token"]

            @contextmanager
            def browser(self):
                other = TestClient(self.app, raise_server_exceptions=False)
                try:
                    yield other
                finally:
                    other.close()

            def recover(self, account):
                response = self.post("/auth/recuperacion", {"correo": account[1]})
                assert response.status_code == 202
                listing = httpx.get("http://127.0.0.1:8025/api/v1/messages").json()
                matching = [m for m in listing["messages"] if any(r["Address"] == account[1] for r in m["To"])]
                assert bool(matching), "Correo no recibido por SMTP real"
                message = httpx.get("http://127.0.0.1:8025/api/v1/message/" + matching[0]["ID"]).json()
                import re
                match = re.search(r"#restablecer=([A-Za-z0-9_-]+)", message["Text"])
                assert bool(match), "Enlace de recuperación ausente"
                return match.group(1)

        context = Environment()
        yield context
    with owner.begin() as c:
        if users:
            c.execute(text("DELETE FROM usuario WHERE id=ANY(:ids)"), {"ids": users})
        if keys:
            c.execute(text("DELETE FROM limite_solicitud WHERE clave=ANY(:keys)"), {"keys": keys})
    owner.dispose()


@pytest.fixture
def account(env):
    return env.account()
