from copy import deepcopy

import pytest

from app.application.fixture_evaluation import evaluate_case, expected_view, load_fixture_data
from app.domain.evaluation import EvaluationError


CASES = load_fixture_data()["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_fixture(case, data):
    if "error" in case["esperado"]:
        with pytest.raises(EvaluationError) as caught:
            evaluate_case(case, data)
        assert caught.value.code == case["esperado"]["error"]
    else:
        assert expected_view(evaluate_case(case, data)) == case["esperado"]


@pytest.mark.parametrize("case", [c for c in CASES if "error" not in c["esperado"]], ids=lambda c: c["id"])
def test_repeatable_without_mutating_inputs(case, data):
    original = deepcopy(data)
    assert evaluate_case(case, data) == evaluate_case(case, data)
    assert data == original
