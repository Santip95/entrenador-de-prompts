from copy import deepcopy
from uuid import uuid4
import pytest
from sqlalchemy import text
from app.application.numeric_detector import activate_numeric_detector
from app.domain.evaluation import NUMERIC_DETECTOR
from test_administration import catalog
from test_practices import begin, save, review, post, CASES


def activate(env):
    with env.db.begin() as c:
        assert c.scalar(text('SELECT current_database()')) == 'entrenador_prompts_test'
        return activate_numeric_detector(c, env.app.state.settings)


@pytest.mark.parametrize('mode', ['guiado', 'libre'])
def test_versioned_activation_review_confirm_save_and_history(env, account, catalog, mode):
    practice, _ = begin(env, account, mode=mode)
    draft = deepcopy(CASES['CP-01']['entrada'])
    draft['componentes']['tarea']['texto'] = 'Usar número ficticio 1234567'
    if mode == 'libre':
        draft.update(modo='libre', texto_libre='Usar número ficticio 0123456', componentes_confirmados=True)
        draft['componentes']['tarea']['texto'] = 'Redactar un ejemplo ficticio'
    first, _ = save(env, practice['id'], draft)
    assert not first['coincidencias'] and first['motor_version'] == '1.1.0'
    stale_data, _ = review(env, practice['id'], draft)
    with env.db.connect() as c:
        old = dict(c.execute(text("SELECT * FROM regla r WHERE r.activa AND r.criterio_id=(SELECT id FROM criterio WHERE codigo='C6')")).mappings().one())
    result = activate(env)
    assert result['creada'] is True
    assert activate(env) == {**result, 'creada': False}
    assert post(env, f"/practicas/{practice['id']}/versiones", stale_data).status_code == 409
    data, preview = review(env, practice['id'], draft)
    assert len(preview['coincidencias']) == 1 and preview['resultados'][5]['estado'] == 'advertencia'
    missing = {**data, 'coincidencias_confirmadas': []}
    assert post(env, f"/practicas/{practice['id']}/versiones", missing).status_code == 409
    assert len(env.api.get(f"/api/v1/practicas/{practice['id']}/versiones").json()['items']) == 1
    response = post(env, f"/practicas/{practice['id']}/versiones", data)
    assert response.status_code == 201
    second = response.json()
    assert second['resultados'][5]['estado'] == 'cumple'
    assert second['coincidencias'][0]['confirmada'] is True
    assert env.api.get('/api/v1/versiones/' + first['id']).json() == first
    comparison = env.api.get(f"/api/v1/practicas/{practice['id']}/comparacion",params={'desde':first['id'],'hasta':second['id']}).json()
    assert comparison['comparable'] is False and comparison['delta_pp'] is None
    with env.db.connect() as c:
        current = dict(c.execute(text('SELECT * FROM regla WHERE id=:id'), {'id': old['id']}).mappings().one())
        assert {**current, 'activa': old['activa']} == old
        stored = c.execute(text('SELECT tipo,campo,estado FROM alerta_sensible WHERE version_id=:id'), {'id':second['id']}).mappings().one()
        assert stored['tipo'] == 'secuencia_numerica' and stored['estado'] == 'confirmada'


def test_numeric_objective_review_does_not_persist_before_confirmation(env, account, catalog):
    activate(env); env.login(account)
    entry={'modo':'guiado','objetivo':'Objetivo ficticio 12345678','aplicabilidad':{'C2':False,'C3':False,'C4':False}}
    preview=post(env,'/practicas/preparar',entry).json()
    assert len(preview['coincidencias']) == 1
    data={**entry,'token_inicio':preview['token_inicio'],'request_id':str(uuid4()),'coincidencias_confirmadas':[]}
    assert post(env,'/practicas',data).status_code == 409
    with env.db.connect() as c:
        assert c.scalar(text('SELECT count(*) FROM practica WHERE usuario_id=:id'),{'id':account[0]}) == 0
    data['coincidencias_confirmadas']=[m['clave'] for m in preview['coincidencias']]
    assert post(env,'/practicas',data).status_code == 201
