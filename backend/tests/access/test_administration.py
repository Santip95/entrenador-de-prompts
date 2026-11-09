"""Etapa 05: PostgreSQL real, catálogo y borrado; sin alterar desarrollo."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
from uuid import uuid4
import pytest
from sqlalchemy import text
from cryptography.fernet import Fernet
from app.operations.journal import DeletionJournal,JournalError
from app.domain.evaluation import canonical
from test_practices import begin,save,review,post,CASES

@pytest.fixture
def catalog(env):
    with env.db.connect() as c:
        assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
        rules=[dict(r) for r in c.execute(text('SELECT * FROM regla')).mappings()]
        criteria=[dict(r) for r in c.execute(text('SELECT * FROM criterio')).mappings()]
        challenges=[dict(r) for r in c.execute(text('SELECT * FROM desafio')).mappings()]
        configs=[dict(r) for r in c.execute(text('SELECT * FROM desafio_criterio')).mappings()]
    yield
    with env.db.begin() as c:
        assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
        for uid in env.created_users:
            c.execute(text('DELETE FROM practica WHERE usuario_id=:id'),{'id':uid})
        c.execute(text('DELETE FROM desafio_criterio'))
        c.execute(text('DELETE FROM desafio WHERE NOT(id=ANY(:ids))'),{'ids':[r['id'] for r in challenges]})
        for r in challenges:
            c.execute(text('UPDATE desafio SET titulo=:titulo,consigna=:consigna,estado=:estado,activo=:activo,revision=:revision,actualizado_en=:actualizado_en WHERE id=:id'),r)
        for r in configs:
            c.execute(text('INSERT INTO desafio_criterio VALUES (:desafio_id,:criterio_id,:obligatorio,CAST(:configuracion AS jsonb))'),{**r,'configuracion':canonical(r['configuracion'])})
        c.execute(text('UPDATE regla SET activa=false'))
        c.execute(text('DELETE FROM regla WHERE NOT(id=ANY(:ids))'),{'ids':[r['id'] for r in rules]})
        for r in rules: c.execute(text('UPDATE regla SET activa=:activa WHERE id=:id'),r)
        for r in criteria: c.execute(text('UPDATE criterio SET nombre=:nombre,descripcion=:descripcion,actualizado_en=:actualizado_en WHERE id=:id'),r)

@pytest.fixture
def journal(env,tmp_path):
    state=tmp_path/'state';keys=tmp_path/'keys';state.mkdir();keys.mkdir()
    key=keys/'journal.key';key.write_bytes(Fernet.generate_key())
    j=DeletionJournal(state/'journal.fernet',key,keys/'anchor')
    j.initialize()
    env.app.state.settings.deletion_journal_location=str(j.path)
    env.app.state.settings.deletion_journal_key_file=str(j.key_file)
    env.app.state.settings.deletion_journal_anchor_file=str(j.anchor)
    return j

def admin(env):
    a=env.account(role='administrador');env.login(a);return a

def challenge_input(env):
    old=env.api.get('/api/v1/admin/desafios?limit=100').json()['items'][0]
    return {'codigo':'TEST_'+uuid4().hex.upper(),'titulo':'Desafío ficticio','consigna':'Redactar texto ficticio','configuracion':old['configuracion']}

def new_rule(env,code='C2'):
    current=next(r for r in env.api.get('/api/v1/admin/reglas').json()['items'] if r['criterio_codigo']==code and r['activa'])
    data={k:current[k] for k in ('criterio_codigo','tipo','parametros','mensajes')}
    data=deepcopy(data);data['mensajes']['cumple']='Contexto declarado: revisión ficticia nueva.'
    r=post(env,'/admin/reglas',data)
    assert r.status_code==201,r.status_code
    assert r.json()['activa'] is False
    return current,r.json()

def test_draft_publish_edit_revision_and_no_destructive_routes(env,catalog):
    admin(env);data=challenge_input(env)
    r=post(env,'/admin/desafios',data);assert r.status_code==201
    row=r.json();assert row['estado']=='borrador'
    assert row['id'] not in [x['id'] for x in env.api.get('/api/v1/desafios?limit=100').json()['items']]
    edit=env.api.put('/api/v1/admin/desafios/'+row['id'],json={**data,'titulo':'Edición borrador','revision_esperada':1},headers={'Origin':env.origin,'X-CSRF-Token':env.csrf()})
    assert edit.status_code==200 and edit.json()['estado']=='borrador'
    assert post(env,f"/admin/desafios/{row['id']}/publicar",{'revision_esperada':1}).status_code==409
    published=post(env,f"/admin/desafios/{row['id']}/publicar",{'revision_esperada':2})
    assert published.status_code==200 and published.json()['estado']=='publicado'
    assert row['id'] in [x['id'] for x in env.api.get('/api/v1/desafios?limit=100').json()['items']]
    assert env.api.delete('/api/v1/admin/desafios/'+row['id'],headers={'Origin':env.origin,'Content-Type':'application/json','X-CSRF-Token':env.csrf()}).status_code==405

def test_at23_int03_publish_preserves_snapshot_and_stales_review(env,catalog,account):
    p,_=begin(env,account);first,_=save(env,p['id'],CASES['CP-31']['entrada']);stale,_=review(env,p['id'],CASES['CP-01']['entrada'])
    administrator=admin(env);old,new=new_rule(env)
    published=post(env,f"/admin/reglas/{new['id']}/publicar",{'regla_activa_esperada':old['id']});assert published.status_code==200
    env.login(account)
    assert post(env,f"/practicas/{p['id']}/versiones",stale).status_code==409
    assert env.api.get('/api/v1/versiones/'+first['id']).json()==first
    second,_=save(env,p['id'],CASES['CP-01']['entrada'])
    comparison=env.api.get(f"/api/v1/practicas/{p['id']}/comparacion?desde={first['id']}&hasta={second['id']}").json()
    assert comparison['comparable'] is False
    assert comparison['delta_pp'] is None and comparison['resolucion'] is None
    env.login(administrator)
    assert post(env,f"/admin/reglas/{old['id']}/publicar",{'regla_activa_esperada':old['id']}).status_code==409

def test_at24_inactive_challenge_history_read_and_no_new_versions(env,catalog,account):
    p,_=begin(env,account);saved,_=save(env,p['id'],CASES['CP-01']['entrada'])
    a=admin(env);row=next(r for r in env.api.get('/api/v1/admin/desafios?limit=100').json()['items'] if r['id']==p['desafio_id'])
    assert post(env,f"/admin/desafios/{row['id']}/desactivar",{'revision_esperada':row['revision']}).status_code==200
    env.login(account)
    assert env.api.get('/api/v1/versiones/'+saved['id']).status_code==200
    assert post(env,f"/practicas/{p['id']}/revisar",CASES['CP-01']['entrada']).status_code==409

def test_missing_active_rule_blocks_evaluation_without_partial_persistence(env,catalog,account):
    p,_=begin(env,account);a=admin(env)
    rule=next(r for r in env.api.get('/api/v1/admin/reglas').json()['items'] if r['criterio_codigo']=='C2' and r['activa'])
    assert post(env,f"/admin/reglas/{rule['id']}/desactivar",{'regla_activa_esperada':rule['id']}).status_code==200
    env.login(account)
    r=post(env,f"/practicas/{p['id']}/revisar",CASES['CP-01']['entrada']);assert r.status_code==503
    with env.db.connect() as c: assert c.scalar(text('SELECT count(*) FROM version_prompt WHERE practica_id=:id'),{'id':p['id']})==0

@pytest.mark.parametrize('field,value',[('tipo','eval'),('parametros',{'expresion':'__import__("os")'}),('parametros',{'combinacion':'OR'}),('mensajes',{'cumple':'incompleto'})])
def test_invalid_rule_never_inserted(env,catalog,field,value):
    admin(env);row=next(r for r in env.api.get('/api/v1/admin/reglas').json()['items'] if r['activa'])
    data={k:deepcopy(row[k]) for k in ('criterio_codigo','tipo','parametros','mensajes')};data[field]=value
    with env.db.connect() as c: before=c.scalar(text('SELECT count(*) FROM regla'))
    assert post(env,'/admin/reglas',data).status_code in (422,503)
    with env.db.connect() as c: assert c.scalar(text('SELECT count(*) FROM regla'))==before

def test_no_admin_role_no_csrf_and_fixed_criterion(env,catalog,account):
    env.login(account)
    assert env.api.get('/api/v1/admin/reglas').status_code==403
    admin(env);data=challenge_input(env)
    assert env.post('/admin/desafios',data).status_code==403
    row=env.api.get('/api/v1/admin/criterios').json()['items'][0]
    r=env.api.patch('/api/v1/admin/criterios/'+row['codigo'],json={'nombre':'Presentación ficticia','descripcion':'Conserva significado','revision_esperada':row['revision']},headers={'Origin':env.origin,'X-CSRF-Token':env.csrf()})
    assert r.status_code==200
    assert env.api.patch('/api/v1/admin/criterios/'+row['codigo'],json={'codigo':'C7','nombre':'x','descripcion':'y','revision_esperada':row['revision']},headers={'Origin':env.origin,'X-CSRF-Token':env.csrf()}).status_code==422

def test_at25_concurrent_publication_one_winner(env,catalog):
    a=admin(env);old,new=new_rule(env)
    other=post(env,'/admin/reglas',{k:new[k] for k in ('criterio_codigo','tipo','parametros','mensajes')}).json()
    token=env.api.cookies.get('ep_session');csrf=env.csrf()
    second=env.account('administrador');second_token=env.login(second);second_csrf=env.csrf()
    def publish(args):
        row,token,csrf=args
        with env.browser() as browser:
            browser.cookies.set('ep_session',token)
            return env.post(f"/admin/reglas/{row['id']}/publicar",{'regla_activa_esperada':old['id']},csrf=csrf,browser=browser).status_code
    with ThreadPoolExecutor(2) as pool: results=list(pool.map(publish,[(new,token,csrf),(other,second_token,second_csrf)]))
    assert sorted(results)==[200,409]
    with env.db.connect() as c: assert c.scalar(text("SELECT count(*) FROM regla r JOIN criterio c ON c.id=r.criterio_id WHERE c.codigo='C2' AND activa"))==1

def delete(env,path,body=None,csrf=True):
    return env.api.request('DELETE','/api/v1'+path,json=body or {},headers={'Origin':env.origin,'X-CSRF-Token':env.csrf() if csrf else ''})

def test_own_delete_cascade_retry_other_practice_and_foreign_admin(env,journal,account):
    p,_=begin(env,account);v,_=save(env,p['id'],CASES['CP-01']['entrada']);other,_=begin(env,account,own='Otro objetivo ficticio')
    a=admin(env)
    assert delete(env,'/practicas/'+p['id']).status_code==404
    env.login(account)
    assert delete(env,'/practicas/'+p['id'],csrf=False).status_code==403
    assert delete(env,'/practicas/'+p['id']).status_code==204
    assert delete(env,'/practicas/'+p['id']).status_code==204
    assert env.api.get('/api/v1/versiones/'+v['id']).status_code==404
    assert env.api.get('/api/v1/practicas/'+other['id']).status_code==200
    records=journal.entries();assert len(records)==1 and records[0]['completado_en']
    assert b'@' not in Fernet(journal.key_file.read_bytes()).decrypt(journal.path.read_bytes())

def test_journal_failure_blocks_delete_and_pending_retry(env,journal,account,monkeypatch):
    p,_=begin(env,account,own='Datos ficticios')
    original=journal.path.read_bytes();journal.path.write_bytes(b'corrupto')
    assert delete(env,'/practicas/'+p['id']).status_code==503
    assert env.api.get('/api/v1/practicas/'+p['id']).status_code==200
    journal.path.write_bytes(original)
    def fail_complete(self,identifier): raise JournalError('fallo ficticio')
    with monkeypatch.context() as patch:
        patch.setattr(DeletionJournal,'complete',fail_complete)
        assert delete(env,'/practicas/'+p['id']).status_code==503
    assert journal.entries()[0]['completado_en'] is None
    assert delete(env,'/practicas/'+p['id']).status_code==204
    assert journal.entries()[0]['completado_en'] is not None

def test_account_delete_password_csrf_and_global_cascade(env,journal,account):
    p,_=begin(env,account);v,_=save(env,p['id'],CASES['CP-01']['entrada'])
    with env.browser() as second:
        env.login(account,browser=second)
        assert delete(env,'/cuenta',{'password_actual':account[2]},csrf=False).status_code==403
        assert delete(env,'/cuenta',{'password_actual':'incorrecta ficticia'}).status_code==401
        env.login(account)
        assert delete(env,'/cuenta',{'password_actual':account[2]}).status_code==204
        assert second.get('/api/v1/auth/me').status_code==401
    with env.db.connect() as c:
        assert not c.scalar(text('SELECT EXISTS(SELECT FROM usuario WHERE id=:id)'),{'id':account[0]})
        assert not c.scalar(text('SELECT EXISTS(SELECT FROM version_prompt WHERE id=:id)'),{'id':v['id']})
    assert journal.entries()[0]['tipo']=='cuenta'

def test_admin_cannot_delete_self_without_transfer(env,journal):
    a=admin(env)
    assert delete(env,'/cuenta',{'password_actual':a[2]}).status_code==409
    assert journal.entries()==[]


def test_local_first_admin_command_uses_hidden_password_and_never_overwrites(env,monkeypatch,capsys):
    from app.scripts import manage_access
    mail='cli05-'+str(uuid4())+'@example.invalid'
    password='Frase ficticia privada para comando local'
    monkeypatch.setattr('builtins.input',lambda prompt:mail)
    monkeypatch.setattr(manage_access,'getpass',lambda prompt:password)
    monkeypatch.setattr('sys.argv',['manage_access','crear-admin','--test'])
    manage_access.main()
    with env.db.connect() as c:
        row=c.execute(text('SELECT id,clave_hash,rol FROM usuario WHERE correo=:mail'),{'mail':mail}).mappings().one()
    env.created_users.append(row['id'])
    assert row['rol']=='administrador' and env.access.verify(row['clave_hash'],password)
    with pytest.raises(SystemExit):manage_access.main()
    output=capsys.readouterr();assert password not in output.out+output.err
    with env.db.connect() as c:assert c.scalar(text('SELECT count(*) FROM usuario WHERE correo=:mail'),{'mail':mail})==1


def test_admin_restrictions_serialized_and_last_enabled_admin_protected(env,journal):
    first=env.account('administrador');second=env.account('administrador')
    token_a=env.login(first);csrf_a=env.csrf();token_b=env.login(second);csrf_b=env.csrf()
    def restrict(arguments):
        token,csrf,target=arguments
        try:env.access.set_state(token,csrf,target,'bloqueado','seguridad');return 204
        except Exception as error:return getattr(error,'status',500)
    with ThreadPoolExecutor(2) as pool:
        results=list(pool.map(restrict,[(token_a,csrf_a,second[0]),(token_b,csrf_b,first[0])]))
    assert sorted(results)==[204,401]
    with env.db.connect() as c:
        active=c.execute(text("SELECT id FROM usuario WHERE id=ANY(:ids) AND estado='activo'"),{'ids':[first[0],second[0]]}).scalars().all()
    assert len(active)==1
    survivor=first if active[0]==first[0] else second
    env.login(survivor)
    assert delete(env,'/cuenta',{'password_actual':survivor[2]}).status_code==409


def test_pending_journal_survives_sql_rollback_and_retry(env,journal,account):
    from sqlalchemy import event
    p,_=begin(env,account,own='Rollback ficticio')
    def fail(connection,cursor,statement,parameters,context,executemany):
        if statement.startswith('DELETE FROM practica'):raise RuntimeError('Fallo ficticio')
    event.listen(env.engine,'before_cursor_execute',fail)
    try:assert delete(env,'/practicas/'+p['id']).status_code==500
    finally:event.remove(env.engine,'before_cursor_execute',fail)
    assert journal.entries()[0]['completado_en'] is None
    assert env.api.get('/api/v1/practicas/'+p['id']).status_code==200
    assert delete(env,'/practicas/'+p['id']).status_code==204
    assert len(journal.entries())==1 and journal.entries()[0]['completado_en']


def test_published_challenge_edit_rolls_back_all_six_criteria(env,catalog):
    from sqlalchemy import event
    admin(env);data=challenge_input(env);created=post(env,'/admin/desafios',data).json()
    old=post(env,f"/admin/desafios/{created['id']}/publicar",{'revision_esperada':1}).json()
    count=[0]
    def fail(connection,cursor,statement,parameters,context,executemany):
        if statement.startswith('INSERT INTO desafio_criterio'):
            count[0]+=1
            if count[0]==3:raise RuntimeError('Fallo ficticio')
    event.listen(env.engine,'before_cursor_execute',fail)
    try:
        r=env.api.put('/api/v1/admin/desafios/'+old['id'],json={**data,'titulo':'Cambio ficticio que debe revertirse','revision_esperada':old['revision']},headers={'Origin':env.origin,'X-CSRF-Token':env.csrf()})
        assert r.status_code==500
    finally:event.remove(env.engine,'before_cursor_execute',fail)
    actual=next(r for r in env.api.get('/api/v1/admin/desafios?limit=100').json()['items'] if r['id']==old['id'])
    assert actual==old and len(actual['configuracion'])==6


def test_sec14_real_publisher_waits_for_save_and_rejects_old_review(env,catalog,account):
    from concurrent.futures import TimeoutError
    import threading
    from uuid import UUID
    p,_=begin(env,account);data,_=review(env,p['id'],CASES['CP-01']['entrada']);writer_token=env.api.cookies.get('ep_session');writer_csrf=env.csrf()
    admin(env);old,new=new_rule(env);admin_token=env.api.cookies.get('ep_session');admin_csrf=env.csrf()
    # Crear una versión inactiva también cambia el catálogo ligado al token.
    # Revisar sobre ese estado antes de iniciar la carrera de publicación.
    writer_token=env.login(account);writer_csrf=env.csrf();data,_=review(env,p['id'],CASES['CP-01']['entrada'])
    locked,release,started=threading.Event(),threading.Event(),threading.Event()
    def writing():
        with env.access.authorized(writer_token,csrf=writer_csrf,write=True) as (c,u,s):
            env.app.state.practices.catalog(c,p['desafio_id']);locked.set();assert release.wait(10)
            return env.app.state.practices.save(c,u,UUID(p['id']),data)
    def publish():
        with env.browser() as browser:
            browser.cookies.set('ep_session',admin_token);started.set()
            return env.post(f"/admin/reglas/{new['id']}/publicar",{'regla_activa_esperada':old['id']},csrf=admin_csrf,browser=browser)
    try:
        with ThreadPoolExecutor(2) as pool:
            writer=pool.submit(writing);assert locked.wait(5)
            publisher=pool.submit(publish);assert started.wait(5)
            try:
                with pytest.raises(TimeoutError):publisher.result(.25)
            finally:release.set()
            version,created=writer.result(10);assert created and publisher.result(10).status_code==200
        env.login(account);data['request_id']=str(uuid4())
        assert post(env,f"/practicas/{p['id']}/versiones",data).status_code==409
    finally:release.set()
