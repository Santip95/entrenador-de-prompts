from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import ConfigurationError, get_settings
from app.db.session import build_engine
from app.application.access import AccessError, AccessService
from app.api.access import router, error_response
from app.api.guards import RequestGuards
from app.api.practices import router as practices_router
from app.application.practices import PracticeService
from app.domain.evaluation import EvaluationError
from app.application.administration import AdministrationService
from app.api.administration import router as administration_router
from app.api.deletion import router as deletion_router
from app.application.deletion import DeletionService


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = application.state.settings
    settings.validate_access()
    settings.validate_reviews()
    engine = application.state.engine if hasattr(application.state, "engine") else build_engine(settings)
    try:
        with engine.connect() as connection:
            is_superuser = connection.scalar(text(
                "SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls FROM pg_roles WHERE rolname = current_user"
            ))
            ddl = connection.scalar(text("SELECT has_schema_privilege(current_user,'public','CREATE') OR has_database_privilege(current_user,current_database(),'CREATE') OR has_database_privilege(current_user,current_database(),'TEMP') OR EXISTS (SELECT FROM pg_tables WHERE schemaname='public' AND tableowner=current_user)"))
            memberships = connection.scalar(text("SELECT EXISTS(SELECT FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname=current_user))"))
            if is_superuser or ddl or memberships:
                raise ConfigurationError("La API requiere el rol de ejecución sin propiedad, DDL ni membresías.")
        application.state.access = AccessService(engine, settings)
        application.state.practices = PracticeService(settings)
        application.state.administration = AdministrationService(application.state.practices)
        application.state.deletion = DeletionService(application.state.access,settings)
        yield
    except SQLAlchemyError:
        raise ConfigurationError(
            "No se pudo conectar a PostgreSQL. Revisá el servicio, la base y las credenciales locales."
        ) from None
    finally:
        engine.dispose()


def create_app(settings=None, engine=None):
    settings = settings or get_settings()
    application = FastAPI(title=settings.app_name, lifespan=lifespan,
                         telemetry={"tracing": False, "metrics": False, "auto_configure": False})
    application.state.settings = settings
    if engine is not None:
        application.state.engine = engine
    application.add_middleware(RequestGuards, origin=settings.public_origin)
    application.include_router(router, prefix=settings.api_prefix)
    application.include_router(practices_router, prefix=settings.api_prefix)
    application.include_router(administration_router, prefix=settings.api_prefix)
    application.include_router(deletion_router, prefix=settings.api_prefix)

    @application.exception_handler(EvaluationError)
    async def evaluation_error(request: Request, error: EvaluationError):
        messages={"objetivo_invalido":"El objetivo debe contener entre 1 y 1000 caracteres y no puede estar vacío.","componentes_sin_confirmar":"Confirmá los componentes declarados antes de revisar el texto libre.","limite_excedido":"Revisá los límites: objetivo 1000, cada componente 2000 y prompt 10000 caracteres."}
        return error_response(request,error.status,error.code,messages.get(error.code,str(error)))

    @application.exception_handler(AccessError)
    async def access_error(request: Request, error: AccessError):
        return error_response(request, error.status, error.code, error.message)

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        if any(item["type"] == "json_invalid" for item in error.errors()):
            return error_response(request, 400, "json_invalido", "Enviá un JSON válido.")
        return error_response(request, 422, "entrada_invalida", "Revisá los campos y el formato de la solicitud.")

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        return error_response(request, error.status_code, "solicitud_invalida", "Solicitud no válida o recurso no encontrado.")

    @application.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, error: SQLAlchemyError):
        return error_response(request, 503, "dependencia_no_disponible", "No se pudo completar la operación. Reintentá más tarde.")

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, error: Exception):
        return error_response(request, 500, "error_interno", "No se pudo completar la operación.")

    @application.get("/health", tags=["infraestructura"])
    def healthcheck():
        return {"status": "ok", "service": "api"}

    return application


app = create_app()
