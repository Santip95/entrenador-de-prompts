from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import pytest

from app.application.fixture_evaluation import fixture_context
from app.domain.evaluation import (
    CODES, DETECTORS, EvaluationError, MOTOR_VERSION, canonical, compare, comprehension,
    confirm, review_objective, rounded_ratio, transfer,
)


def draft(data, code="CP-01"):
    return deepcopy(next(item["entrada"] for item in data["cases"] if item["id"] == code))


def configuration(data):
    return deepcopy(data["challenges"]["D01_CORREO_REUNION"]["configuracion"])


def test_detector_definitions_match_specification():
    path = Path(__file__).resolve().parents[3] / "seeds" / "rules.json"
    seed = json.loads(path.read_text(encoding="utf-8"))
    assert MOTOR_VERSION == seed["motor_version"]
    for detector in seed["detectores_permitidos"]:
        kind, expression, group, minimum, maximum = DETECTORS[detector["codigo"]]
        assert (kind, expression.pattern, group, minimum, maximum) == (
            detector["tipo"], detector["regex"], detector["grupo_valor"], detector["digitos_min"], detector["digitos_max"])


def test_evidence_and_matches_do_not_echo_sensitive_fragments(evaluate_base, data, capsys):
    value = draft(data)
    secret = "persona@example.invalid"
    value["componentes"]["tarea"]["texto"] = secret
    review = evaluate_base(draft=value)
    serialized = canonical([review.results, review.matches])
    assert secret not in serialized
    assert all(not ({"inicio", "fin", "fragmento", "huella"} & set(match)) for match in review.matches)
    assert secret not in repr(review)
    assert review.text.count(secret) == 1  # Guiado no vuelve a escanear el ensamblado.
    assert len(review.matches) == 1
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("field", ["contexto", "destinatario", "restricciones"])
def test_non_applicable_text_still_scanned(field, evaluate_base, data):
    value = draft(data, "CP-33")
    value["componentes"][field]["texto"] = "persona@example.invalid"
    review = evaluate_base(case="CP-33", draft=value)
    assert review.results[5]["estado"] == "advertencia"
    assert len(review.matches) == 1
    assert "persona@example.invalid" in review.text


def test_objective_review_and_later_evaluation(evaluate_base):
    context = fixture_context()
    review = review_objective("Contactar a persona@example.invalid", list(DETECTORS), context=context)
    assert review.matches[0]["campo"] == "objetivo"
    approved = confirm(review, [review.matches[0]["clave"]])
    assert review_objective(review.objective, list(DETECTORS), context=context, confirmation=approved).matches[0]["confirmada"]
    evaluation = evaluate_base(objective=review.objective)
    assert evaluation.results[5]["estado"] == "advertencia"
    assert "persona@example.invalid" not in evaluation.text  # No se ensambla el objetivo.
    with pytest.raises(EvaluationError, match="Revisá"):
        evaluate_base(objective=review.objective, confirmation=approved)  # No reutiliza confirmación inicial.


def test_partial_and_complete_confirmation(evaluate_base, data):
    value = draft(data)
    value["componentes"]["tarea"]["texto"] = "a@example.invalid y b@example.invalid"
    review = evaluate_base(draft=value)
    partial = evaluate_base(draft=value, confirmation=confirm(review, [review.matches[0]["clave"]]))
    assert partial.results[5]["estado"] == "advertencia" and not partial.saveable
    complete = evaluate_base(draft=value, confirmation=confirm(review, [m["clave"] for m in review.matches]))
    assert complete.results[5]["estado"] == "cumple" and complete.saveable
    assert len(complete.matches) == 2 and all(m["confirmada"] for m in complete.matches)
    assert "no garantiza" in complete.results[5]["mensaje"]


@pytest.mark.parametrize("change", ["text", "configuration", "subject", "practice", "key_version"])
def test_confirmation_invalidated_on_change(change, evaluate_base, data):
    value = draft(data, "CP-09")
    review = evaluate_base(draft=value)
    confirmation = confirm(review, [m["clave"] for m in review.matches])
    kwargs = {"draft": value, "confirmation": confirmation}
    if change == "text": value["componentes"]["contexto"]["texto"] += " Cambio"
    if change == "configuration":
        config = configuration(data)
        config["C5"]["parametros"]["exigir_detalle"] = False
        kwargs["configuration"] = config
    if change in ("subject", "practice", "key_version"):
        kwargs["context"] = replace(fixture_context(), **{change: "otro"})
    with pytest.raises(EvaluationError) as error:
        evaluate_base(**kwargs)
    assert error.value.code == "revision_desactualizada"


