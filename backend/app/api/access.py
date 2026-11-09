from __future__ import annotations

import re
from email.errors import HeaderParseError
from email.headerregistry import Address
from uuid import UUID, uuid4

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from sqlalchemy import text

from app.application.access import AccessError, RECOVERY, REGISTRATION


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True, str_strip_whitespace=False)


class Email(Input):
    correo: str = Field(max_length=254, strict=True)

    @field_validator("correo")
    @classmethod
    def valid_email(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Formato de correo inválido")
        try:
            address = Address(addr_spec=value)
            if address.addr_spec != value or not address.username or not address.domain:
                raise ValueError("Formato de correo inválido")
        except (ValueError, HeaderParseError):
            raise ValueError("Formato de correo inválido") from None
        return value


class Credentials(Email):
    password: SecretStr = Field(min_length=1, max_length=128, repr=False)


class Reset(Input):
    token: SecretStr = Field(min_length=1, max_length=128, repr=False)
    password_nueva: SecretStr = Field(min_length=1, max_length=128, repr=False)


class PasswordChange(Input):
    password_actual: SecretStr = Field(min_length=1, max_length=128, repr=False)
    password_nueva: SecretStr = Field(min_length=1, max_length=128, repr=False)


class StateChange(Input):
    estado: str
    motivo: str

    @field_validator("estado")
    @classmethod
    def valid_state(cls, value):
        if value not in {"activo", "bloqueado", "desactivado"}:
            raise ValueError("Estado inválido")
        return value

    @field_validator("motivo")
    @classmethod
    def valid_reason(cls, value):
        if value not in {"solicitud_titular", "seguridad", "incumplimiento", "correccion"}:
            raise ValueError("Motivo inválido")
        return value


def token(request):
    return request.cookies.get(request.app.state.settings.session_cookie_name)


def csrf(request):
    return request.headers.get("x-csrf-token")


def limited(request, scope, maximum):
    ip = request.client.host if request.client else "unknown"
    # No confiar en X-Forwarded-For de clientes. Proxy confiable se configura al desplegar.
    if not request.app.state.access.rate(scope, ip, maximum):
        raise AccessError(429, "limite_solicitudes", "Demasiados intentos. Esperá 15 minutos y reintentá.")


router = APIRouter()


@router.post("/auth/registro", status_code=202)
def register(data: Credentials, request: Request):
    limited(request, "registro", 10)
    request.app.state.access.register(data.correo, data.password.get_secret_value())
    return {"message": REGISTRATION}


@router.post("/auth/login")
def login(data: Credentials, request: Request, response: Response):
    limited(request, "login", 20)
    new_token, profile = request.app.state.access.login(data.correo, data.password.get_secret_value(), token(request))
    settings = request.app.state.settings
    response.set_cookie(settings.session_cookie_name, new_token, httponly=True,
                        secure=settings.session_cookie_secure, samesite="lax", path="/", max_age=28800)
    return profile


@router.post("/auth/logout", status_code=204)
def logout(request: Request):
    request.app.state.access.logout(token(request), csrf(request))
    response = Response(status_code=204)
    response.delete_cookie(request.app.state.settings.session_cookie_name, path="/")
    return response


@router.get("/auth/me")
def me(request: Request):
    with request.app.state.access.authorized(token(request),touch=request.headers.get("x-session-probe")!="1") as (c, u, s):
        return {k: str(u[k]) for k in ("id", "correo", "rol")}


@router.get("/auth/csrf")
def get_csrf(request: Request):
    with request.app.state.access.authorized(token(request)):
        return {"csrf_token": request.app.state.access.csrf(token(request))}


@router.post("/auth/recuperacion", status_code=202)
def recover(data: Email, request: Request):
    limited(request, "recuperacion", 5)
    service = request.app.state.access
    if service.rate("recuperacion_cuenta", data.correo, 3):
        service.recover(data.correo)
    return {"message": RECOVERY}


@router.post("/auth/restablecer", status_code=204)
def reset(data: Reset, request: Request):
    limited(request, "restablecer", 10)
    request.app.state.access.reset(data.token.get_secret_value(), data.password_nueva.get_secret_value())
    response = Response(status_code=204)
    response.delete_cookie(request.app.state.settings.session_cookie_name, path="/")
    return response


@router.post("/cuenta/cambiar-clave", status_code=204)
def change_password(data: PasswordChange, request: Request):
    limited(request, "cambiar_clave", 5)
    request.app.state.access.change_password(token(request), csrf(request), data.password_actual.get_secret_value(), data.password_nueva.get_secret_value())
    response = Response(status_code=204)
    response.delete_cookie(request.app.state.settings.session_cookie_name, path="/")
    return response


@router.get("/admin/cuentas")
def list_accounts(request: Request, limit: int = 20, cursor: UUID | None = None):
    if not 1 <= limit <= 100:
        raise AccessError(422, "entrada_invalida", "El límite debe estar entre 1 y 100.")
    with request.app.state.access.authorized(token(request), admin=True) as (c, u, s):
        rows = c.execute(text("SELECT id,correo,rol,estado FROM usuario WHERE (CAST(:cursor AS uuid) IS NULL OR id>CAST(:cursor AS uuid)) ORDER BY id LIMIT :limit"),
                         {"cursor": str(cursor) if cursor else None, "limit": limit+1}).mappings().all()
        return {"items": [dict(r) for r in rows[:limit]], "next_cursor": str(rows[limit-1]["id"]) if len(rows)>limit else None}


@router.post("/admin/cuentas/{user_id}/estado", status_code=204)
def change_state(user_id: UUID, data: StateChange, request: Request):
    request.app.state.access.set_state(token(request), csrf(request), user_id, data.estado, data.motivo)
    return Response(status_code=204)


def error_response(request, status, code, message):
    from fastapi.responses import JSONResponse
    response = JSONResponse({"error": {"code": code, "message": message, "fields": [], "request_id": str(uuid4())}}, status_code=status)
    response.headers["Cache-Control"] = "no-store"
    if status == 401:
        response.delete_cookie(request.app.state.settings.session_cookie_name, path="/")
    return response
