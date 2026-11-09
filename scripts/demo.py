"""Demo separada: datos ficticios por API, claves aleatorias privadas y arranque Windows."""
from pathlib import Path
import argparse
import json
import os
import secrets
import subprocess
import sys
from uuid import UUID,uuid5
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.core.config import Settings
from app.main import create_app
from app.operations.backups import database_engine,migrate_isolated
from app.operations.configuration_archive import private_directory
from app.scripts.manage_access import promote_admin
from app.application.access import ADMIN_LOCK

DATABASE='entrenador_prompts_demo'
NAMESPACE=UUID('53a94144-a4d8-41da-96c8-8ee199efc370')

def credentials_path():return Path(os.environ['LOCALAPPDATA'])/'EntrenadorPromptsDemo/credenciales.json'

def prepare(settings):
    migrate_isolated(settings,DATABASE);owner=database_engine(settings,DATABASE)
    path=credentials_path();url=make_url(settings.resolved_database_url()).set(database=DATABASE).render_as_string(hide_password=False)
    cfg=settings.model_copy(update={'app_env':'test','database_url':SecretStr(url)})
    runtime=create_engine(url,hide_parameters=True)
    try:
        with owner.connect() as c:
            assert c.scalar(text('SELECT current_database()'))==DATABASE
            assert c.scalar(text('SELECT pg_get_userbyid(datdba)=current_user FROM pg_database WHERE datname=current_database()'))
            if not path.exists() and c.scalar(text("SELECT count(*) FROM usuario WHERE correo IN ('demo.usuario@example.invalid','demo.admin@example.invalid')")):
                raise RuntimeError('Falta el archivo de credenciales de una demo existente; no se reemplazan cuentas.')
        if path.exists():credentials=json.loads(path.read_text(encoding='utf-8'))
        else:
            private_directory(path.parent)
            credentials={role:{'correo':'demo.'+('usuario' if role=='usuario' else 'admin')+'@example.invalid','password':secrets.token_urlsafe(36)} for role in ('usuario','administrador')}
            with path.open('x',encoding='utf-8') as handle:json.dump(credentials,handle)
        with TestClient(create_app(cfg,runtime),raise_server_exceptions=False) as api:
            for role,account in credentials.items():
                api.app.state.access.register(account['correo'],account['password'])
                if role=='administrador':
                    with owner.begin() as c:
                        c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':ADMIN_LOCK})
                        if c.scalar(text('SELECT rol FROM usuario WHERE correo=:mail'),{'mail':account['correo']})=='usuario':
                            promote_admin(c,account['correo'])
            headers={'Origin':settings.public_origin};user=credentials['usuario']
            assert api.post('/api/v1/auth/login',json=user,headers=headers).status_code==200
            headers['X-CSRF-Token']=api.get('/api/v1/auth/csrf').json()['csrf_token']
            challenge=next(r for r in api.get('/api/v1/desafios?limit=100').json()['items'] if r['desafio']['codigo']=='D01_CORREO_REUNION')
            entry={'modo':'guiado','desafio_id':challenge['id']};start=api.post('/api/v1/practicas/preparar',json=entry,headers=headers).json()
            result=api.post('/api/v1/practicas',json={**entry,'token_inicio':start['token_inicio'],'coincidencias_confirmadas':[],'request_id':str(uuid5(NAMESPACE,'practica-correo'))},headers=headers)
            assert result.status_code in (200,201);pid=result.json()['id']
            cases=json.loads((ROOT/'fixtures/evaluation_cases.json').read_text(encoding='utf-8'))['casos']
            for case_id in ('CP-31','CP-01'):
                draft=next(r['entrada'] for r in cases if r['id']==case_id)
                preview=api.post(f'/api/v1/practicas/{pid}/revisar',json=draft,headers=headers).json()
                saved=api.post(f'/api/v1/practicas/{pid}/versiones',json={'borrador':draft,'token_revision':preview['token_revision'],'coincidencias_confirmadas':[m['clave'] for m in preview['coincidencias']],'request_id':str(uuid5(NAMESPACE,'version-'+case_id))},headers=headers)
                assert saved.status_code in (200,201)
            assert len(api.get(f'/api/v1/practicas/{pid}/versiones').json()['items'])>=2
        print('Demo preparada en entrenador_prompts_demo: usuario/administrador ficticios y V1 3/6, V2 6/6. Contraseñas fuera de Git y del informe.')
        print('Abrir únicamente en tu editor local:',path)
    finally:owner.dispose();runtime.dispose()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['preparar','api']);args=parser.parse_args()
    try:
        settings=Settings()
        if args.action=='preparar':prepare(settings)
        else:
            variables=os.environ.copy();variables.update(APP_ENV='test',DATABASE_URL=make_url(settings.resolved_database_url()).set(database=DATABASE).render_as_string(hide_password=False))
            result=subprocess.run([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables)
            raise SystemExit(result.returncode)
    except KeyboardInterrupt:pass
    except Exception:raise SystemExit('No se pudo preparar/iniciar la demo. Revisá base exclusiva, credenciales locales y puertos; no se muestran datos privados.') from None

if __name__=='__main__':main()