def test_unknown_confirmation_rejected(evaluate_base):
    with pytest.raises(EvaluationError):
        confirm(evaluate_base(), ["desconocida"])


def test_normalization_preserves_free_text(evaluate_base, data):
    value = draft(data, "CP-21")
    value["texto_libre"] = "  Cafe\u0301\r\n\rMantener <script>texto</script>  "
    review = evaluate_base(draft=value)
    assert review.text == "  Café\n\nMantener <script>texto</script>  "


def test_guided_order_labels_and_optional_content(evaluate_base, data):
    value = draft(data, "CP-33")
    value["componentes"]["contexto"]["texto"] = "  Contexto opcional  "
    value["componentes"]["destinatario"]["texto"] = "Público ficticio"
    value["componentes"]["restricciones"]["texto"] = "Condición escrita"
    value["componentes"]["restricciones"]["selecciones"] = ["sin_identificadores"]
    review = evaluate_base(case="CP-33", draft=value)
    titles = ["Tarea:", "Contexto:", "Destinatario:", "Restricciones:", "Formato:"]
    assert [review.text.index(t) for t in titles] == sorted(review.text.index(t) for t in titles)
    for expected in ("Acción: Explicar", "  Contexto opcional  ", "Público ficticio", "Condición escrita",
                     data["catalogs"]["restricciones"]["sin_identificadores"], "Texto"):
        assert expected in review.text


@pytest.mark.parametrize("length,valid", [(2000, True), (2001, False)])
def test_component_boundaries(length, valid, evaluate_base, data):
    value = draft(data)
    value["componentes"]["tarea"]["texto"] = "x" * length
    if valid:
        assert evaluate_base(draft=value).results[0]["estado"] == "cumple"
    else:
        with pytest.raises(EvaluationError): evaluate_base(draft=value)


@pytest.mark.parametrize("length,valid", [(10000, True), (10001, False)])
def test_free_text_boundaries(length, valid, evaluate_base, data):
    value = draft(data, "CP-21")
    value["texto_libre"] = "x" * length
    if valid:
        assert len(evaluate_base(draft=value).text) == length
    else:
        with pytest.raises(EvaluationError): evaluate_base(draft=value)


@pytest.mark.parametrize("objective,valid", [("", False), (" \t\n", False), ("x" * 1000, True),
                                           ("x" * 1001, False), (" " + "x" * 1000 + " ", True)])
def test_objective_boundaries(objective, valid, evaluate_base):
    if valid: evaluate_base(objective=objective)
    else:
        with pytest.raises(EvaluationError): evaluate_base(objective=objective)


def test_assembled_length_and_json_size_limits(evaluate_base, data):
    value = draft(data)
    for key in ("tarea", "contexto", "destinatario", "restricciones"):
        value["componentes"][key]["texto"] = "x" * 2000
    value["componentes"]["formato"]["detalle"] = "x" * 2000
    with pytest.raises(EvaluationError) as error: evaluate_base(draft=value)
    assert error.value.code == "limite_excedido"
    value["componentes"]["contexto"]["campos"] = {"finalidad": "x" * 2000, "fecha": "x" * 2000}
    value["modo"], value["componentes_confirmados"] = "libre", True
    value["texto_libre"] = "Texto pequeño"
    # JSON bajo el límite aún puede contener muchos valores; agregar hasta superar 20K.
    catalogs = deepcopy(data["catalogs"])
    for index in range(4):
        key = f"campo_{index}"
        catalogs["campos_contexto"][key] = key
        value["componentes"]["contexto"]["campos"][key] = "x" * 2000
    with pytest.raises(EvaluationError) as error: evaluate_base(draft=value, catalogs=catalogs)
    assert error.value.code == "limite_excedido"


