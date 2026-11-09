"""Etapa 04: endpoints reales, PostgreSQL aislado, expectativas originales."""
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from copy import deepcopy
import base64
import hashlib
import hmac
import json
import threading
from uuid import uuid4, UUID

import pytest
from sqlalchemy import event, text

from app.application.fixture_evaluation import load_fixture_data
from app.application.practices import CATALOG_LOCK
from app.application.access import AccessError
from app.domain.evaluation import canonical

DATA=load_fixture_data()
CASES={case['id']:case for case in DATA['cases']}


def post(env,path,data):
    return env.post(path,data,csrf=env.csrf())


def begin(env,account,*,own=None,mode='guiado'):
    env.login(account)
    if own is None:
        challenge=next(c for c in env.api.get('/api/v1/desafios?limit=100').json()['items'] if c['desafio']['codigo']=='D01_CORREO_REUNION')
        entry={'modo':mode,'desafio_id':challenge['id']}
    else:
        entry={'modo':mode,'objetivo':own,'aplicabilidad':{'C2':False,'C3':False,'C4':False}}
    response=post(env,'/practicas/preparar',entry)
    assert response.status_code==200
    start=response.json()
    creation={**entry,'token_inicio':start['token_inicio'],'coincidencias_confirmadas':[m['clave'] for m in start['coincidencias']],'request_id':str(uuid4())}
    response=post(env,'/practicas',creation)
    assert response.status_code==201
    return response.json(),creation


def review(env,pid,draft):
    r=post(env,f'/practicas/{pid}/revisar',draft)
    assert r.status_code==200
    preview=r.json()
    return {'borrador':deepcopy(draft),'token_revision':preview['token_revision'],'coincidencias_confirmadas':[m['clave'] for m in preview['coincidencias']],'request_id':str(uuid4())},preview


def save(env,pid,draft):
    data,preview=review(env,pid,draft)
    r=post(env,f'/practicas/{pid}/versiones',data)
    assert r.status_code==201
    return r.json(),data


def test_cp12_real_v1_v2_and_history(env,account):
    p,_=begin(env,account)
    first,_=save(env,p['id'],CASES['CP-31']['entrada'])
    second,_=save(env,p['id'],CASES['CP-01']['entrada'])
    original=env.api.get('/api/v1/versiones/'+first['id']).json()
    r=env.api.get(f"/api/v1/practicas/{p['id']}/comparacion",params={'desde':first['id'],'hasta':second['id']})
    assert r.status_code==200
    comparison=r.json()
    actual={'versiones':len(env.api.get(f"/api/v1/practicas/{p['id']}/versiones").json()['items']),'v1_sin_cambios':original==first,'v1_cumplidos':first['cumplidos'],'v2_cumplidos':second['cumplidos'],'aplicables':second['aplicables'],'delta_pp':comparison['delta_pp'],'resolucion':comparison['resolucion'],'alertas_nuevas':comparison['alertas_nuevas']}
    expected=json.loads((__import__('pathlib').Path(__file__).parents[3]/'fixtures/integration_cases.json').read_text(encoding='utf-8'))['casos'][0]['esperado']
    assert actual==expected
    assert comparison['mejora_estructural'] is True
    assert env.api.get('/api/v1/practicas').json()['items'][0]['id']==p['id']
    assert len(env.api.get('/api/v1/progreso').json()['items'])==1


def test_int05_preventive_objective_no_persistence_until_confirmation(env,account):
    env.login(account)
    entry={'modo':'guiado','objetivo':'Ejercicio con persona@example.invalid','aplicabilidad':{'C2':False,'C3':False,'C4':False}}
    start=post(env,'/practicas/preparar',entry).json()
    assert len(start['coincidencias'])==1
    with env.db.connect() as c:
        assert c.scalar(text('SELECT count(*) FROM practica WHERE usuario_id=:id'),{'id':account[0]})==0
    data={**entry,'token_inicio':start['token_inicio'],'coincidencias_confirmadas':[],'request_id':str(uuid4())}
    assert post(env,'/practicas',data).status_code==409
    assert env.api.get('/api/v1/practicas').json()['items']==[]
    data['coincidencias_confirmadas']=[m['clave'] for m in start['coincidencias']]
    created=post(env,'/practicas',data)
    assert created.status_code==201
    assert created.json()['configuracion_propia']['C2']['aplica'] is False
    assert 'persona@example.invalid' not in canonical(created.json()['revision_inicio'])
    data['token_inicio']='respuesta-perdida';data['coincidencias_confirmadas']=[]
    assert post(env,'/practicas',data).status_code==200


