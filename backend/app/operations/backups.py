"""pg_dump/age y restauración cerrada por defecto en destinos ficticios explícitos."""
from datetime import datetime,timezone,timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from uuid import UUID,uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from cryptography.fernet import Fernet
from app.core.config import ROOT_DIR, ConfigurationError
from app.operations.journal import DeletionJournal,JournalError,atomic
from app.scripts.manage_access import invalidate_all
from app.db.seed import seed_initial_data

SOURCE_DATABASES={'entrenador_prompts','entrenador_prompts_test','entrenador_prompts_ops_test','entrenador_prompts_demo'}
RESTORE_DATABASES={'entrenador_prompts_restore_test','entrenador_prompts_contingencia_test'}
SCHEMA='20261107_0004'
CLIENT=Path('C:/Program Files/PostgreSQL/18/bin')
AGE=ROOT_DIR/'local-data/age/age.exe'


def database_engine(settings,database):
    if database not in SOURCE_DATABASES|RESTORE_DATABASES:
        raise ConfigurationError('Destino fuera de las bases explícitas del proyecto.')
    return create_engine(make_url(settings.resolved_migration_url()).set(database=database),hide_parameters=True)


def migrate_isolated(settings,database):
    if database not in {'entrenador_prompts_test','entrenador_prompts_ops_test','entrenador_prompts_demo'}:
        raise ConfigurationError('La preparación requiere una base de pruebas explícita.')
    engine=database_engine(settings,database)
    try:
        with engine.begin() as c:
            if c.scalar(text('SELECT current_database()'))!=database:
                raise ConfigurationError('La conexión no corresponde al destino autorizado.')
            c.execute(text('REVOKE CREATE ON SCHEMA public FROM PUBLIC'))
            c.execute(text('REVOKE TEMP ON DATABASE '+database+' FROM PUBLIC'))
            c.execute(text('GRANT USAGE ON SCHEMA public TO entrenador_app'))
            config=Config(str(ROOT_DIR/'backend/alembic.ini'));config.attributes['connection']=c
            command.upgrade(config,'head')
            seed_initial_data(c)
            c.execute(text('GRANT SELECT ON ALL TABLES IN SCHEMA public TO entrenador_app'))
            c.execute(text('GRANT INSERT,UPDATE,DELETE ON usuario,sesion,recuperacion_acceso,evento_auditoria,limite_solicitud TO entrenador_app'))
    finally: engine.dispose()


def pg_environment(settings):
    env=os.environ.copy()
    env['PGPASSWORD']=settings.migration_password.get_secret_value()
    env['PGCONNECT_TIMEOUT']='10'
    return env


def connection_args(settings,database):
    if settings.postgres_host!='127.0.0.1' or settings.postgres_port!=5432:
        raise ConfigurationError('La operación local exige 127.0.0.1:5432.')
    return ['--host=127.0.0.1','--port=5432','--username=entrenador_migracion','--dbname='+database,'--no-password']


def directory(settings):
    if not settings.backup_directory:
        raise ConfigurationError('Falta BACKUP_DIRECTORY.')
    path=Path(settings.backup_directory).resolve()
    if not path.is_dir() or path.is_relative_to(ROOT_DIR) or path.is_symlink():
        raise ConfigurationError('Usar un destino privado existente fuera del repositorio.')
    for key in (settings.backup_identity_file,settings.deletion_journal_key_file,settings.deletion_journal_anchor_file):
        if not key or Path(key).resolve().is_relative_to(path):
            raise ConfigurationError('Las claves y el ancla deben estar separados del destino de copias.')
    return path


def pipeline(first,second,*,env=None):
    creation=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    p=subprocess.Popen(first,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,creationflags=creation)
    try:
        q=subprocess.Popen(second,stdin=p.stdout,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=creation,env=env)
        p.stdout.close()
        try:
            status=q.wait(timeout=300)
            parent=p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            q.kill();q.wait();p.kill();p.wait()
            raise ConfigurationError('La operación excedió el tiempo permitido.') from None
        if status or parent:
            raise ConfigurationError('Falló pg_dump/pg_restore/age; no se habilita la copia ni el acceso.')
    finally:
        if p.poll() is None: p.kill();p.wait()