@pytest.mark.parametrize("mutation", ["type", "missing", "duplicate", "unknown", "guided_free", "extra", "eleven"])
def test_invalid_drafts_rejected_safely(mutation, evaluate_base, data):
    value = draft(data)
    secret = "privado@example.invalid"
    value["componentes"]["tarea"]["texto"] = secret
    if mutation == "type": value["componentes"]["contexto"]["texto"] = 42
    if mutation == "missing": del value["componentes"]["tarea"]
    if mutation == "duplicate": value["componentes"]["restricciones"]["selecciones"] *= 2
    if mutation == "unknown": value["componentes"]["tarea"]["accion_id"] = secret
    if mutation == "guided_free": value["texto_libre"] = secret
    if mutation == "extra": value["componentes"]["tarea"][secret] = secret
    if mutation == "eleven": value["componentes"]["contexto"]["campos"] = {str(k): "x" for k in range(11)}
    with pytest.raises(EvaluationError) as error: evaluate_base(draft=value)
    assert secret not in str(error.value) and secret not in repr(error.value)


@pytest.mark.parametrize("mutation", ["missing_rule", "inactive", "duplicate", "unknown_type", "operator", "regex", "vacuous_c2",
                                    "vacuous_c4", "mandatory", "missing_c6", "disable_c1", "unknown_parameter"])
def test_invalid_configuration_fails_closed(mutation, evaluate_base, data):
    config, rules = configuration(data), deepcopy(data["rules"])
    if mutation == "missing_rule": rules.pop(0)
    if mutation == "inactive": rules[0]["activa"] = False
    if mutation == "duplicate": rules.append(deepcopy(rules[0]))
    if mutation == "unknown_type": rules[0]["tipo"] = "ejecutar_python"
    if mutation == "operator": rules[0]["parametros"]["combinacion"] = "OR"
    if mutation == "regex": rules[5]["parametros"]["detectores_activos"] = ["regex_arbitraria"]
    if mutation == "vacuous_c2": config["C2"]["parametros"] = {"campos_requeridos": [], "exigir_texto": False}
    if mutation == "vacuous_c4": config["C4"]["parametros"] = {"selecciones_requeridas": [], "exigir_texto": False}
    if mutation == "mandatory": config["C3"]["obligatorio"] = False
    if mutation == "missing_c6": del config["C6"]
    if mutation == "disable_c1": config["C1"]["aplica"] = config["C1"]["obligatorio"] = False
    if mutation == "unknown_parameter": config["C1"]["parametros"]["eval"] = "print('no')"
    with pytest.raises(EvaluationError) as error: evaluate_base(configuration=config, rules=rules)
    assert error.value.status == 503


def test_comparison_and_comparability(evaluate_base, data):
    first, second = evaluate_base(case="CP-31"), evaluate_base()
    assert compare(first, second)["delta_pp"] == 50
    assert compare(first, second)["resolucion"] == 100
    assert compare(first, second)["mejora_estructural"]
    assert compare(second, second)["resolucion"] is None
    assert transfer(second, evaluate_base(case="CP-32")) == 0
    config = configuration(data)
    config["C5"]["parametros"]["exigir_detalle"] = False
    changed = evaluate_base(configuration=config)
    assert not compare(first, changed)["comparable"]
    assert compare(first, changed)["delta_pp"] is None
    assert transfer(first, changed) is None


def test_names_and_messages_are_snapshotted_but_not_in_signature(evaluate_base, data):
    first = evaluate_base()
    names, rules = deepcopy(data["criteria"]), deepcopy(data["rules"])
    names["C1"]["nombre"] = "Tarea actualizada"
    rules[0]["mensajes"]["cumple"] = "Nuevo mensaje"
    second = evaluate_base(criteria=names, rules=rules)
    assert first.signature == second.signature
    assert first.snapshot["criterios"]["C1"]["nombre"] == "Tarea"
    assert second.snapshot != first.snapshot


