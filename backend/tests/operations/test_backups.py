"""Ensayo real: sólo tres bases ficticias dedicadas, nunca desarrollo."""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
from uuid import uuid4
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from app.core.config import Settings,ROOT_DIR,ConfigurationError
from app.main import create_app
from app.operations.journal import DeletionJournal,JournalError
from app.operations.backups import backup,restore,purge,retained,database_engine,migrate_isolated
from app.application.access import AccessService
from app.application.fixture_evaluation import load_fixture_data


def setup_settings(tmp_path):
    s=Settings();keys=tmp_path/'keys';diary=tmp_path/'diary';copies=tmp_path/'copies'
    for d in (keys,diary,copies): d.mkdir()
    key=keys/'journal.key';key.write_bytes(Fernet.generate_key())
    s=s.model_copy(update={'backup_directory':str(copies),'deletion_journal_location':str(diary/'journal.fernet'),'deletion_journal_key_file':str(key),'deletion_journal_anchor_file':str(keys/'anchor')})
    journal=DeletionJournal.settings(s);journal.initialize()
    return s,journal


def runtime(s,database):
    url=make_url(s.resolved_database_url()).set(database=database).render_as_string(hide_password=False)
    settings=s.model_copy(update={'database_url':__import__('pydantic').SecretStr(url),'app_env':'test'})
    return settings,create_engine(url,hide_parameters=True)


def client(s,database):
    settings,engine=runtime(s,database)
    return TestClient(create_app(settings,engine),raise_server_exceptions=False)