def backup(settings,database):
    if database not in SOURCE_DATABASES:
        raise ConfigurationError('Origen no autorizado.')
    target=directory(settings)
    journal=DeletionJournal.settings(settings)
    journal.entries() # No generar una copia operacional si el diario no es verificable.
    engine=database_engine(settings,database)
    try:
        with engine.connect() as c:
            schema=c.scalar(text('SELECT version_num FROM alembic_version'))
    finally: engine.dispose()
    stamp=datetime.now(timezone.utc)
    identifier='tfg-'+stamp.strftime('%Y%m%dT%H%M%S')+'-'+uuid4().hex
    encrypted=target/(identifier+'.backup.age')
    temporary=target/(identifier+'.partial')
    try:
        pipeline([str(CLIENT/'pg_dump.exe'),*connection_args(settings,database),'--format=custom'],[str(AGE),'-r',settings.backup_encryption_recipient,'-o',str(temporary)],env=pg_environment(settings))
        if not temporary.stat().st_size:
            raise ConfigurationError('Copia vacía.')
        # Validación real del archivo personalizado; no guardar dump en claro.
        # --list cierra antes de EOF y no verifica el cuerpo completo de age.
        # Reconstruir SQL al dispositivo nulo consume/verifica TODO el archivo.
        pipeline([str(AGE),'-d','-i',settings.backup_identity_file,str(temporary)],[str(CLIENT/'pg_restore.exe'),'--file='+os.devnull])
        os.replace(temporary,encrypted)
        manifest={'formato':1,'fecha_utc':stamp.isoformat(),'app_version':'0.5.0','schema_version':schema,'origen':database,'archivo':encrypted.name,'bytes':encrypted.stat().st_size,'sha256':hashlib.sha256(encrypted.read_bytes()).hexdigest()}
        public=json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()
        atomic(target/(identifier+'.manifest.json'),public)
        # Autenticación del manifiesto con la receta mantenida Fernet.
        atomic(target/(identifier+'.manifest.auth'),Fernet(Path(settings.deletion_journal_key_file).read_bytes()).encrypt(public))
        return target/(identifier+'.manifest.json')
    finally: temporary.unlink(missing_ok=True)


def verify_manifest(settings,path):
    root=directory(settings)
    path=Path(path).resolve()
    if path.parent!=root or not path.name.startswith('tfg-') or not path.name.endswith('.manifest.json') or path.is_symlink():
        raise ConfigurationError('Manifiesto fuera del destino configurado.')
    raw=path.read_bytes()
    auth=path.with_name(path.name.replace('.manifest.json','.manifest.auth')).read_bytes()
    if Fernet(Path(settings.deletion_journal_key_file).read_bytes()).decrypt(auth)!=raw:
        raise ConfigurationError('Manifiesto no auténtico.')
    info=json.loads(raw)
    archive=root/info['archivo']
    if archive.parent!=root or archive.is_symlink() or archive.suffix!='.age' or archive.stat().st_size!=info['bytes'] or hashlib.sha256(archive.read_bytes()).hexdigest()!=info['sha256']:
        raise ConfigurationError('Copia no verificable.')
    if datetime.fromisoformat(info['fecha_utc'])>datetime.now(timezone.utc)+timedelta(minutes=5):
        raise ConfigurationError('Fecha de copia inválida.')
    return info,archive


def replay(c,entries):
    # Pendientes y completados: una solicitud durable basta para reaplicar.
    for entry in entries:
        if entry['tipo']=='cuenta':
            c.execute(text('DELETE FROM usuario WHERE id=:id'),{'id':UUID(entry['recurso_id'])})
        elif entry['tipo']=='practica':
            c.execute(text('DELETE FROM practica WHERE id=:id AND usuario_id=:uid'),{'id':UUID(entry['recurso_id']),'uid':UUID(entry['titular_id'])})


