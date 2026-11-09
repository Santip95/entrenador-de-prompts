"""Diario independiente Fernet, escritura durable y bloqueo entre procesos Windows.

El ancla separada detecta reemplazos/truncados. Un corte entre reemplazos deja
el servicio cerrado: requiere conciliación técnica, nunca apertura automática.
"""
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID, uuid4

from cryptography.fernet import Fernet, InvalidToken
from app.application.access import AccessError


class JournalError(Exception):
    pass


def atomic(path, data):
    path=Path(path)
    temp=path.with_name(path.name+'.'+uuid4().hex+'.tmp')
    try:
        with temp.open('xb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        # MOVEFILE_WRITE_THROUGH asegura el reemplazo en Windows.
        if os.name=='nt':
            import ctypes
            if not ctypes.windll.kernel32.MoveFileExW(str(temp),str(path),0x1|0x8):
                raise OSError('No se pudo confirmar el diario')
        else:
            os.replace(temp,path)
            fd=os.open(path.parent,os.O_RDONLY)
            try: os.fsync(fd)
            finally: os.close(fd)
    finally:
        temp.unlink(missing_ok=True)


class DeletionJournal:
    def __init__(self,location,key_file,anchor_file):
        if not location or not key_file or not anchor_file:
            raise JournalError('Falta configurar el diario independiente.')
        self.path,self.key_file,self.anchor=map(lambda p:Path(p).resolve(),(location,key_file,anchor_file))
        if self.path.parent==self.key_file.parent or self.path.parent==self.anchor.parent:
            raise JournalError('El ancla y la clave deben estar separados del diario.')

    @classmethod
    def settings(cls,settings):
        return cls(settings.deletion_journal_location,settings.deletion_journal_key_file,settings.deletion_journal_anchor_file)

    @contextmanager
    def locked(self):
        try:
            # No crea directorios automáticamente ni recrea un diario ausente.
            with self.path.with_suffix('.lock').open('a+b') as handle:
                handle.seek(0)
                handle.write(b'0');handle.flush();handle.seek(0)
                if os.name=='nt':
                    import msvcrt
                    msvcrt.locking(handle.fileno(),msvcrt.LK_LOCK,1)
                else:
                    import fcntl
                    fcntl.flock(handle,fcntl.LOCK_EX)
                try: yield
                finally:
                    handle.seek(0)
                    if os.name=='nt': msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
                    else: fcntl.flock(handle,fcntl.LOCK_UN)
        except (OSError,ValueError,InvalidToken,KeyError,TypeError,json.JSONDecodeError):
            raise JournalError('No se pudo verificar o escribir el diario independiente.') from None

    def _read(self):
        encrypted=self.path.read_bytes()
        digest=hashlib.sha256(encrypted).hexdigest().encode()
        if self.anchor.read_bytes()!=digest:
            raise JournalError('El diario y su ancla no coinciden. Mantener el acceso cerrado.')
        value=json.loads(Fernet(self.key_file.read_bytes()).decrypt(encrypted))
        if set(value)!={'version','entries'} or value['version']!=1 or type(value['entries']) is not list:
            raise JournalError('Formato de diario inválido.')
        for r in value['entries']:
            if set(r)!={'id','tipo','recurso_id','titular_id','fecha','completado_en'} or r['tipo'] not in {'practica','cuenta'}:
                raise JournalError('Registro de diario inválido.')
            for key in ('id','recurso_id','titular_id'): UUID(r[key])
            datetime.fromisoformat(r['fecha'])
            if r['completado_en']: datetime.fromisoformat(r['completado_en'])
        return value

    def _write(self,value):
        encrypted=Fernet(self.key_file.read_bytes()).encrypt(json.dumps(value,separators=(',',':')).encode())
        atomic(self.path,encrypted)
        atomic(self.anchor,hashlib.sha256(encrypted).hexdigest().encode())

    def initialize(self):
        with self.locked():
            if self.path.exists() or self.anchor.exists():
                self._read()  # Nunca reiniciar un diario existente o parcialmente perdido.
            else:
                self._write({'version':1,'entries':[]})

    def entries(self):
        with self.locked(): return self._read()['entries']

    def request(self,kind,resource,owner):
        if kind not in {'practica','cuenta'}: raise JournalError('Tipo inválido.')
        resource,owner=str(UUID(str(resource))),str(UUID(str(owner)))
        with self.locked():
            value=self._read()
            found=next((r for r in value['entries'] if r['tipo']==kind and r['recurso_id']==resource and r['titular_id']==owner),None)
            if found: return found['id']
            identifier=str(uuid4())
            value['entries'].append({'id':identifier,'tipo':kind,'recurso_id':resource,'titular_id':owner,'fecha':datetime.now(timezone.utc).isoformat(),'completado_en':None})
            self._write(value)
            return identifier

    def complete(self,identifier):
        with self.locked():
            value=self._read()
            record=next(r for r in value['entries'] if r['id']==identifier)
            if not record['completado_en']:
                record['completado_en']=datetime.now(timezone.utc).isoformat()
                self._write(value)

    def prune(self,oldest_retained_backup,now=None):
        # Sólo después de purgar/verificar TODAS las copias locales y externas.
        now=now or datetime.now(timezone.utc)
        boundary=min(oldest_retained_backup,now-timedelta(days=30))
        with self.locked():
            value=self._read()
            value['entries']=[r for r in value['entries'] if not r['completado_en'] or datetime.fromisoformat(r['fecha'])>=boundary]
            self._write(value)


def unavailable():
    return AccessError(503,'diario_no_disponible','No se pudo registrar el borrado durable. Reintentá más tarde; no se confirma su eliminación.')
