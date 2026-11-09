"""Operación local privilegiada, sin endpoints de cambio de rol ni usuarios seed."""
import argparse
from getpass import getpass
from uuid import uuid4
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.application.access import AccessService, password_policy,ADMIN_LOCK
from app.core.config import ConfigurationError, Settings


def invalidate_all(c):
    c.execute(text("SELECT id FROM usuario ORDER BY id FOR UPDATE"))
    c.execute(text("UPDATE usuario SET auth_epoch=auth_epoch+1"))
    c.execute(text("UPDATE sesion SET revocada_en=clock_timestamp() WHERE revocada_en IS NULL"))
    c.execute(text("UPDATE recuperacion_acceso SET usado_en=clock_timestamp() WHERE usado_en IS NULL"))


def promote_admin(c, email):
    user = c.scalar(text("SELECT id FROM usuario WHERE correo=:email AND estado='activo' FOR UPDATE"), {"email": email.strip().lower()})
    if not user:
        raise ConfigurationError("No existe una cuenta activa con ese correo.")
    c.execute(text("UPDATE usuario SET rol='administrador' WHERE id=:id"), {"id": user})
    AccessService.revoke(c, user)
    AccessService.audit(c, user, "cambio_rol", user)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["crear-admin", "promover-admin", "invalidar-restauracion"])
    parser.add_argument("--correo")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    try:
        settings=Settings()
        engine = create_engine(settings.resolved_migration_url(test=args.test), hide_parameters=True)
        email=None;encoded=None
        if args.action=='crear-admin':
            from app.api.access import Email
            email=Email(correo=input('Correo de la nueva cuenta administradora: ')).correo
            password=getpass('Contraseña nueva (15–128 caracteres, sin eco): ')
            if password!=getpass('Repetir contraseña: '):
                raise ConfigurationError('Las contraseñas no coinciden.')
            password_policy(password)
            encoded=AccessService(engine,settings).hasher.hash(password)
            password=None
        with engine.begin() as c:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':ADMIN_LOCK})
            if args.action == "invalidar-restauracion":
                invalidate_all(c)
            elif args.action=='crear-admin':
                if c.scalar(text('SELECT EXISTS(SELECT FROM usuario WHERE correo=:email)'),{'email':email}):
                    raise ConfigurationError('La cuenta ya existe; no se reemplaza ni se cambia su clave.')
                c.execute(text("INSERT INTO usuario(id,correo,clave_hash,rol) VALUES (:id,:email,:hash,'administrador')"),{'id':uuid4(),'email':email,'hash':encoded})
            else:
                if not args.correo:
                    raise ConfigurationError("Indicar --correo de una cuenta local ya registrada.")
                promote_admin(c, args.correo)
        engine.dispose()
        print("Operación local completada; sesiones anteriores invalidadas.")
    except ConfigurationError as error:
        raise SystemExit(str(error)) from None
    except SQLAlchemyError:
        raise SystemExit("No se pudo completar la operación en PostgreSQL.") from None


if __name__ == "__main__":
    main()
