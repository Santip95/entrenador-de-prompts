"""Archivo de recuperación separado del dump; identidad age privada siempre aparte."""
from datetime import datetime,timezone
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
from uuid import uuid4
from app.core.config import ROOT_DIR,ConfigurationError
from app.operations.backups import AGE
from app.operations.journal import DeletionJournal

NAMES={'local.env','journal.key','journal.anchor','borrados.fernet','manifest.json'}

def private_directory(path):
    path=Path(path).resolve();path.mkdir(parents=True,exist_ok=True)
    if os.name=='nt':
        import csv
        sid=next(csv.reader(io.StringIO(subprocess.check_output(['whoami','/user','/fo','csv','/nh'],text=True))))[1]
        subprocess.run(['icacls',str(path),'/inheritance:r','/grant:r',f'*{sid}:(OI)(CI)F','*S-1-5-18:(OI)(CI)F'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    else:path.chmod(0o700)
    return path

def safe_destination(settings,destination):
    target=Path(destination).resolve()
    protected=[ROOT_DIR,Path(settings.backup_directory).resolve(),Path(settings.deletion_journal_location).resolve().parent,Path(settings.backup_identity_file).resolve().parent]
    if any(target.is_relative_to(p) or p.is_relative_to(target) for p in protected):
        raise ConfigurationError('Recuperación requiere un directorio separado del repo, copias, diario y claves.')
    return target

def export_configuration(settings,destination,env_file=None):
    target=private_directory(safe_destination(settings,destination));journal=DeletionJournal.settings(settings)
    with journal.locked():
        journal._read()
        files={'local.env':Path(env_file or ROOT_DIR/'.env').read_bytes(),'journal.key':journal.key_file.read_bytes(),'journal.anchor':journal.anchor.read_bytes(),'borrados.fernet':journal.path.read_bytes()}
        if sum(map(len,files.values()))>16*1024*1024:raise ConfigurationError('El paquete supera el límite de recuperación de 16 MiB; no se trunca.')
        manifest={'formato':1,'fecha_utc':datetime.now(timezone.utc).isoformat(),'archivos':{name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in files.items()},'limite':'Estado del diario en la fecha de exportacion; para restaurar se exige el diario independiente mas reciente. Identidad privada age NO incluida.'}
        files['manifest.json']=json.dumps(manifest).encode()
        buf=io.BytesIO()
        with tarfile.open(fileobj=buf,mode='w') as archive:
            for name,raw in files.items():
                info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o600;archive.addfile(info,io.BytesIO(raw))
        path=target/('tfg-config-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid4().hex+'.age')
        r=subprocess.run([str(AGE),'-r',settings.backup_encryption_recipient,'-o',str(path)],input=buf.getvalue(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        if r.returncode:raise ConfigurationError('No se pudo cifrar el paquete de recuperación.')
    verify_configuration(settings,path)
    return path

def contents(settings,path):
    if Path(path).stat().st_size>18*1024*1024:raise ConfigurationError('El archivo cifrado supera el límite de recuperación.')
    r=subprocess.run([str(AGE),'-d','-i',settings.backup_identity_file,str(path)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    if r.returncode or len(r.stdout)>17*1024*1024:raise ConfigurationError('Paquete de recuperación no verificable.')
    files={}
    with tarfile.open(fileobj=io.BytesIO(r.stdout),mode='r:') as archive:
        for member in archive:
            if member.name not in NAMES or not member.isfile() or member.name in files or member.size>16*1024*1024:raise ConfigurationError('Contenido de recuperación no permitido.')
            files[member.name]=archive.extractfile(member).read()
    if set(files)!=NAMES:raise ConfigurationError('Paquete de recuperación incompleto.')
    manifest=json.loads(files['manifest.json'])
    if manifest['formato']!=1 or set(manifest['archivos'])!=NAMES-{'manifest.json'}:raise ConfigurationError('Manifiesto de recuperación inválido.')
    for name,info in manifest['archivos'].items():
        if len(files[name])!=info['bytes'] or hashlib.sha256(files[name]).hexdigest()!=info['sha256']:raise ConfigurationError('Integridad de recuperación incorrecta.')
    return files,manifest

def verify_configuration(settings,path):
    _,manifest=contents(settings,path)
    return {'formato':manifest['formato'],'archivos_verificados':4,'fecha_utc':manifest['fecha_utc'],'identidad_age_incluida':False,'limite':'No habilita servicio ni prueba vigencia del diario frente a borrados posteriores.'}

def extract_configuration(settings,path,destination):
    target=safe_destination(settings,destination)
    if target.exists() and any(target.iterdir()):raise ConfigurationError('Extraer sólo en un directorio nuevo o vacío; no sobrescribir configuración activa.')
    files,_=contents(settings,path);target=private_directory(target)
    for name,raw in files.items():
        with (target/name).open('xb') as handle:handle.write(raw);handle.flush();os.fsync(handle.fileno())
    # Comprobar también el diario extraído; identidad age permanece separada.
    check=DeletionJournal(target/'journal-state/borrados.fernet',target/'journal.key',target/'journal.anchor')
    (target/'journal-state').mkdir();(target/'borrados.fernet').replace(check.path)
    check.entries()
    return {'archivos_recuperados':4,'activo_modificado':False,'apertura_automatica':False}