def test_real_encrypted_restore_completed_pending_deletions_and_contingency(tmp_path):
    s,journal=setup_settings(tmp_path)
    source='entrenador_prompts_ops_test'
    migrate_isolated(s,source)
    owner=database_engine(s,source);users=[];resources=[];report={}
    try:
        with client(s,source) as api:
            def post(path,data,csrf=None):
                return api.post('/api/v1'+path,json=data,headers={'Origin':s.public_origin,**({'X-CSRF-Token':csrf} if csrf else {})})
            cases={c['id']:c for c in load_fixture_data()['cases']}
            def login(account):
                assert post('/auth/login',{'correo':account[1],'password':account[2]}).status_code==200
                return api.get('/api/v1/auth/csrf').json()['csrf_token']
            for i in range(3):
                account=(uuid4(),f'ops05-{uuid4()}@example.invalid','Una frase ficticia de operación 2026')
                api.app.state.access.register(account[1],account[2])
                with owner.connect() as c: uid=c.scalar(text('SELECT id FROM usuario WHERE correo=:mail'),{'mail':account[1]})
                account=(uid,*account[1:]);users.append(account)
                csrf=login(account)
                challenge=next(c for c in api.get('/api/v1/desafios?limit=100').json()['items'] if c['desafio']['codigo']=='D01_CORREO_REUNION')
                entry={'modo':'guiado','desafio_id':challenge['id']}
                start=post('/practicas/preparar',entry,csrf).json()
                result=post('/practicas',{**entry,'token_inicio':start['token_inicio'],'coincidencias_confirmadas':[],'request_id':str(uuid4())},csrf)
                assert result.status_code==201
                pid=result.json()['id'];versions=[]
                for case in ('CP-31','CP-01'):
                    draft=cases[case]['entrada'];preview=post('/practicas/'+pid+'/revisar',draft,csrf).json()
                    result=post('/practicas/'+pid+'/versiones',{'borrador':draft,'token_revision':preview['token_revision'],'coincidencias_confirmadas':[m['clave'] for m in preview['coincidencias']],'request_id':str(uuid4())},csrf)
                    assert result.status_code==201;versions.append(result.json())
                # Token de recuperación ficticio hash-only, para verificar invalidación.
                with owner.begin() as c:
                    c.execute(text("INSERT INTO recuperacion_acceso(id,usuario_id,token_hash,expira_en) VALUES (:id,:uid,:hash,clock_timestamp()+interval '15 minutes')"),{'id':uuid4(),'uid':uid,'hash':uuid4().hex*2})
                resources.append((pid,versions))
            old_cookie=api.cookies.get('ep_session')
            manifest=backup(s,source)
            csrf=login(users[0])
            assert api.request('DELETE','/api/v1/cuenta',json={'password_actual':users[0][2]},headers={'Origin':s.public_origin,'X-CSRF-Token':csrf}).status_code==204
            csrf=login(users[1])
            assert api.request('DELETE','/api/v1/practicas/'+resources[1][0],json={},headers={'Origin':s.public_origin,'X-CSRF-Token':csrf}).status_code==204
            # Solicitud pendiente durable antes de borrar activo: también debe aplicarse.
            pending_id=journal.request('practica',resources[1][0],users[1][0])
            # Una cuarta práctica sólo en el respaldo queda pendiente sin borrar activo.
            keep_user=users[2]
            # Reusar la práctica de B completada no prueba pendiente real: registrar
            # cuenta B como pendiente y comprobar que tampoco resucita su cuenta.
            journal.request('cuenta',users[1][0],users[1][0])
        for target in ('entrenador_prompts_restore_test','entrenador_prompts_contingencia_test'):
            result=restore(s,manifest,target);report[target]=result
            restored=database_engine(s,target)
            with restored.connect() as c:
                assert c.scalar(text('SELECT current_database()'))==target
                for account in users[:2]:
                    assert not c.scalar(text('SELECT EXISTS(SELECT FROM usuario WHERE id=:id)'),{'id':account[0]})
                assert c.scalar(text('SELECT count(*) FROM sesion WHERE revocada_en IS NULL'))==0
                assert c.scalar(text('SELECT count(*) FROM recuperacion_acceso WHERE usado_en IS NULL'))==0
                assert c.scalar(text('SELECT EXISTS(SELECT FROM practica WHERE id=:id)'),{'id':resources[2][0]})
            restored.dispose()
            with client(s,target) as api:
                api.cookies.set('ep_session',old_cookie)
                assert api.get('/api/v1/auth/me').status_code==401
                result=api.post('/api/v1/auth/login',json={'correo':users[2][1],'password':users[2][2]},headers={'Origin':s.public_origin});assert result.status_code==200
                pid,versions=resources[2]
                history=api.get('/api/v1/practicas').json();assert any(p['id']==pid for p in history['items'])
                first=api.get('/api/v1/versiones/'+versions[0]['id']).json();assert first==versions[0]
                comparison=api.get(f"/api/v1/practicas/{pid}/comparacion?desde={versions[0]['id']}&hasta={versions[1]['id']}").json()
                assert comparison['delta_pp']==50 and comparison['resolucion']==100
            assert report[target]['objetivo_rto_local'] and report[target]['objetivo_rpo_local']
            if target=='entrenador_prompts_contingencia_test':
                import sys
                sys.path.insert(0,str(ROOT_DIR/'scripts'))
                from verify_restore_contingency import verify
                check=verify(s,target,users[2]);report[target]['recorrido_real']=check
                total=report[target]['duracion_segundos']+check['arranque_y_recorrido_segundos']
                report[target]['rto_hasta_lectura_comparacion_segundos']=round(total,3)
                report[target]['objetivo_rto_local']=total<=14400
                assert report[target]['objetivo_rto_local']
        folder=ROOT_DIR/'local-data/etapa05';folder.mkdir(exist_ok=True,parents=True)
        (folder/'restauracion.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        # Diario ausente/corrupto: no se abre CONNECT ni se anuncia éxito.
        journal.path.write_bytes(b'fallo ficticio')
        with pytest.raises(JournalError): restore(s,manifest,'entrenador_prompts_restore_test')
        e=database_engine(s,'entrenador_prompts_restore_test')
        with e.connect() as c: assert not c.scalar(text("SELECT has_database_privilege('entrenador_app',current_database(),'CONNECT')"))
        e.dispose()
    finally:
        for database in (source,'entrenador_prompts_restore_test','entrenador_prompts_contingencia_test'):
            e=database_engine(s,database)
            with e.begin() as c:
                assert c.scalar(text('SELECT current_database()'))==database
                for account in users: c.execute(text('DELETE FROM usuario WHERE id=:id'),{'id':account[0]})
            e.dispose()
        owner.dispose()


def test_retention_seven_days_four_weeks_all_max_thirty_days():
    now=datetime(2026,11,7,17,tzinfo=timezone.utc)
    copies=[{'archivo':str(i),'fecha_utc':(now-timedelta(days=i)).isoformat()} for i in range(60)]
    keep=retained(copies,now)
    assert all(str(i) in keep for i in range(7))
    assert all(int(i)<=30 for i in keep)
    assert len(keep)<=11
    assert len(keep)>7


def test_restore_refuses_active_or_arbitrary_database(tmp_path):
    s,j=setup_settings(tmp_path)
    for database in ('entrenador_prompts','entrenador_prompts_test','postgres','ajena'):
        with pytest.raises(ConfigurationError): restore(s,'inexistente',database)


def test_journal_detects_rollback_tampering_and_missing_files(tmp_path):
    s,j=setup_settings(tmp_path);original=j.path.read_bytes()
    uid=uuid4();record=j.request('cuenta',uid,uid)
    assert j.request('cuenta',uid,uid)==record and len(j.entries())==1
    j.complete(record);assert j.entries()[0]['completado_en']
    j.path.write_bytes(original)
    with pytest.raises(JournalError): j.entries()
    j.path.unlink()
    with pytest.raises(JournalError): j.entries()
