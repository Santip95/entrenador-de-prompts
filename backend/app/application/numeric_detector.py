"""Publicación técnica aditiva: conserva reglas, mensajes e historia existentes."""
from copy import deepcopy
from sqlalchemy import text
from app.application.administration import AdministrationService
from app.application.practices import PracticeService
from app.domain.evaluation import NUMERIC_DETECTOR


def activate_numeric_detector(connection, settings):
    admin = AdministrationService(PracticeService(settings))
    admin.lock(connection)
    rules = admin.rules(connection)
    active = [r for r in rules if r['criterio_codigo'] == 'C6' and r['activa']]
    if len(active) != 1:
        raise ValueError('Se requiere exactamente una regla C6 activa; no se sustituye configuración ausente.')
    previous = active[0]
    # No alterar configuraciones inmutables o específicas silenciosamente.
    overrides = connection.scalar(text("SELECT count(*) FROM desafio_criterio dc JOIN criterio c ON c.id=dc.criterio_id WHERE c.codigo='C6' AND dc.configuracion->'parametros' ? 'detectores_activos'"))
    if overrides:
        raise ValueError('Hay desafíos con detectores explícitos; revisar su publicación antes de activar globalmente.')
    if NUMERIC_DETECTOR in previous['parametros']['detectores_activos']:
        return {'creada': False, 'version': previous['version'], 'regla_id': previous['id']}
    data = {k: deepcopy(previous[k]) for k in ('criterio_codigo', 'tipo', 'parametros', 'mensajes')}
    data['parametros']['detectores_activos'].append(NUMERIC_DETECTOR)
    # Actor nulo identifica intervención técnica local; no crea cuentas ni privilegios.
    candidate = admin.new_rule(connection, {'id': None}, data)
    admin.rule_state(connection, {'id': None}, candidate['id'], previous['id'], True)
    return {'creada': True, 'version': candidate['version'], 'regla_id': candidate['id']}