@pytest.mark.parametrize('case_id',['CP-01','CP-05','CP-20','CP-25','CP-27','CP-28','CP-31','CP-33'])
def test_saved_results_match_unchanged_fixture(env,account,case_id):
    case=CASES[case_id]
    env.login(account)
    if case['desafio_codigo']:
        challenge=next(c for c in env.api.get('/api/v1/desafios?limit=100').json()['items'] if c['desafio']['codigo']==case['desafio_codigo'])
        entry={'modo':case['entrada']['modo'],'desafio_id':challenge['id']}
    else:
        entry={'modo':case['entrada']['modo'],'objetivo':'Ensayo propio ficticio','aplicabilidad':{code:case['configuracion_propia'][code]['aplica'] for code in ('C2','C3','C4')}}
    start=post(env,'/practicas/preparar',entry).json()
    p=post(env,'/practicas',{**entry,'token_inicio':start['token_inicio'],'coincidencias_confirmadas':[],'request_id':str(uuid4())}).json()
    result,_=save(env,p['id'],case['entrada'])
    expected=case['esperado']
    assert {r['criterio_codigo']:r['estado'] for r in result['resultados']}==expected['estados']
    assert result['cumplidos']==expected['cumplidos']
    assert result['aplicables']==expected['aplicables']
    assert result['cumplimiento_mostrado']==expected['cumplimiento_mostrado']


def test_alerts_confirmation_and_safe_storage(env,account):
    p,_=begin(env,account,own='Ensayo ficticio')
    draft=deepcopy(CASES['CP-01']['entrada'])
    draft['componentes']['contexto']['texto']='uno@example.invalid y dos@example.invalid'
    data,preview=review(env,p['id'],draft)
    assert len(preview['coincidencias'])==2
    assert env.api.get(f"/api/v1/practicas/{p['id']}/versiones").json()['items']==[]
    partial=deepcopy(data);partial['coincidencias_confirmadas']=data['coincidencias_confirmadas'][:1]
    assert post(env,f"/practicas/{p['id']}/versiones",partial).status_code==409
    result=post(env,f"/practicas/{p['id']}/versiones",data).json()
    assert len(result['coincidencias'])==2 and result['resultados'][5]['estado']=='cumple'
    with env.db.connect() as c:
        alerts=c.execute(text('SELECT tipo,campo,huella,estado FROM alerta_sensible WHERE version_id=:id'),{'id':result['id']}).mappings().all()
        assert len(alerts)==2
        assert 'uno@example.invalid' not in str(alerts)
    assert all('uno@example.invalid' not in canonical(r) for r in result['resultados'])


@pytest.mark.parametrize('change',['draft','token','operation','scope','expired','config','rules','key'])
def test_sec13_14_stale_review_never_writes(env,account,change):
    p,_=begin(env,account)
    data,_=review(env,p['id'],CASES['CP-01']['entrada'])
    cleanup=None
    if change=='draft':data['borrador']['componentes']['tarea']['texto']='Texto editado después'
    if change=='token':data['token_revision']+='x'
    if change=='operation':data['token_revision']=post(env,'/practicas/preparar',{'modo':'guiado','desafio_id':p['desafio_id']}).json()['token_inicio']
    if change=='scope':
        p2,_=begin(env,account)
        p=p2
    if change=='expired':
        raw,_=data['token_revision'].split('.')
        payload=json.loads(base64.urlsafe_b64decode(raw+'='*(-len(raw)%4)));payload['exp']=0
        raw=base64.urlsafe_b64encode(canonical(payload).encode()).rstrip(b'=').decode()
        data['token_revision']=raw+'.'+hmac.new(env.app.state.practices.key,raw.encode(),hashlib.sha256).hexdigest()
    if change in ('config','rules'):
        with env.db.begin() as c:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':CATALOG_LOCK})
            if change=='config':
                old=c.scalar(text('SELECT revision FROM desafio WHERE id=:id'),{'id':p['desafio_id']})
                c.execute(text('UPDATE desafio SET revision=revision+1 WHERE id=:id'),{'id':p['desafio_id']})
                cleanup=('UPDATE desafio SET revision=:old WHERE id=:id',{'old':old,'id':p['desafio_id']})
            else:
                row=c.execute(text("SELECT id,mensajes FROM regla WHERE activa AND criterio_id=(SELECT id FROM criterio WHERE codigo='C1')")).mappings().one()
                c.execute(text("UPDATE regla SET mensajes=mensajes || '{\"cumple\":\"Mensaje cambiado\"}'::jsonb WHERE id=:id"),{'id':row['id']})
                cleanup=('UPDATE regla SET mensajes=CAST(:old AS jsonb) WHERE id=:id',{'old':canonical(row['mensajes']),'id':row['id']})
    if change=='key':env.app.state.practices.settings.alert_fingerprint_key_version+=1
    try:
        assert post(env,f"/practicas/{p['id']}/versiones",data).status_code==409
        assert env.api.get(f"/api/v1/practicas/{p['id']}/versiones").json()['items']==[]
    finally:
        if cleanup:
            with env.db.begin() as c:c.execute(text(cleanup[0]),cleanup[1])


