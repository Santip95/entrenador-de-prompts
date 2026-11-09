"""Casos técnicos SEC con PostgreSQL real y SMTP real a Mailpit.

Las dos sesiones son clientes HTTP independientes, no navegadores visuales.
No se implementan endpoints de prácticas/versiones de la etapa 04.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
from datetime import timedelta
import secrets
import threading
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.application.access import AccessError, AccessService, digest
from app.scripts.manage_access import invalidate_all, promote_admin

pytestmark = pytest.mark.integration


def test_031_register_duplicate_and_forbid_role(env):
    email = f"register-{uuid4()}@example.invalid"
    data = {"correo": email, "password": "Frase de registro ficticia número 5"}
    first = env.post("/auth/registro", data)
    second = env.post("/auth/registro", data)
    assert first.status_code == second.status_code == 202
    assert first.json() == second.json()
    with env.db.begin() as c:
        rows = c.execute(text("SELECT id,rol,clave_hash FROM usuario WHERE correo=:email"), {"email": email}).mappings().all()
        env.created_users.extend(r["id"] for r in rows)
        assert len(rows) == 1 and rows[0]["rol"] == "usuario"
        assert rows[0]["clave_hash"].startswith("$argon2id$")
    assert env.post("/auth/registro", dict(data, rol="administrador")).status_code == 422
    assert env.post("/auth/login", data).status_code == 200


def test_032_generic_login_and_dummy_verification(env, account, monkeypatch):
    calls = []
    real = env.access.verify
    def verify(encoded, password):
        calls.append(encoded.startswith("$argon2id$"))
        return real(encoded, password)
    monkeypatch.setattr(env.access, "verify", verify)
    wrong = env.post("/auth/login", {"correo": account[1], "password": "Contraseña incorrecta ficticia 8"})
    absent = env.post("/auth/login", {"correo": "desconocido@example.invalid", "password": "Contraseña incorrecta ficticia 8"})
    assert wrong.status_code == absent.status_code == 401
    assert wrong.json()["error"]["message"] == absent.json()["error"]["message"]
    assert calls == [True, True]


def test_sec05_logout_rotates_and_revokes_only_current(env, account):
    first = env.login(account)
    with env.browser() as other:
        second = env.login(account, other)
        assert first != second
        csrf = env.csrf()
        assert env.post("/auth/logout", csrf=csrf).status_code == 204
        assert env.api.get("/api/v1/auth/me").status_code == 401
        assert other.get("/api/v1/auth/me").status_code == 200
        with pytest.raises(AccessError):
            with env.access.authorized(first):
                pass


@pytest.mark.parametrize("length,allowed", [(14,False),(15,True),(128,True),(129,False)])
def test_sec03_registration_boundaries(env, length, allowed):
    email = f"boundary-{uuid4()}@example.invalid"
    password = "Á " + "z"*(length-2)
    response = env.post("/auth/registro", {"correo": email, "password": password})
    assert response.status_code == (202 if allowed else 422)
    with env.db.begin() as c:
        uid = c.scalar(text("SELECT id FROM usuario WHERE correo=:email"), {"email": email})
        if uid:
            env.created_users.append(uid)
    if allowed:
        assert env.post("/auth/login", {"correo": email, "password": password}).status_code == 200


def test_sec03_password_not_trimmed(env):
    account = env.account(password="  Frase ficticia con bordes á  ")
    env.login(account)
    assert env.post("/auth/login", {"correo": account[1], "password": account[2].strip()}).status_code == 401


def test_sec04_five_failures_revoke_and_timeout_does_not_revive(env, account):
    old = env.login(account)
    for _ in range(5):
        response = env.post("/auth/login", {"correo": account[1], "password": "Fallo ficticio de autenticación"})
        assert response.status_code == 401
    with env.db.begin() as c:
        user = c.execute(text("SELECT estado,bloqueado_hasta,auth_epoch FROM usuario WHERE id=:id"), {"id": account[0]}).mappings().one()
        now = c.scalar(text("SELECT clock_timestamp()"))
        assert user["estado"] == "bloqueado"
        assert timedelta(minutes=14) < user["bloqueado_hasta"]-now <= timedelta(minutes=15)
        assert user["auth_epoch"] > 0
        c.execute(text("UPDATE usuario SET bloqueado_hasta=clock_timestamp()-interval '1 second' WHERE id=:id"), {"id": account[0]})
    env.login(account)
    with pytest.raises(AccessError):
        with env.access.authorized(old):
            pass


def test_sec04_ip_limit_shared_between_service_instances(env):
    second = AccessService(env.engine, env.app.state.settings)
    for _ in range(20):
        assert env.access.rate("login", "testclient", 20)
    assert not second.rate("login", "testclient", 20)
    assert env.post("/auth/login", {"correo":"inexistente@example.invalid", "password":"Una frase ficticia para el límite"}).status_code == 429
    with env.db.begin() as c:
        c.execute(text("UPDATE limite_solicitud SET desde=clock_timestamp()-interval '16 minutes' WHERE clave=:key"), {"key": hmac.new(env.access.key,b'login:testclient',hashlib.sha256).hexdigest()})
    assert second.rate("login", "testclient", 20)


@pytest.mark.parametrize("change", ["idle", "absolute", "epoch", "revoked"])
def test_sec05_server_expirations_and_deleted_cookie(env, account, change):
    session = env.login(account)
    sql = {
        "idle": "ultimo_uso_en=clock_timestamp()-interval '30 minutes'",
        "absolute": "creado_en=clock_timestamp()-interval '8 hours'",
        "revoked": "revocada_en=clock_timestamp()",
    }
    with env.db.begin() as c:
        if change == "epoch":
            c.execute(text("UPDATE usuario SET auth_epoch=auth_epoch+1 WHERE id=:id"), {"id": account[0]})
        else:
            c.execute(text("UPDATE sesion SET " + sql[change] + " WHERE token_hash=:hash"), {"hash": digest(session)})
    response = env.api.get("/api/v1/auth/me", headers={"Date": "Mon, 01 Jan 1990 00:00:00 GMT"})
    assert response.status_code == 401
    assert "Max-Age=0" in response.headers.get("set-cookie", "")


def test_cookie_flags_rotation_and_hash_only(env, account):
    first = env.login(account)
    second_response = env.post("/auth/login", {"correo": account[1], "password": account[2]})
    second = env.api.cookies.get("ep_session")
    assert first != second
    cookie = second_response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie and "Path=/" in cookie
    assert "Secure" not in cookie  # Sólo localhost; producción lo exige.
    with env.db.begin() as c:
        hashes = c.scalars(text("SELECT token_hash FROM sesion WHERE usuario_id=:id"), {"id": account[0]}).all()
        assert all(h != first and h != second for h in hashes)
    with pytest.raises(AccessError):
        with env.access.authorized(first):
            pass


def test_sec01_two_independent_sessions_admin_block_and_unblock(env, account):
    first = env.login(account)
    with env.browser() as other:
        second = env.login(account, other)
        admin = env.account("administrador")
        env.login(admin)
        admin_csrf = env.csrf()
        assert env.post(f"/admin/cuentas/{account[0]}/estado", {"estado": "bloqueado", "motivo": "seguridad"}, csrf=admin_csrf).status_code == 204
        for session in [first, second]:
            with pytest.raises(AccessError):
                with env.access.authorized(session):
                    pass
        assert other.get("/api/v1/auth/me").status_code == 401
        assert env.post(f"/admin/cuentas/{account[0]}/estado", {"estado": "activo", "motivo": "correccion"}, csrf=admin_csrf).status_code == 204
        with pytest.raises(AccessError):
            with env.access.authorized(first):
                pass
        env.login(account)


@pytest.mark.parametrize("state", ["bloqueado", "desactivado"])
def test_admin_restriction_does_not_expire_or_recover(env, account, state):
    old = env.login(account)
    admin = env.account("administrador")
    env.login(admin)
    response = env.post(f"/admin/cuentas/{account[0]}/estado", {"estado": state, "motivo": "seguridad"}, csrf=env.csrf())
    assert response.status_code == 204
    assert env.post("/auth/login", {"correo": account[1], "password": account[2]}).status_code == 401
    assert env.post("/auth/recuperacion", {"correo": account[1]}).status_code == 202
    with env.db.begin() as c:
        assert c.scalar(text("SELECT bloqueado_hasta IS NULL FROM usuario WHERE id=:id"), {"id": account[0]})
        assert c.scalar(text("SELECT count(*) FROM recuperacion_acceso WHERE usuario_id=:id"), {"id": account[0]}) == 0


def test_sec06_smtp_reset_single_use_and_global_revocation(env, account, caplog):
    first = env.login(account)
    token = env.recover(account)
    new = "Otra frase ficticia para recuperar á 38"
    response = env.post("/auth/restablecer", {"token": token, "password_nueva": new})
    assert response.status_code == 204
    assert env.post("/auth/restablecer", {"token": token, "password_nueva": new}).status_code == 400
    assert env.post("/auth/login", {"correo": account[1], "password": account[2]}).status_code == 401
    assert env.post("/auth/login", {"correo": account[1], "password": new}).status_code == 200
    with pytest.raises(AccessError):
        with env.access.authorized(first):
            pass
    assert token not in caplog.text and new not in caplog.text


@pytest.mark.parametrize("case", ["expired", "blocked", "disabled", "unknown"])
def test_sec06_reset_negative_cases(env, account, case):
    reset = env.recover(account)
    with env.db.begin() as c:
        if case == "expired":
            c.execute(text("UPDATE recuperacion_acceso SET expira_en=clock_timestamp()-interval '1 second' WHERE usuario_id=:id"), {"id": account[0]})
        elif case in {"blocked", "disabled"}:
            c.execute(text("UPDATE usuario SET estado=:state WHERE id=:id"), {"id": account[0], "state": "bloqueado" if case == "blocked" else "desactivado"})
        else:
            reset = secrets.token_urlsafe(32)
    response = env.post("/auth/restablecer", {"token": reset, "password_nueva": "Otra contraseña ficticia para probar"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "recuperacion_invalida"


def test_sec06_two_consumers_exactly_one_commits(env, account):
    reset = env.recover(account)
    gate = threading.Barrier(2)
    def consume():
        gate.wait(timeout=5)
        try:
            env.access.reset(reset, "Restablecimiento concurrente ficticio á")
            return 204
        except AccessError as error:
            return error.status
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = sorted(pool.map(lambda _: consume(), range(2)))
    assert results == [204, 400]


def test_sec06_policy_invalid_reset_does_not_consume(env, account):
    reset = env.recover(account)
    assert env.post("/auth/restablecer", {"token": reset, "password_nueva": "corta"}).status_code == 422
    assert env.post("/auth/restablecer", {"token": reset, "password_nueva": "Frase de recuperación ficticia á"}).status_code == 204


def test_sec09_password_change_revokes_sessions_and_reset_tokens(env, account):
    first = env.login(account)
    reset = env.recover(account)
    new = "Nueva frase para cambio de clave á 51"
    response = env.post("/cuenta/cambiar-clave", {"password_actual": account[2], "password_nueva": new}, csrf=env.csrf())
    assert response.status_code == 204
    with pytest.raises(AccessError):
        with env.access.authorized(first):
            pass
    assert env.post("/auth/restablecer", {"token": reset, "password_nueva": new}).status_code == 400
    assert env.post("/auth/login", {"correo": account[1], "password": new}).status_code == 200


def test_sec07_common_user_cannot_admin_or_choose_role(env, account):
    env.login(account)
    assert env.api.get("/api/v1/admin/cuentas").status_code == 403
    response = env.post(f"/admin/cuentas/{account[0]}/estado", {"estado": "activo", "motivo": "correccion"}, csrf=env.csrf())
    assert response.status_code == 403


def test_last_admin_protected_and_list_minimal(env):
    admin = env.account("administrador")
    env.login(admin)
    response = env.api.get("/api/v1/admin/cuentas")
    assert response.status_code == 200
    assert all(set(item) == {"id", "correo", "rol", "estado"} for item in response.json()["items"])
    result = env.post(f"/admin/cuentas/{admin[0]}/estado", {"estado": "desactivado", "motivo": "seguridad"}, csrf=env.csrf())
    assert result.status_code == 409


@pytest.mark.parametrize("bad", ["missing_csrf", "wrong_csrf", "origin", "content"])
def test_sec08_csrf_and_origin(env, account, bad):
    env.login(account)
    headers = {"Origin": env.origin, "X-CSRF-Token": env.csrf()}
    if bad == "missing_csrf":
        headers.pop("X-CSRF-Token")
    elif bad == "wrong_csrf":
        headers["X-CSRF-Token"] = "incorrecto"
    elif bad == "origin":
        headers["Origin"] = "https://otro.example.invalid"
    else:
        headers["Content-Type"] = "text/plain"
    response = env.api.post("/api/v1/auth/logout", json={}, headers=headers)
    assert response.status_code == (400 if bad == "content" else 403)


def test_sec08_csrf_bound_to_session(env, account):
    env.login(account)
    old = env.csrf()
    env.login(account)
    assert env.post("/auth/logout", csrf=old).status_code == 403


@pytest.mark.parametrize("path", ["/auth/registro", "/auth/login", "/auth/recuperacion", "/auth/restablecer"])
def test_sec17_errors_never_echo_sensitive_body(env, path, caplog):
    marker = f"privado-{uuid4()}@example.invalid"
    response = env.post(path, {"correo": marker, "password": {"valor": marker}, "token": marker})
    assert response.status_code == 422
    assert marker not in response.text and marker not in caplog.text
    assert set(response.json()["error"]) == {"code", "message", "fields", "request_id"}


def test_invalid_json_and_size_limit_no_echo(env):
    response = env.api.post("/api/v1/auth/registro", content='{"correo":"sensible@example.invalid",', headers={"Origin": env.origin,"Content-Type":"application/json"})
    assert response.status_code == 400
    assert "sensible@example.invalid" not in response.text
    invalid_utf8 = env.api.post("/api/v1/auth/registro", content=b'\xff', headers={"Origin": env.origin,"Content-Type":"application/json"})
    assert invalid_utf8.status_code == 400
    response = env.api.post("/api/v1/auth/registro", content=b"x"*65537, headers={"Origin": env.origin,"Content-Type":"application/json"})
    assert response.status_code == 413


@pytest.mark.parametrize("ddl", ["CREATE TABLE public.etapa03_probe(id int)", "ALTER TABLE public.usuario ADD COLUMN etapa03_probe int", "DROP TABLE public.limite_solicitud", "CREATE TEMP TABLE etapa03_probe(id int)", "CREATE SCHEMA etapa03_probe", "SET ROLE entrenador_migracion"])
def test_runtime_no_ddl_or_owner_membership(env, ddl):
    with env.engine.connect() as c:
        transaction = c.begin()
        try:
            with pytest.raises(DBAPIError) as failure:
                c.execute(text(ddl))
            assert failure.value.orig.sqlstate == "42501"
        finally:
            transaction.rollback()


def test_sec09_restoration_invalidation_hook(env, account):
    old = env.login(account)
    reset = env.recover(account)
    # Probar el hook sólo sobre fixtures propias, usando savepoint: no restaurar backups.
    with env.db.connect() as c:
        transaction = c.begin()
        try:
            invalidate_all(c)
            assert c.scalar(text("SELECT auth_epoch FROM usuario WHERE id=:id"), {"id": account[0]}) > 0
            assert c.scalar(text("SELECT count(*) FROM sesion WHERE usuario_id=:id AND revocada_en IS NULL"), {"id": account[0]}) == 0
            assert c.scalar(text("SELECT count(*) FROM recuperacion_acceso WHERE usuario_id=:id AND usado_en IS NULL"), {"id": account[0]}) == 0
        finally:
            transaction.rollback()


@pytest.mark.parametrize("role", ["usuario", "administrador"])
def test_sec07_ownership_cannot_be_bypassed_by_role(env, account, role):
    from fastapi import Request
    from uuid import UUID
    owner, outsider = account, env.account(role)
    practice, version = uuid4(), uuid4()
    literal = "<script>alert('ficticio')</script> '; DROP TABLE usuario;--"
    with env.db.begin() as c:
        c.execute(text("INSERT INTO practica(id,usuario_id,objetivo,modo,configuracion_propia,request_id,entrada_hash) VALUES (:id,:uid,:goal,'guiado','{}',:id,'fixture')"), {"id":practice,"uid":owner[0],"goal":literal})
        c.execute(text("INSERT INTO version_prompt(id,practica_id,numero,componentes,texto,request_id,contenido_hash) VALUES (:id,:pid,1,'{}',:body,:id,'fixture')"), {"id":version,"pid":practice,"body":literal})

    # Adaptador HTTP exclusivo de la prueba, no un endpoint funcional del producto.
    @env.app.get("/_tests/version/{resource_id}")
    def test_only_read(resource_id: UUID, request: Request):
        session = request.cookies.get("ep_session")
        with env.access.authorized(session) as (c, user, s):
            return dict(env.access.owned(c, user, "version", resource_id))

    env.login(owner)
    own = env.api.get(f"/_tests/version/{version}")
    assert own.status_code == 200 and own.json()["texto"] == literal
    env.login(outsider)
    denied = env.api.get(f"/_tests/version/{version}")
    assert denied.status_code == 404 and literal not in denied.text
    with env.access.authorized(env.api.cookies.get("ep_session")) as (c, user, s):
        with pytest.raises(AccessError) as failure:
            env.access.owned(c, user, "practica", practice)
        assert failure.value.status == 404
    with env.db.begin() as c:
        assert c.scalar(text("SELECT count(*) FROM usuario WHERE id=:id"), {"id": owner[0]}) == 1


@pytest.mark.parametrize("state", ["bloqueado", "desactivado"])
def test_sec02_write_serializes_before_restriction(env, account, state):
    from concurrent.futures import TimeoutError
    session = env.login(account)
    csrf = env.csrf()
    admin = env.account("administrador")
    admin_session = env.login(admin)
    admin_csrf = env.csrf()
    locked, release, restricting = threading.Event(), threading.Event(), threading.Event()
    audit_id = uuid4()

    def write():
        with env.access.authorized(session, csrf=csrf, write=True) as (c, user, s):
            locked.set()
            assert release.wait(10)
            c.execute(text("INSERT INTO evento_auditoria(id,actor_id,evento,recurso_tipo,metadatos) VALUES (:id,:uid,'prueba_carrera','cuenta','{}')"), {"id": audit_id, "uid": user["id"]})

    def restrict():
        restricting.set()
        env.access.set_state(admin_session, admin_csrf, account[0], state, "seguridad")

    with ThreadPoolExecutor(max_workers=2) as pool:
        writing = pool.submit(write)
        assert locked.wait(5)
        blocking = pool.submit(restrict)
        assert restricting.wait(5)
        try:
            with pytest.raises(TimeoutError):
                blocking.result(timeout=.25)
        finally:
            release.set()
        writing.result(timeout=10)
        blocking.result(timeout=10)
    with env.db.begin() as c:
        assert c.scalar(text("SELECT estado FROM usuario WHERE id=:id"), {"id": account[0]}) == state
        assert c.scalar(text("SELECT count(*) FROM evento_auditoria WHERE id=:id"), {"id": audit_id}) == 1
    # Segunda ordenación: la restricción ya confirmó; la escritura debe fallar.
    with pytest.raises(AccessError):
        with env.access.authorized(session, csrf=csrf, write=True):
            pytest.fail("Una sesión vieja llegó a la escritura después del bloqueo")


def test_sec09_role_changes_are_read_server_side(env, account):
    old = env.login(account)
    assert env.api.get("/api/v1/admin/cuentas").status_code == 403
    # Mismo procedimiento transaccional que la herramienta operativa local.
    with env.db.begin() as c:
        promote_admin(c, account[1])
    assert env.api.get("/api/v1/auth/me").status_code == 401
    env.login(account)
    assert env.api.get("/api/v1/admin/cuentas").status_code == 200
    # Aun si un cambio externo omite revocación, no conservar el privilegio copiado.
    with env.db.begin() as c:
        c.execute(text("UPDATE usuario SET rol='usuario' WHERE id=:id"), {"id": account[0]})
    assert env.api.get("/api/v1/admin/cuentas").status_code == 403


def test_recovery_response_generic_and_expiry_server_side(env, account):
    unknown = env.post("/auth/recuperacion", {"correo": "ausente@example.invalid"})
    known = env.post("/auth/recuperacion", {"correo": account[1]})
    assert known.status_code == unknown.status_code == 202 and known.json() == unknown.json()
    with env.db.begin() as c:
        duration = c.scalar(text("SELECT expira_en-creado_en FROM recuperacion_acceso WHERE usuario_id=:id"), {"id": account[0]})
        assert timedelta(minutes=14, seconds=59) < duration <= timedelta(minutes=15, seconds=1)


def test_reset_invalidates_other_pending_tokens(env, account):
    first = env.recover(account)
    second = env.recover(account)
    assert first != second
    new = "Frase ficticia para invalidar los otros enlaces"
    assert env.post("/auth/restablecer", {"token": first, "password_nueva": new}).status_code == 204
    assert env.post("/auth/restablecer", {"token": second, "password_nueva": new}).status_code == 400


def test_mail_dependency_failure_generic_no_active_token(env, account, monkeypatch, caplog):
    import smtplib
    def unavailable(*args, **kwargs):
        raise OSError("Detalle privado que no debe llegar al usuario")
    monkeypatch.setattr(smtplib, "SMTP", unavailable)
    response = env.post("/auth/recuperacion", {"correo": account[1]})
    assert response.status_code == 202
    assert "Detalle privado" not in response.text and "Detalle privado" not in caplog.text
    with env.db.begin() as c:
        assert c.scalar(text("SELECT count(*) FROM recuperacion_acceso WHERE usuario_id=:id"), {"id": account[0]}) == 0
        assert c.scalar(text("SELECT count(*) FROM evento_auditoria WHERE evento='correo_no_disponible'")) > 0


def test_public_origin_required_and_session_id_not_chosen_by_client(env, account):
    data = {"correo": account[1], "password": account[2]}
    assert env.api.post("/api/v1/auth/login", json=data).status_code == 403
    chosen = secrets.token_urlsafe(32)
    env.api.cookies.set("ep_session", chosen)
    response = env.post("/auth/login", data)
    assert response.status_code == 200
    assert chosen not in response.headers["set-cookie"]
    assert response.headers["cache-control"] == "no-store"


def test_login_upgrades_old_argon2_parameters(env, account):
    from argon2 import PasswordHasher, Type
    old = PasswordHasher(memory_cost=19456, time_cost=2, parallelism=1, type=Type.ID).hash(account[2])
    with env.db.begin() as c:
        c.execute(text("UPDATE usuario SET clave_hash=:hash WHERE id=:id"), {"hash": old, "id": account[0]})
    env.login(account)
    with env.db.begin() as c:
        current = c.scalar(text("SELECT clave_hash FROM usuario WHERE id=:id"), {"id": account[0]})
        assert current.startswith("$argon2id$v=19$m=65536,t=3,p=1$")


def test_concurrent_counter_refresh_and_purge_do_not_deadlock(env):
    from sqlalchemy import event
    for value in ("a", "b"):
        assert env.access.rate("purga_concurrente", value, 5)
    keys = [hmac.new(env.access.key, ("purga_concurrente:"+value).encode(), hashlib.sha256).hexdigest() for value in ("a", "b")]
    with env.db.begin() as c:
        c.execute(text("UPDATE limite_solicitud SET desde=clock_timestamp()-interval '2 days' WHERE clave=ANY(:keys)"), {"keys": keys})
    gate = threading.Barrier(2)

    def synchronize_before_purge(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith("DELETE FROM limite_solicitud"):
            gate.wait(timeout=10)

    event.listen(env.engine, "before_cursor_execute", synchronize_before_purge)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda value: env.access.rate("purga_concurrente", value, 5), ("a", "b")))
        assert outcomes == [True, True]
    finally:
        event.remove(env.engine, "before_cursor_execute", synchronize_before_purge)


@pytest.mark.parametrize("email", ["a,b@example.invalid", "a;@example.invalid", "a..b@example.invalid"], ids=["lista","separador","local_invalido"])
def test_registration_and_recovery_reject_invalid_mailbox(env, email):
    for path, data in [("/auth/registro", {"correo": email, "password": "Frase de validación ficticia á 67"}), ("/auth/recuperacion", {"correo": email})]:
        response = env.post(path, data)
        assert response.status_code == 422
        assert email not in response.text


def test_email_login_normalized_without_altering_password(env, account):
    response = env.post("/auth/login", {"correo": "  "+account[1].upper()+"  ", "password": account[2]})
    assert response.status_code == 200
    assert response.json()["correo"] == account[1]