def restore(settings,manifest,database):
    if database not in RESTORE_DATABASES:
        raise ConfigurationError('Restaurar sólo en entrenador_prompts_restore_test o entrenador_prompts_contingencia_test.')
    start=time.perf_counter()
    engine=database_engine(settings,database)
    opened=False
    try:
        # COMMIT separado: un fallo posterior no revierte el cierre de CONNECT.
        with engine.begin() as c:
            if c.scalar(text('SELECT current_database()'))!=database:
                raise ConfigurationError('Destino incorrecto.')
            c.execute(text('REVOKE CONNECT ON DATABASE '+database+' FROM PUBLIC,entrenador_app'))
        with engine.connect() as c:
            if c.scalar(text('SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid()')):
                raise ConfigurationError('Cerrar primero todas las conexiones al destino aislado. Acceso permanece cerrado.')
        journal=DeletionJournal.settings(settings)
        # Mantener diario bloqueado hasta COMMIT y reapertura: no perder solicitudes concurrentes.
        with journal.locked():
            entries=journal._read()['entries']
            info,archive=verify_manifest(settings,manifest)
            pipeline([str(AGE),'-d','-i',settings.backup_identity_file,str(archive)],[str(CLIENT/'pg_restore.exe'),*connection_args(settings,database),'--clean','--if-exists','--exit-on-error'],env=pg_environment(settings))
            with engine.begin() as c:
                replay(c,entries)
                invalidate_all(c)
                if c.scalar(text('SELECT version_num FROM alembic_version'))!=info['schema_version']:
                    raise ConfigurationError('Versión restaurada no coincide.')
                incomplete=c.scalar(text('SELECT count(*) FROM version_prompt v LEFT JOIN evaluacion e ON e.version_id=v.id WHERE e.id IS NULL OR (SELECT count(*) FROM resultado r WHERE r.evaluacion_id=e.id)<>6'))
                if incomplete: raise ConfigurationError('Historial incompleto; no abrir acceso.')
                for entry in entries:
                    table='usuario' if entry['tipo']=='cuenta' else 'practica'
                    if c.scalar(text('SELECT EXISTS(SELECT FROM '+table+' WHERE id=:id)'),{'id':entry['recurso_id']}):
                        raise ConfigurationError('Reaplicación incompleta; no abrir acceso.')
                c.execute(text('GRANT CONNECT ON DATABASE '+database+' TO entrenador_app'))
                opened=True
        elapsed=time.perf_counter()-start
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(info['fecha_utc'])).total_seconds()
        return {'destino':database,'integridad':True,'borrados_reaplicados':len(entries),'sesiones_invalidadas':True,'duracion_segundos':round(elapsed,3),'antiguedad_copia_segundos':round(age,3),'objetivo_rto_local':elapsed<=14400,'objetivo_rpo_local':age<=86400,'acceso_habilitado':opened,'limite':'Ensayo local; no acredita continuidad ni restauración externa.'}
    finally: engine.dispose()


def retained(manifests,now):
    origins={m.get('origen','entrenador_prompts') for m in manifests}
    if len(origins)>1:
        return set().union(*(retained([m for m in manifests if m.get('origen','entrenador_prompts')==origin],now) for origin in origins))
    eligible=sorted([m for m in manifests if now-timedelta(days=30)<=datetime.fromisoformat(m['fecha_utc'])<=now],key=lambda m:m['fecha_utc'],reverse=True)
    days={};weeks={}
    for item in eligible:
        date=datetime.fromisoformat(item['fecha_utc'])
        days.setdefault(date.date(),item)
        weeks.setdefault(date.isocalendar()[:2],item)
    return {m['archivo'] for m in list(days.values())[:7]+list(weeks.values())[:4]}


def purge(settings,now=None):
    root=directory(settings);now=now or datetime.now(timezone.utc)
    manifests=[]
    # Verificar todos antes de borrar nada. No tocar archivos desconocidos.
    for path in root.glob('tfg-*.manifest.json'):
        info,_=verify_manifest(settings,path);manifests.append((path,info))
    keep=retained([m for _,m in manifests],now);removed=0
    for path,info in manifests:
        if info['archivo'] not in keep:
            (root/info['archivo']).unlink()
            path.with_name(path.name.replace('.manifest.json','.manifest.auth')).unlink()
            path.unlink();removed+=1
    # parciales propios abortados: sólo tras 24 h, destino exacto.
    for path in root.glob('tfg-*.partial'):
        if path.is_file() and not path.is_symlink() and datetime.fromtimestamp(path.stat().st_mtime,timezone.utc)<now-timedelta(days=1): path.unlink()
    return {'copias_purgadas':removed,'retenidas':len(keep),'b2_verificado':False}