def test_idempotency_lost_responses_and_conflicts(env,account):
    p,creation=begin(env,account)
    creation['token_inicio']='expired-and-corrupt-after-lost-response'
    assert post(env,'/practicas',creation).status_code==200
    changed=deepcopy(creation);changed['modo']='libre'
    assert post(env,'/practicas',changed).status_code==409
    result,data=save(env,p['id'],CASES['CP-01']['entrada'])
    data['token_revision']='expired-and-corrupt-after-lost-response'
    replay=post(env,f"/practicas/{p['id']}/versiones",data)
    assert replay.status_code==200 and replay.json()==result
    data['borrador']['componentes']['tarea']['texto']='Otra entrada'
    assert post(env,f"/practicas/{p['id']}/versiones",data).status_code==409
    alert=deepcopy(CASES['CP-01']['entrada']);alert['componentes']['contexto']['texto']='ficticio@example.invalid'
    first,retry=save(env,p['id'],alert)
    retry['token_revision']='respuesta-perdida';retry['coincidencias_confirmadas']=[]
    result=post(env,f"/practicas/{p['id']}/versiones",retry)
    assert result.status_code==200 and result.json()==first
    new,preview=review(env,p['id'],alert);new['coincidencias_confirmadas']=[]
    assert post(env,f"/practicas/{p['id']}/versiones",new).status_code==409


def test_int04_failure_rolls_back_all_rows(env,account):
    p,_=begin(env,account)
    data,_=review(env,p['id'],CASES['CP-01']['entrada'])
    def failure(conn,cursor,statement,parameters,context,executemany):
        if statement.startswith('INSERT INTO resultado'):raise RuntimeError('Fallo técnico ficticio sin datos')
    event.listen(env.engine,'before_cursor_execute',failure)
    try:assert post(env,f"/practicas/{p['id']}/versiones",data).status_code==500
    finally:event.remove(env.engine,'before_cursor_execute',failure)
    with env.db.connect() as c:
        assert c.scalar(text('SELECT count(*) FROM version_prompt WHERE practica_id=:id'),{'id':p['id']})==0
        assert c.scalar(text('SELECT count(*) FROM evaluacion e JOIN version_prompt v ON v.id=e.version_id WHERE v.practica_id=:id'),{'id':p['id']})==0
        assert c.scalar(text('SELECT count(*) FROM resultado r JOIN evaluacion e ON e.id=r.evaluacion_id JOIN version_prompt v ON v.id=e.version_id WHERE v.practica_id=:id'),{'id':p['id']})==0


@pytest.mark.parametrize('same_id',[True,False])
def test_concurrent_versions_numbering_and_retries(env,account,same_id):
    p,_=begin(env,account)
    data,_=review(env,p['id'],CASES['CP-01']['entrada'])
    session=env.api.cookies.get('ep_session'); csrf=env.csrf()
    gate=threading.Barrier(2)
    def write(index):
        values=deepcopy(data)
        if not same_id:values['request_id']=str(uuid4())
        gate.wait(timeout=5)
        with env.access.authorized(session,csrf=csrf,write=True) as (c,u,s):
            return env.app.state.practices.save(c,u,UUID(p['id']),values)
    with ThreadPoolExecutor(max_workers=2) as pool: outcomes=list(pool.map(write,(1,2)))
    rows=env.api.get(f"/api/v1/practicas/{p['id']}/versiones").json()['items']
    assert len(rows)==(1 if same_id else 2)
    assert [r['numero'] for r in rows]==([1] if same_id else [1,2])
    assert sum(created for _,created in outcomes)==(1 if same_id else 2)


