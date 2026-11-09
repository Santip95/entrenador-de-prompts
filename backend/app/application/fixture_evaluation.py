"""Adaptador explícito para datos ficticios; nunca se conecta a PostgreSQL."""

from copy import deepcopy
import json
from pathlib import Path

from app.domain.evaluation import EvaluationContext, EvaluationError, confirm, evaluate


ROOT = Path(__file__).resolve().parents[3]


def load_fixture_data():
    def read(path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    return {
        "cases": read("fixtures/evaluation_cases.json")["casos"],
        "catalogs": read("seeds/catalogs.json"),
        "rules": read("seeds/rules.json")["reglas"],
        "criteria": {item["codigo"]: item for item in read("seeds/criteria.json")["criterios"]},
        "challenges": {item["codigo"]: item for item in read("seeds/challenges.json")["desafios"]},
    }


def fixture_context():
    # Datos ficticios EXCLUSIVOS de este adaptador de pruebas, sin validez en API.
    return EvaluationContext(b"revision-ficticia-de-fixtures-0001", b"huellas-ficticias-de-fixtures-0001",
                             "usuario-ficticio", "practica-ficticia")


def evaluate_case(case, data):
    configuration = (data["challenges"][case["desafio_codigo"]]["configuracion"]
                     if case.get("desafio_codigo") else case["configuracion_propia"])
    args = (case["entrada"], configuration, data["rules"], data["catalogs"], data["criteria"])
    review = evaluate(*args, context=fixture_context())
    if case.get("confirmar_todas"):
        # Sólo interpreta el estado explícito del corpus; el motor no acepta esta bandera.
        review = evaluate(*args, context=fixture_context(),
                          confirmation=confirm(review, [item["clave"] for item in review.matches]))
    return review


def expected_view(review):
    public = review.public()
    return {"estados": {r["criterio_codigo"]: r["estado"] for r in review.results},
            "cumplidos": public["cumplidos"], "aplicables": public["aplicables"],
            "cumplimiento_mostrado": public["cumplimiento_mostrado"],
            "coincidencias": [{"tipo": m["tipo"], "campo": m["campo"]} for m in review.matches]}


def run_corpus(data):
    report = []
    for case in data["cases"]:
        try:
            actual = expected_view(evaluate_case(deepcopy(case), data))
        except EvaluationError as error:
            actual = {"error": error.code}
        report.append({"id": case["id"], "esperado": deepcopy(case["esperado"]),
                       "obtenido": actual, "aprobado": actual == case["esperado"]})
    return report
