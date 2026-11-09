from copy import deepcopy

import pytest

from app.application.fixture_evaluation import fixture_context, load_fixture_data
from app.domain.evaluation import evaluate


@pytest.fixture
def data():
    return load_fixture_data()


@pytest.fixture
def evaluate_base(data):
    def run(*, case="CP-01", draft=None, configuration=None, rules=None, catalogs=None,
            criteria=None, context=None, objective=None, confirmation=None):
        original = next(item for item in data["cases"] if item["id"] == case)
        config = (data["challenges"][original["desafio_codigo"]]["configuracion"]
                  if original.get("desafio_codigo") else original["configuracion_propia"])
        return evaluate(deepcopy(original["entrada"]) if draft is None else draft,
                        deepcopy(config) if configuration is None else configuration,
                        deepcopy(data["rules"]) if rules is None else rules,
                        deepcopy(data["catalogs"]) if catalogs is None else catalogs,
                        deepcopy(data["criteria"]) if criteria is None else criteria,
                        context=context or fixture_context(), objective=objective, confirmation=confirmation)
    return run