def test_concurrent_creation_idempotent(env,account):
    env.login(account)
    challenge=next(c for c in env.api.get('/api/v1/desafios?limit=100').json()['items'] if c['desafio']['codigo']=='D01_CORREO_REUNION')
    entry={'modo':'guiado','desafio_id':challenge['id']}
    prepared=post(env,'/practicas/preparar',entry).json()
    creation={**entry,'token_inicio':prepared['token_inicio'],'coincidencias_confirmadas':[],'request_id':str(uuid4())}
    session=env.api.cookies.get('ep_session');csrf=env.csrf()
    gate=threading.Barrier(2)
    def retry(_):
        gate.wait(timeout=5)
        with env.access.authorized(session,csrf=csrf,write=True) as (c,u,s):return env.app.state.practices.create(c,u,creation)
    with ThreadPoolExecutor(max_workers=2) as pool:outcomes=list(pool.map(retry,(1,2)))
    assert sum(created for _,created in outcomes)==1
    assert outcomes[0][0]['id']==outcomes[1][0]['id']
    assert len(env.api.get('/api/v1/practicas').json()['items'])==1


def test_sec12_15_16_new_alert_and_key_rotation(env,account):
    p,_=begin(env,account,own='Ensayo sin datos reales')
    draft=deepcopy(CASES['CP-01']['entrada']);draft['componentes']['contexto']['texto']='uno@example.invalid'
    first,_=save(env,p['id'],draft)
    draft['componentes']['contexto']['texto']='dos@example.invalid'
    second,_=save(env,p['id'],draft)
    r=env.api.get(f"/api/v1/practicas/{p['id']}/comparacion",params={'desde':first['id'],'hasta':second['id']}).json()
    assert r['alertas_nuevas']==1 and r['mejora_estructural'] is False
    env.app.state.practices.settings.alert_fingerprint_key_version=2
    env.app.state.practices.fingerprint=b'ficticia-rotada-para-test-00000000000000'
    third,_=save(env,p['id'],draft)
    r=env.api.get(f"/api/v1/practicas/{p['id']}/comparacion",params={'desde':second['id'],'hasta':third['id']}).json()
    assert r['alertas_nuevas'] is None and r['mejora_estructural'] is False
    assert r['resolucion'] is None
    assert env.api.get('/api/v1/versiones/'+first['id']).json()==first


def test_changed_rules_snapshot_historical_comparison(env,account):
    p,_=begin(env,account)
    first,_=save(env,p['id'],CASES['CP-31']['entrada'])
    with env.db.begin() as c:
        old=c.execute(text("SELECT * FROM regla WHERE activa AND criterio_id=(SELECT id FROM criterio WHERE codigo='C2')")).mappings().one()
        new=uuid4()
        c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':CATALOG_LOCK})
        c.execute(text('UPDATE regla SET activa=false WHERE id=:id'),{'id':old['id']})
        c.execute(text('INSERT INTO regla(id,criterio_id,tipo,parametros,mensajes,version,activa) VALUES (:id,:cid,:type,CAST(:params AS jsonb),CAST(:messages AS jsonb),:version,true)'),{'id':new,'cid':old['criterio_id'],'type':old['tipo'],'params':canonical(old['parametros']),'messages':canonical(old['mensajes']),'version':old['version']+1})
    try:
        second,_=save(env,p['id'],CASES['CP-01']['entrada'])
        r=env.api.get(f"/api/v1/practicas/{p['id']}/comparacion",params={'desde':first['id'],'hasta':second['id']}).json()
        assert r['comparable'] is False and r['delta_pp'] is None and r['resolucion'] is None
        assert env.api.get('/api/v1/versiones/'+first['id']).json()==first
        assert len(env.api.get('/api/v1/progreso').json()['items'])==2
    finally:
        with env.db.begin() as c:
            # La fila nueva ya usada se conserva inactiva; eliminar sólo con su práctica de fixture.
            c.execute(text('DELETE FROM practica WHERE id=:id'),{'id':p['id']})
            c.execute(text('DELETE FROM regla WHERE id=:id'),{'id':new})
            c.execute(text('UPDATE regla SET activa=true WHERE id=:id'),{'id':old['id']})


