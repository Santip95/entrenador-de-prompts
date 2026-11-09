"""Inicialización explícita local: ACL privadas, claves separadas, nunca reemplazar."""
import csv
import io
import os
from pathlib import Path
import subprocess
import sys
from dotenv import dotenv_values
from cryptography.fernet import Fernet

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.operations.journal import DeletionJournal

def main():
    local=dotenv_values(ROOT/'.env')
    state=Path(os.environ['LOCALAPPDATA'])/'EntrenadorPrompts'
    keys=Path(os.environ['LOCALAPPDATA'])/'EntrenadorPromptsKeys'
    dirs=[state/'backups',state/'diario',keys]
    sid=next(csv.reader(io.StringIO(subprocess.check_output(['whoami','/user','/fo','csv','/nh'],text=True))))[1]
    for directory in dirs:
        directory.mkdir(parents=True,exist_ok=True)
        subprocess.run(['icacls',str(directory),'/inheritance:r','/grant:r',f'*{sid}:(OI)(CI)F','*S-1-5-18:(OI)(CI)F'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    identity=Path(local.get('BACKUP_IDENTITY_FILE') or keys/'backup.agekey')
    journal_key=Path(local.get('DELETION_JOURNAL_KEY_FILE') or keys/'journal.key')
    journal_path=Path(local.get('DELETION_JOURNAL_LOCATION') or state/'diario/borrados.fernet')
    anchor=Path(local.get('DELETION_JOURNAL_ANCHOR_FILE') or keys/'journal.anchor')
    backup=Path(local.get('BACKUP_DIRECTORY') or state/'backups')
    for key in (identity,journal_key,anchor):
        if key.resolve().is_relative_to(ROOT) or key.resolve().is_relative_to(backup.resolve()):
            raise SystemExit('Las claves y ancla deben estar fuera del repositorio y destino de copias.')
    age=ROOT/'local-data/age/age-keygen.exe'
    # Si ya había un diario, perder una clave nunca permite generar otra.
    if journal_path.exists() and not journal_key.exists():
        raise SystemExit('Falta la clave de un diario existente: recuperar la original, no reiniciar.')
    if not identity.exists():
        subprocess.run([str(age),'-o',str(identity)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    recipient=subprocess.check_output([str(age),'-y',str(identity)],text=True,stderr=subprocess.DEVNULL).strip()
    if not journal_key.exists():
        with journal_key.open('xb') as handle: handle.write(Fernet.generate_key());handle.flush();os.fsync(handle.fileno())
    journal=DeletionJournal(journal_path,journal_key,anchor)
    journal.initialize()
    values={'BACKUP_DIRECTORY':str(backup),'BACKUP_ENCRYPTION_RECIPIENT':recipient,'BACKUP_IDENTITY_FILE':str(identity),'DELETION_JOURNAL_LOCATION':str(journal_path),'DELETION_JOURNAL_KEY_FILE':str(journal_key),'DELETION_JOURNAL_ANCHOR_FILE':str(anchor)}
    original=(ROOT/'.env').read_text(encoding='utf-8')
    lines=original.splitlines()
    for key,value in values.items():
        if local.get(key): continue
        replacement=key+'='+value.replace('\\','/')
        index=next((i for i,line in enumerate(lines) if line.startswith(key+'=')),None)
        if index is None: lines.append(replacement)
        else: lines[index]=replacement
    (ROOT/'.env').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Preparación local completada: ACL privadas, claves separadas y diario verificado. No se reemplazaron valores existentes.')

if __name__=='__main__': main()
