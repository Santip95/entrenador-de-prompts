"""Ejecuta el corpus ficticio y muestra sólo resultados sin textos originales."""

import argparse
import json

from app.application.fixture_evaluation import load_fixture_data, run_corpus
from app.domain.evaluation import LIMITATION, MOTOR_VERSION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Informe esperado/obtenido sin textos del prompt")
    options = parser.parse_args()
    results = run_corpus(load_fixture_data())
    if options.json:
        print(json.dumps({"motor_version": MOTOR_VERSION, "casos": results}, ensure_ascii=False, indent=2))
    else:
        print(f"Motor {MOTOR_VERSION}; corpus ficticio, sin base de datos ni red.")
        for row in results:
            actual = row["obtenido"]
            detail = actual.get("error") or f"{actual['cumplidos']}/{actual['aplicables']} ({actual['cumplimiento_mostrado']} %)"
            print(f"{row['id']}: {'APROBADO' if row['aprobado'] else 'FALLO'} — {detail}")
        print(f"{sum(row['aprobado'] for row in results)}/{len(results)} casos aprobados; CP-12 reservado para etapa 04.")
        print(LIMITATION + ". El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad.")
    return 0 if all(row["aprobado"] for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