@pytest.mark.parametrize('role',['usuario','administrador'])
def test_sec07_all_derived_resources_enforce_owner(env,account,role):
    p,_=begin(env,account)
    first,_=save(env,p['id'],CASES['CP-01']['entrada'])
    outsider=env.account(role);env.login(outsider)
    for path in [f"/practicas/{p['id']}",f"/practicas/{p['id']}/versiones",'/versiones/'+first['id'],f"/practicas/{p['id']}/comparacion?desde={first['id']}&hasta={first['id']}"]:
        assert env.api.get('/api/v1'+path).status_code==404
    assert post(env,f"/practicas/{p['id']}/revisar",CASES['CP-01']['entrada']).status_code==404
    assert env.api.get('/api/v1/practicas').json()['items']==[]
    assert env.api.get('/api/v1/progreso').json()['items']==[]


def test_history_cursor_filters_and_progress_pagination(env,account):
    p,_=begin(env,account)
    first,_=save(env,p['id'],CASES['CP-31']['entrada'])
    second,_=save(env,p['id'],CASES['CP-01']['entrada'])
    own,_=begin(env,account,own='Otra práctica ficticia')
    listing=env.api.get('/api/v1/practicas?limit=1').json()
    assert listing['items'][0]['id']==own['id']
    assert env.api.get('/api/v1/practicas',params={'limit':1,'cursor':listing['next_cursor']}).json()['items'][0]['id']==p['id']
    assert len(env.api.get('/api/v1/practicas',params={'desafio_id':p['desafio_id']}).json()['items'])==1
    assert env.api.get('/api/v1/practicas?desde=2099-01-01').json()['items']==[]
    assert env.api.get('/api/v1/practicas?desde=2099-01-01&hasta=2000-01-01').status_code==422
    progress=env.api.get('/api/v1/progreso?limit=1').json()
    assert progress['items'][0]['versiones'][0]['id']==first['id']
    assert env.api.get('/api/v1/progreso',params={'limit':1,'cursor':progress['next_cursor']}).json()['items'][0]['versiones'][0]['id']==second['id']


def test_free_normalization_partial_and_empty_guard(env,account):
    p,_=begin(env,account,own='Ensayo libre',mode='libre')
    draft=deepcopy(CASES['CP-01']['entrada']);draft['modo']='libre';draft['texto_libre']='  Redaccio\u0301n original\r\ncon espacios  '
    assert post(env,f"/practicas/{p['id']}/revisar",draft).status_code==422
    draft['componentes_confirmados']=True
    first,_=save(env,p['id'],draft)
    assert first['texto']=='  Redacción original\ncon espacios  '
    draft['texto_libre']=''
    data,_=review(env,p['id'],draft)
    assert post(env,f"/practicas/{p['id']}/versiones",data).status_code==422
    draft['texto_libre']='Texto con componentes incompletos'
    draft['componentes']['tarea']['texto']=''
    result,_=save(env,p['id'],draft)
    assert result['resultados'][0]['estado']=='revisar'


def test_review_errors_csrf_and_sensitive_text_are_safe(env,account,caplog):
    p,_=begin(env,account)
    marker='dato-privado@example.invalid'
    data=deepcopy(CASES['CP-01']['entrada']);data['componentes']['tarea']['texto']={'no_valido':marker}
    response=post(env,f"/practicas/{p['id']}/revisar",data)
    assert response.status_code==422 and marker not in response.text and marker not in caplog.text
    assert env.post(f"/practicas/{p['id']}/revisar",CASES['CP-01']['entrada']).status_code==403


def test_server_storage_is_immutable_to_runtime(env,account):
    p,_=begin(env,account)
    first,_=save(env,p['id'],CASES['CP-01']['entrada'])
    from sqlalchemy.exc import DBAPIError
    for query in ["UPDATE version_prompt SET texto='alterado' WHERE id=:id",'DELETE FROM version_prompt WHERE id=:id',"UPDATE practica SET objetivo='alterado' WHERE id=:id"]:
        with env.engine.connect() as c:
            with pytest.raises(DBAPIError):c.execute(text(query),{'id':first['id'] if 'version_prompt' in query else p['id']})


