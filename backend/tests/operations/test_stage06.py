"""Verificación final: migración realmente vacía e INT-05 completo en bases ficticias."""
import hashlib
import json
import secrets
from uuid import uuid4
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from app.core.config import Settings,ROOT_DIR
from app.db.seed import seed_initial_data
from app.operations.backups import database_engine,migrate_isolated,backup,restore
from test_backups import setup_settings,client


def test_migrations_from_empty_isolated_schema_and_seed_without_overwrites():
    s=Settings();database='entrenador_prompts_restore_test';engine=database_engine(s,database)
    try:
        with engine.begin() as c:
            assert c.scalar(text('SELECT current_database()'))==database
            assert c.scalar(text('SELECT pg_get_userbyid(datdba)=current_user FROM pg_database WHERE datname=current_database()'))
            c.execute(text('REVOKE CONNECT ON DATABASE '+database+' FROM PUBLIC,entrenador_app'))
            assert not c.scalar(text('SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid()'))
            tables=set(c.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).scalars())
            permitted={'usuario','desafio','criterio','desafio_criterio','regla','practica','version_prompt','evaluacion','resultado','alerta_sensible','sesion','recuperacion_acceso','evento_auditoria','limite_solicitud','alembic_version'}
            assert tables<=permitted
            if 'usuario' in tables:assert c.scalar(text('SELECT count(*) FROM usuario'))==0
            if 'practica' in tables:assert c.scalar(text('SELECT count(*) FROM practica'))==0
            c.execute(text('DROP SCHEMA public CASCADE'))
            c.execute(text('CREATE SCHEMA public AUTHORIZATION entrenador_migracion'))
            assert c.scalar(text("SELECT count(*) FROM pg_tables WHERE schemaname='public'"))==0
            config=Config(str(ROOT_DIR/'backend/alembic.ini'));config.attributes['connection']=c
            command.upgrade(config,'head')
            c.exec_driver_sql((ROOT_DIR/'scripts/permisos_ejecucion_acceso.sql').read_text(encoding='utf-8'))
            assert c.scalar(text("SELECT has_table_privilege('entrenador_app','usuario','INSERT')"))
            assert not c.scalar(text("SELECT has_schema_privilege('entrenador_app','public','CREATE')"))
            assert c.scalar(text('SELECT version_num FROM alembic_version'))=='20261107_0004'
            assert c.scalar(text("SELECT count(*) FROM pg_tables WHERE schemaname='public'"))==15
            def snapshot():
                return {table:sorted(json.dumps(dict(r),default=str,sort_keys=True) for r in c.execute(text('SELECT * FROM '+table)).mappings()) for table in ('criterio','regla','desafio','desafio_criterio')}
            seed_initial_data(c);first=snapshot();seed_initial_data(c);assert snapshot()==first
            assert [len(first[t]) for t in ('criterio','regla','desafio','desafio_criterio')]==[6,6,4,24]
    finally:engine.dispose()


def test_int05_complete_objective_confirmation_delete_backup_restore(tmp_path):
    s,journal=setup_settings(tmp_path);source='entrenador_prompts_ops_test';target='entrenador_prompts_restore_test'
    migrate_isolated(s,source);owner=database_engine(s,source)
    email='int05-'+str(uuid4())+'@example.invalid';password=secrets.token_urlsafe(32);uid=None
    actual={}
    try:
        with client(s,source) as api:
            api.app.state.access.register(email,password)
            with owner.connect() as c:uid=c.scalar(text('SELECT id FROM usuario WHERE correo=:mail'),{'mail':email})
            headers={'Origin':s.public_origin}
            assert api.post('/api/v1/auth/login',json={'correo':email,'password':password},headers=headers).status_code==200
            headers['X-CSRF-Token']=api.get('/api/v1/auth/csrf').json()['csrf_token']
            entry={'modo':'guiado','objetivo':'Preparar consulta para persona@example.invalid','aplicabilidad':{'C2':False,'C3':False,'C4':False}}
            preview=api.post('/api/v1/practicas/preparar',json=entry,headers=headers).json();assert preview['coincidencias']
            data={**entry,'token_inicio':preview['token_inicio'],'request_id':str(uuid4()),'coincidencias_confirmadas':[]}
            assert api.post('/api/v1/practicas',json=data,headers=headers).status_code==409
            with owner.connect() as c:actual['sin_confirmar_no_persiste']=c.scalar(text('SELECT count(*) FROM practica WHERE usuario_id=:id'),{'id':uid})==0
            data['coincidencias_confirmadas']=[m['clave'] for m in preview['coincidencias']]
            response=api.post('/api/v1/practicas',json=data,headers=headers);assert response.status_code==201
            pid=response.json()['id'];manifest=backup(s,source)
            assert api.request('DELETE','/api/v1/practicas/'+pid,json={},headers=headers).status_code==204
        restore(s,manifest,target)
        with client(s,target) as api:
            assert api.post('/api/v1/auth/login',json={'correo':email,'password':password},headers={'Origin':s.public_origin}).status_code==200
            actual['tras_borrado_no_reaparece']=api.get('/api/v1/practicas/'+pid).status_code==404 and api.get('/api/v1/practicas').json()['items']==[]
        expected=next(c['esperado'] for c in json.loads((ROOT_DIR/'fixtures/integration_cases.json').read_text(encoding='utf-8'))['casos'] if c['id']=='INT-05')
        assert actual==expected
    finally:
        owner.dispose()
        if uid:
            for database in (source,target):
                engine=database_engine(s,database)
                with engine.begin() as c:
                    assert c.scalar(text('SELECT current_database()'))==database
                    c.execute(text('DELETE FROM usuario WHERE id=:id'),{'id':uid})
                engine.dispose()
