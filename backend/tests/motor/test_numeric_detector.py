from copy import deepcopy
import pytest
from app.application.fixture_evaluation import fixture_context
from app.domain.evaluation import DETECTORS, NUMERIC_DETECTOR, _scan, confirm, review_objective

LEGACY = [d for d in DETECTORS if d != NUMERIC_DETECTOR]


@pytest.mark.parametrize('value', ['1234567', '12345678', '1234567890', '0123456', '0000000', '00000000', '0000000000'])
def test_numeric_exact_positive(value):
    result = review_objective(value, [NUMERIC_DETECTOR], context=fixture_context())
    assert len(result.matches) == 1
    assert result.matches[0]['tipo'] == 'secuencia_numerica'
    assert value not in str(result.matches)


@pytest.mark.parametrize('value', ['123456', '123456789', '12345678901', '2026', '12.345.678', '1234 5678',
                                  '123-4567', '1'*1000, '１２３４５６７', '١٢٣٤٥٦٧'])
def test_numeric_exact_negative(value):
    assert review_objective(value, [NUMERIC_DETECTOR], context=fixture_context()).matches == ()


@pytest.mark.parametrize('value', ['DNI 12345678', 'documento 12.345.678', 'tel 1234567890',
                                  '+54 1234567890', '12345678@example.invalid', 'tel 123456789'])
@pytest.mark.parametrize('reverse', [False, True])
def test_legacy_alerts_unchanged_and_numeric_overlap_suppressed(value, reverse):
    values = [('objetivo', value)]
    old, fingerprints = _scan(values, LEGACY, fixture_context(), 'binding-ficticio')
    assert old
    configured = [NUMERIC_DETECTOR, *LEGACY] if reverse else [*LEGACY, NUMERIC_DETECTOR]
    current, current_fingerprints = _scan(values, configured, fixture_context(), 'binding-ficticio')
    assert current == old
    assert current_fingerprints == fingerprints


def test_distinct_occurrences_and_fields_not_merged():
    result = review_objective('DNI 12345678; aislado 12345678; otra vez 12345678', list(DETECTORS), context=fixture_context())
    assert [m['tipo'] for m in result.matches] == ['documento', 'secuencia_numerica', 'secuencia_numerica']
    assert len({m['clave'] for m in result.matches}) == 3


@pytest.mark.parametrize('path', ['tarea', 'contexto', 'destinatario', 'restricciones', 'detalle', 'finalidad', 'libre', 'objetivo'])
def test_new_detector_uses_all_existing_fields(evaluate_base, data, path):
    value = deepcopy(next(c['entrada'] for c in data['cases'] if c['id'] == 'CP-33'))
    rules = deepcopy(data['rules'])
    next(r for r in rules if r['criterio_codigo'] == 'C6')['parametros']['detectores_activos'].append(NUMERIC_DETECTOR)
    objective = None
    if path in ('tarea','contexto','destinatario','restricciones'):
        value['componentes'][path]['texto'] = '1234567'
    elif path == 'detalle': value['componentes']['formato']['detalle'] = '1234567'
    elif path == 'finalidad': value['componentes']['contexto']['campos']['finalidad'] = '1234567'
    elif path == 'libre':
        value['modo'] = 'libre'; value['texto_libre'] = '1234567'; value['componentes_confirmados'] = True
    else: objective = '1234567'
    preview = evaluate_base(case='CP-33', draft=value, rules=rules, objective=objective)
    assert len(preview.matches) == 1
    assert preview.results[5]['estado'] == 'advertencia'
    approved = evaluate_base(case='CP-33', draft=value, rules=rules, objective=objective,
                             confirmation=confirm(preview, [m['clave'] for m in preview.matches]))
    assert approved.saveable and approved.results[5]['estado'] == 'cumple'
    assert approved.matches[0]['confirmada'] is True
    assert '1234567' not in str(approved.results) + str(approved.matches)
