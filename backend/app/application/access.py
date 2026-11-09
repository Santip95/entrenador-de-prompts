"""Acceso transaccional. Nunca recibe privilegios DDL ni registra cuerpos."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import timedelta
from email.message import EmailMessage
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import smtplib
from uuid import uuid4

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import text


class AccessError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


INVALID = "No se pudo iniciar sesión con esos datos."
RESET_INVALID = "El enlace no es válido o venció. Solicitá uno nuevo."
REGISTRATION = "Si los datos permiten crear una cuenta, ya podés intentar ingresar"
RECOVERY = "Si la cuenta permite recuperar el acceso, recibirás un correo."
COMMON = frozenset(json.loads(Path(__file__).with_name("common_passwords.json").read_text(encoding="utf-8")))
ADMIN_LOCK = 90505


def digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def password_policy(password):
    if not 15 <= len(password) <= 128 or password.casefold() in COMMON:
        raise AccessError(422, "password_invalida", "Usá entre 15 y 128 caracteres y evitá contraseñas comunes.")


class AccessService:
    def __init__(self, engine, settings):
        self.engine, self.settings = engine, settings
        self.hasher = PasswordHasher(memory_cost=settings.argon2_memory_kib,
                                     time_cost=settings.argon2_time_cost,
                                     parallelism=settings.argon2_parallelism, type=Type.ID)
        self._dummy = self.hasher.hash(secrets.token_urlsafe(32))
        self.key = settings.csrf_signing_key.get_secret_value().encode("utf-8")

    def verify(self, encoded, password):
        try:
            return self.hasher.verify(encoded, password)
        except (VerificationError, InvalidHashError):
            return False

    def csrf(self, token):
        return hmac.new(self.key, ("csrf:" + token).encode(), hashlib.sha256).hexdigest()

    def rate(self, scope, value, maximum):
        """Contador compartido PostgreSQL; no conservar IP/correo en claro."""
        key = hmac.new(self.key, (scope + ":" + value).encode(), hashlib.sha256).hexdigest()
        with self.engine.begin() as c:
            count = c.scalar(text("""
                INSERT INTO limite_solicitud(clave,desde,cantidad) VALUES (:key,clock_timestamp(),1)
                ON CONFLICT (clave) DO UPDATE SET
                  cantidad=CASE WHEN limite_solicitud.desde <= clock_timestamp()-interval '15 minutes'
                                THEN 1 ELSE limite_solicitud.cantidad+1 END,
                  desde=CASE WHEN limite_solicitud.desde <= clock_timestamp()-interval '15 minutes'
                             THEN clock_timestamp() ELSE limite_solicitud.desde END
                RETURNING cantidad
            """), {"key": key})
            # Contadores vencidos no se retienen indefinidamente.
            c.execute(text("DELETE FROM limite_solicitud WHERE clave IN (SELECT clave FROM limite_solicitud WHERE desde < clock_timestamp()-interval '1 day' ORDER BY clave LIMIT 1000 FOR UPDATE SKIP LOCKED)"))
        return count <= maximum

    @staticmethod
    def revoke(c, user):
        c.execute(text("UPDATE usuario SET auth_epoch=auth_epoch+1,actualizado_en=clock_timestamp() WHERE id=:id"), {"id": user})
        c.execute(text("UPDATE sesion SET revocada_en=clock_timestamp() WHERE usuario_id=:id AND revocada_en IS NULL"), {"id": user})

    @staticmethod
    def audit(c, actor, event, resource=None, reason=None):
        metadata = {"motivo": reason} if reason else {}
        c.execute(text("INSERT INTO evento_auditoria(id,actor_id,evento,recurso_tipo,recurso_id,metadatos) VALUES (:id,:actor,:event,'cuenta',:resource,CAST(:metadata AS jsonb))"),
                  {"id": uuid4(), "actor": actor, "event": event, "resource": resource, "metadata": json.dumps(metadata)})

    def register(self, correo, password):
        password_policy(password)
        encoded = self.hasher.hash(password)  # También para correo duplicado.
        with self.engine.begin() as c:
            c.execute(text("INSERT INTO usuario(id,correo,clave_hash) VALUES (:id,:email,:hash) ON CONFLICT(correo) DO NOTHING"),
                      {"id": uuid4(), "email": correo, "hash": encoded})

    def login(self, correo, password, old_token=None):
        failure = None
        token = None
        with self.engine.begin() as c:
            u = c.execute(text("SELECT * FROM usuario WHERE correo=:email FOR UPDATE"), {"email": correo}).mappings().first()
            now = c.scalar(text("SELECT clock_timestamp()"))
            valid_password = self.verify(u["clave_hash"] if u else self._dummy, password)
            if u and u["estado"] == "bloqueado" and u["bloqueado_hasta"] and u["bloqueado_hasta"] <= now:
                c.execute(text("UPDATE usuario SET estado='activo',bloqueado_hasta=NULL,fallos_login=0,ventana_fallos_desde=NULL WHERE id=:id"), {"id": u["id"]})
                u = dict(u, estado="activo", fallos_login=0, ventana_fallos_desde=None)
            if not u or u["estado"] != "activo":
                failure = (401, "credenciales_invalidas", INVALID)
            elif not valid_password:
                count = u["fallos_login"]+1 if u["ventana_fallos_desde"] and u["ventana_fallos_desde"] > now-timedelta(minutes=15) else 1
                c.execute(text("UPDATE usuario SET fallos_login=:n,ventana_fallos_desde=:start WHERE id=:id"),
                          {"n": count, "start": u["ventana_fallos_desde"] if count > 1 else now, "id": u["id"]})
                if count >= 5:
                    c.execute(text("UPDATE usuario SET estado='bloqueado',bloqueado_hasta=:until WHERE id=:id"), {"id": u["id"], "until": now+timedelta(minutes=15)})
                    self.revoke(c, u["id"])
                failure = (401, "credenciales_invalidas", INVALID)
            else:
                if self.hasher.check_needs_rehash(u["clave_hash"]):
                    c.execute(text("UPDATE usuario SET clave_hash=:hash WHERE id=:id"), {"id": u["id"], "hash": self.hasher.hash(password)})
                if old_token:
                    c.execute(text("UPDATE sesion SET revocada_en=:now WHERE token_hash=:hash AND usuario_id=:uid"), {"now": now, "hash": digest(old_token), "uid": u["id"]})
                token = secrets.token_urlsafe(32)
                c.execute(text("INSERT INTO sesion(id,usuario_id,token_hash,auth_epoch_emitido,ultimo_uso_en,expira_en) VALUES (:id,:uid,:hash,:epoch,:now,:expiry)"),
                          {"id": uuid4(), "uid": u["id"], "hash": digest(token), "epoch": u["auth_epoch"], "now": now, "expiry": now+timedelta(hours=8)})
                c.execute(text("UPDATE usuario SET fallos_login=0,ventana_fallos_desde=NULL WHERE id=:id"), {"id": u["id"]})
                self.audit(c, u["id"], "login")
                profile = {k: str(u[k]) for k in ("id", "correo", "rol")}
        if failure:
            raise AccessError(*failure)
        return token, profile

    @contextmanager
    def authorized(self, token, *, csrf=None, write=False, admin=False, touch=True):
        """Usuario primero, sesión después. El bloqueo dura toda la escritura."""
        with self.engine.begin() as c:
            if not token or len(token) > 128:
                raise AccessError(401, "sesion_invalida", "Ingresá de nuevo.")
            c.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            uid = c.scalar(text("SELECT usuario_id FROM sesion WHERE token_hash=:hash"), {"hash": digest(token)})
            u = c.execute(text("SELECT * FROM usuario WHERE id=:id FOR UPDATE"), {"id": uid}).mappings().first() if uid else None
            s = c.execute(text("SELECT * FROM sesion WHERE token_hash=:hash FOR UPDATE"), {"hash": digest(token)}).mappings().first() if u else None
            now = c.scalar(text("SELECT clock_timestamp()"))
            if not s or u["estado"] != "activo" or s["revocada_en"] or s["auth_epoch_emitido"] != u["auth_epoch"] or s["expira_en"] <= now or s["creado_en"]+timedelta(hours=8) <= now or s["ultimo_uso_en"]+timedelta(minutes=30) <= now:
                raise AccessError(401, "sesion_invalida", "Ingresá de nuevo.")
            if admin and u["rol"] != "administrador":
                raise AccessError(403, "permiso_denegado", "No tenés permiso para esta operación.")
            if write and (not csrf or not hmac.compare_digest(self.csrf(token).encode(), csrf.encode("utf-8"))):
                raise AccessError(403, "csrf_invalido", "Actualizá la sesión y reintentá.")
            if touch:
                c.execute(text("UPDATE sesion SET ultimo_uso_en=:now WHERE id=:id"), {"id": s["id"], "now": now})
            yield c, u, s

    def logout(self, token, csrf):
        with self.authorized(token, csrf=csrf, write=True) as (c, u, s):
            c.execute(text("UPDATE sesion SET revocada_en=clock_timestamp() WHERE id=:id"), {"id": s["id"]})

    def change_password(self, token, csrf, current, new):
        password_policy(new)
        with self.authorized(token, csrf=csrf, write=True) as (c, u, s):
            if not self.verify(u["clave_hash"], current):
                raise AccessError(401, "credenciales_invalidas", INVALID)
            c.execute(text("UPDATE usuario SET clave_hash=:hash WHERE id=:id"), {"id": u["id"], "hash": self.hasher.hash(new)})
            self.revoke(c, u["id"])
            c.execute(text("UPDATE recuperacion_acceso SET usado_en=clock_timestamp() WHERE usuario_id=:id AND usado_en IS NULL"), {"id": u["id"]})
            self.audit(c, u["id"], "cambio_clave")

    def recover(self, correo):
        with self.engine.begin() as c:
            u = c.execute(text("SELECT * FROM usuario WHERE correo=:email FOR UPDATE"), {"email": correo}).mappings().first()
            if not u or u["estado"] != "activo":
                return
            token = secrets.token_urlsafe(32)
            now = c.scalar(text("SELECT clock_timestamp()"))
            message = EmailMessage()
            message["From"], message["To"], message["Subject"] = self.settings.mail_from, correo, "Recuperar acceso — Entrenador de Prompts"
            message.set_content("El enlace vence en 15 minutos y sólo se puede usar una vez.\n" + self.settings.public_origin + "/#restablecer=" + token + "\nSi no lo solicitaste, ignorá este correo.")
            # El fragmento no viaja en solicitudes HTTP ni en logs de acceso.
            try:
                with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=5) as smtp:
                    if self.settings.smtp_starttls:
                        import ssl
                        smtp.starttls(context=ssl.create_default_context())
                    if self.settings.smtp_user:
                        smtp.login(self.settings.smtp_user, self.settings.smtp_password.get_secret_value())
                    smtp.send_message(message)
            except (OSError, smtplib.SMTPException):
                self.audit(c, None, "correo_no_disponible")
                return  # Respuesta genérica también ante fallo del SMTP, sin token activo.
            c.execute(text("INSERT INTO recuperacion_acceso(id,usuario_id,token_hash,expira_en) VALUES (:id,:uid,:hash,:expiry)"),
                      {"id": uuid4(), "uid": u["id"], "hash": digest(token), "expiry": now+timedelta(minutes=15)})

    def reset(self, token, password):
        password_policy(password)
        with self.engine.begin() as c:
            uid = c.scalar(text("SELECT usuario_id FROM recuperacion_acceso WHERE token_hash=:hash"), {"hash": digest(token)})
            u = c.execute(text("SELECT * FROM usuario WHERE id=:id FOR UPDATE"), {"id": uid}).mappings().first() if uid else None
            r = c.execute(text("SELECT * FROM recuperacion_acceso WHERE token_hash=:hash FOR UPDATE"), {"hash": digest(token)}).mappings().first() if u else None
            now = c.scalar(text("SELECT clock_timestamp()"))
            if not r or r["usado_en"] or r["expira_en"] <= now or u["estado"] != "activo":
                raise AccessError(400, "recuperacion_invalida", RESET_INVALID)
            c.execute(text("UPDATE usuario SET clave_hash=:hash,fallos_login=0,ventana_fallos_desde=NULL WHERE id=:id"), {"id": uid, "hash": self.hasher.hash(password)})
            c.execute(text("UPDATE recuperacion_acceso SET usado_en=:now WHERE usuario_id=:id AND usado_en IS NULL"), {"id": uid, "now": now})
            self.revoke(c, uid)
            self.audit(c, uid, "restablecimiento")

    def set_state(self, token, csrf, target, state, reason):
        if state not in {"activo", "bloqueado", "desactivado"} or reason not in {"seguridad", "solicitud_titular", "incumplimiento", "correccion"}:
            raise AccessError(422, "entrada_invalida", "Estado o motivo inválido.")
        # Orden global por UUID para dos administradores que se bloqueen entre sí.
        with self.engine.begin() as c:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':ADMIN_LOCK})
            actor = c.scalar(text("SELECT usuario_id FROM sesion WHERE token_hash=:hash"), {"hash": digest(token or "")})
            ids = sorted({str(actor), str(target)}) if actor else [str(target)]
            for uid in ids:
                c.execute(text("SELECT id FROM usuario WHERE id=CAST(:id AS uuid) FOR UPDATE"), {"id": uid})
            with self._authorized_on_connection(c, token, csrf) as admin:
                u = c.execute(text("SELECT * FROM usuario WHERE id=:id"), {"id": target}).mappings().first()
                if not u:
                    raise AccessError(404, "no_encontrado", "Recurso no encontrado.")
                if u["rol"] == "administrador" and state != "activo":
                    remaining=c.scalar(text("SELECT count(*) FROM usuario WHERE rol='administrador' AND estado='activo' AND id<>:id"),{'id':target})
                    if not remaining:
                        raise AccessError(409, "administrador_protegido", "No se puede restringir al último administrador habilitado. Contactá al responsable técnico.")
                c.execute(text("UPDATE usuario SET estado=:state,bloqueado_hasta=NULL,fallos_login=0,ventana_fallos_desde=NULL,actualizado_en=clock_timestamp() WHERE id=:id"), {"state": state, "id": target})
                if state != "activo":
                    self.revoke(c, target)
                self.audit(c, admin["id"], "estado_" + state, target, reason)

    @contextmanager
    def _authorized_on_connection(self, c, token, csrf, *, admin=True):
        # Reutilizar la misma transacción y el mismo guard, sin commit intermedio.
        class BoundEngine:
            @contextmanager
            def begin(self):
                yield c
        service = object.__new__(AccessService)
        service.engine, service.key = BoundEngine(), self.key
        with service.authorized(token, csrf=csrf, write=True, admin=admin) as (_, user, session):
            yield user

    @staticmethod
    def owned(c, user, resource, resource_id):
        """Política común para futuros endpoints; administrador no evita propiedad."""
        queries = {
            "practica": "SELECT p.* FROM practica p WHERE p.id=:id AND p.usuario_id=:uid",
            "version": "SELECT v.* FROM version_prompt v JOIN practica p ON p.id=v.practica_id WHERE v.id=:id AND p.usuario_id=:uid",
        }
        result = c.execute(text(queries[resource]), {"id": resource_id, "uid": user["id"]}).mappings().first()
        if result is None:
            raise AccessError(404, "no_encontrado", "Recurso no encontrado.")
        return result