@pytest.mark.parametrize('state',['bloqueado','desactivado'])
def test_account_block_serializes_real_version_save(env,account,state):
    p,_=begin(env,account)
    data,_=review(env,p['id'],CASES['CP-01']['entrada'])
    session=env.api.cookies.get('ep_session');csrf=env.csrf()
    admin=env.account('administrador');admin_session=env.login(admin);admin_csrf=env.csrf()
    locked,release,started=threading.Event(),threading.Event(),threading.Event()
    def write():
        with env.access.authorized(session,csrf=csrf,write=True) as (c,u,s):
            locked.set();assert release.wait(10)
            return env.app.state.practices.save(c,u,UUID(p['id']),data)
    def block():
        started.set();env.access.set_state(admin_session,admin_csrf,account[0],state,'seguridad')
    with ThreadPoolExecutor(max_workers=2) as pool:
        writing=pool.submit(write);assert locked.wait(5)
        blocking=pool.submit(block);assert started.wait(5)
        try:
            with pytest.raises(TimeoutError):blocking.result(.25)
        finally:release.set()
        assert writing.result(10)[1] is True;blocking.result(10)
    with pytest.raises(AccessError):
        with env.access.authorized(session,csrf=csrf,write=True):pytest.fail('Escritura posterior al bloqueo autorizada')


@pytest.mark.parametrize('objective',['',' ','\r\n'])
def test_empty_objective_never_creates_practice(env,account,objective):
    env.login(account)
    r=post(env,'/practicas/preparar',{'modo':'guiado','objetivo':objective,'aplicabilidad':{'C2':False,'C3':False,'C4':False}})
    assert r.status_code==422
    assert env.api.get('/api/v1/practicas').json()['items']==[]


def test_foreign_token_cannot_be_reused_even_with_owned_destination(env,account):
    p,creation=begin(env,account)
    data,_=review(env,p['id'],CASES['CP-01']['entrada'])
    outsider=env.account()
    own,_=begin(env,outsider)
    assert post(env,f"/practicas/{own['id']}/versiones",data).status_code==409
    assert post(env,f"/practicas/{p['id']}/versiones",data).status_code==404
    creation['request_id']=str(uuid4())
    assert post(env,'/practicas',creation).status_code==409


def test_polling_does_not_extend_inactivity_and_dates_are_utc(env,account):
    p,_=begin(env,account)
    version,_=save(env,p['id'],CASES['CP-01']['entrada'])
    assert version['fecha'].endswith(('+00:00','Z'))
    token_hash=hashlib.sha256(env.api.cookies.get('ep_session').encode()).hexdigest()
    with env.db.begin() as c:
        previous=c.scalar(text("UPDATE sesion SET ultimo_uso_en=clock_timestamp()-interval '29 minutes' WHERE token_hash=:hash RETURNING ultimo_uso_en"),{'hash':token_hash})
    assert env.api.get('/api/v1/auth/me',headers={'X-Session-Probe':'1'}).status_code==200
    with env.db.begin() as c:
        assert c.scalar(text('SELECT ultimo_uso_en FROM sesion WHERE token_hash=:hash'),{'hash':token_hash})==previous
        c.execute(text("UPDATE sesion SET ultimo_uso_en=clock_timestamp()-interval '31 minutes' WHERE token_hash=:hash"),{'hash':token_hash})
    assert env.api.get('/api/v1/auth/me',headers={'X-Session-Probe':'1'}).status_code==401


def test_publication_waits_for_real_save_and_old_review_is_rejected(env,account):
    p,_=begin(env,account)
    data,_=review(env,p['id'],CASES['CP-01']['entrada'])
    session=env.api.cookies.get('ep_session');csrf=env.csrf()
    locked,release,started=threading.Event(),threading.Event(),threading.Event()
    old=p['configuracion']['desafio']['revision']
    def writing():
        with env.access.authorized(session,csrf=csrf,write=True) as (c,u,s):
            env.app.state.practices.catalog(c,p['desafio_id']);locked.set();assert release.wait(10)
            return env.app.state.practices.save(c,u,UUID(p['id']),data)
    def publishing():
        started.set()
        with env.db.begin() as c:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':CATALOG_LOCK})
            c.execute(text('UPDATE desafio SET revision=revision+1 WHERE id=:id'),{'id':p['desafio_id']})
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            writer=pool.submit(writing);assert locked.wait(5)
            publisher=pool.submit(publishing);assert started.wait(5)
            try:
                with pytest.raises(TimeoutError):publisher.result(.25)
            finally:release.set()
            first,created=writer.result(10);publisher.result(10)
        assert created and first['snapshot']['desafio']['revision']==old
        data['request_id']=str(uuid4())
        assert post(env,f"/practicas/{p['id']}/versiones",data).status_code==409
    finally:
        release.set()
        with env.db.begin() as c:
            c.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':CATALOG_LOCK})
            c.execute(text('UPDATE desafio SET revision=:old WHERE id=:id'),{'old':old,'id':p['desafio_id']})
