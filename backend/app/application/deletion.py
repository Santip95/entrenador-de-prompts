"""Borrado durable de raíces propias; confirmación sólo tras COMMIT y diario."""
from sqlalchemy import text
from app.application.access import AccessError,ADMIN_LOCK
from app.operations.journal import DeletionJournal,JournalError,unavailable

class DeletionService:
    def __init__(self,access,settings):self.access,self.settings=access,settings

    def practice(self,token,csrf,identifier):
        try:
            with self.access.authorized(token,csrf=csrf,write=True) as (c,u,s):
                journal=DeletionJournal.settings(self.settings)
                own=c.scalar(text('SELECT id FROM practica WHERE id=:id AND usuario_id=:uid FOR UPDATE'),{'id':identifier,'uid':u['id']})
                if not own and not any(r['tipo']=='practica' and r['recurso_id']==str(identifier) and r['titular_id']==str(u['id']) for r in journal.entries()):
                    raise AccessError(404,'no_encontrado','Recurso no encontrado.')
                record=journal.request('practica',identifier,u['id'])
                c.execute(text('DELETE FROM practica WHERE id=:id AND usuario_id=:uid'),{'id':identifier,'uid':u['id']})
            journal.complete(record)
        except JournalError:
            raise unavailable() from None

    def account(self,token,csrf,password):
        try:
            with self.access.engine.begin() as c:
                c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':ADMIN_LOCK})
                with self.access._authorized_on_connection(c,token,csrf,admin=False) as u:
                    if not self.access.verify(u['clave_hash'],password):
                        raise AccessError(401,'credenciales_invalidas','No se pudo confirmar la contraseña actual.')
                    if u['rol']=='administrador' and not c.scalar(text("SELECT count(*) FROM usuario WHERE rol='administrador' AND estado='activo' AND id<>:id"),{'id':u['id']}):
                        raise AccessError(409,'administrador_protegido','No se puede eliminar al último administrador habilitado. Contactá al responsable técnico.')
                    journal=DeletionJournal.settings(self.settings)
                    record=journal.request('cuenta',u['id'],u['id'])
                    c.execute(text('DELETE FROM usuario WHERE id=:id'),{'id':u['id']})
            journal.complete(record)
        except JournalError:
            raise unavailable() from None