def test_changed_and_repeated_alerts_and_key_rotation(evaluate_base, data):
    first = evaluate_base(case="CP-09")
    value = draft(data, "CP-09")
    value["componentes"]["tarea"]["texto"] = "Otra persona: distinta@example.invalid"
    second = evaluate_base(draft=value)
    assert compare(first, second)["alertas_nuevas"] == 1
    assert not compare(first, second)["mejora_estructural"]
    value["componentes"]["tarea"]["texto"] = "persona@example.invalid persona@example.invalid"
    assert compare(first, evaluate_base(draft=value))["alertas_nuevas"] == 1
    rotated = evaluate_base(case="CP-09", context=replace(fixture_context(), key_version="2", fingerprint_key=b"z" * 32))
    assert compare(first, rotated)["alertas_nuevas"] is None
    assert "No se pudo determinar" in compare(first, rotated)["aviso_alertas"]


def test_zero_denominators_and_human_counts():
    assert rounded_ratio(0, 0) is None
    assert comprehension(0, 0) is None
    assert comprehension(2, 4) == 50
    with pytest.raises(EvaluationError): comprehension(3, 2)


def test_evaluate_works_when_io_is_forbidden(evaluate_base, monkeypatch):
    import builtins
    import socket
    # Cargar la dependencia antes de bloquear E/S: su importación no es trabajo
    # del motor y puede inicializar módulos estándar como ssl/asyncio.
    import sqlalchemy

    def denied(*args, **kwargs):
        raise AssertionError("El motor intentó una operación de entrada/salida")

    monkeypatch.setattr(builtins, "open", denied)
    monkeypatch.setattr(Path, "open", denied)
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(sqlalchemy, "create_engine", denied)
    assert evaluate_base().fulfilled == 6


def test_domain_imports_with_standard_library_only():
    root = Path(__file__).resolve().parents[2]
    code = "import sys; sys.path.insert(0, sys.argv[1]); from app.domain.evaluation import MOTOR_VERSION; print(MOTOR_VERSION)"
    result = subprocess.run([sys.executable, "-I", "-S", "-c", code, str(root)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == MOTOR_VERSION


@pytest.mark.parametrize("size,valid", [(19999, True), (20000, True), (20001, False)])
def test_normalized_json_exact_boundaries(size, valid, evaluate_base, data):
    value = draft(data, "CP-21")
    catalogs = deepcopy(data["catalogs"])
    fields = value["componentes"]["contexto"]["campos"]
    for index in range(8):
        catalogs["campos_contexto"][f"k{index}"] = f"Etiqueta {index}"
        fields[f"k{index}"] = ""
    targets = [(value["componentes"][key], "texto") for key in ("tarea", "contexto", "destinatario", "restricciones")]
    targets += [(value["componentes"]["formato"], "detalle")]
    targets += [(fields, key) for key in fields]
    remaining = size - len(canonical(value["componentes"]))
    for container, key in targets:
        amount = min(2000 - len(container[key]), remaining)
        container[key] += "x" * amount
        remaining -= amount
    assert remaining == 0 and len(canonical(value["componentes"])) == size
    if valid: evaluate_base(draft=value, catalogs=catalogs)
    else:
        with pytest.raises(EvaluationError) as error: evaluate_base(draft=value, catalogs=catalogs)
        assert error.value.code == "limite_excedido"


@pytest.mark.parametrize("count,valid", [(10, True), (11, False)])
def test_selection_count_boundaries(count, valid, evaluate_base, data):
    value, catalogs = draft(data), deepcopy(data["catalogs"])
    values = [f"condicion_{i}" for i in range(count)]
    catalogs["restricciones"].update({key: "Condición ficticia" for key in values})
    value["componentes"]["restricciones"]["selecciones"] = values
    if valid: evaluate_base(draft=value, catalogs=catalogs)
    else:
        with pytest.raises(EvaluationError): evaluate_base(draft=value, catalogs=catalogs)


def test_empty_draft_not_saveable_but_partial_missing_task_is(evaluate_base, data):
    value = draft(data)
    for key in ("tarea", "contexto", "destinatario", "restricciones"):
        value["componentes"][key]["texto"] = ""
    value["componentes"]["contexto"]["campos"] = {}
    value["componentes"]["tarea"]["accion_id"] = None
    value["componentes"]["formato"] = {"tipo": None, "detalle": ""}
    value["componentes"]["restricciones"]["selecciones"] = []
    assert not evaluate_base(draft=value).saveable
    value["componentes"]["contexto"]["texto"] = "Contenido parcial"
    review = evaluate_base(draft=value)
    assert review.saveable and review.results[0]["estado"] == "revisar"
