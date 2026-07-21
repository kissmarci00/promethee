"""Reproduces the car-purchase worked example from PROMETHEE.pdf (pages 5-7)."""
import numpy as np
import pytest

from promethee_core.core import compute_promethee
from promethee_core.model import ProblemData
from promethee_core.sample import ALTERNATIVE_NAMES as ALT_ORDER
from promethee_core.sample import car_purchase_example

EXPECTED_P1 = np.array(
    [
        [0, 0.83, 0.03, 0.63, 0, 0.23],
        [0, 0, 0, 0, 0, 0],
        [0, 0.8, 0, 0.6, 0, 0.2],
        [0, 0.2, 0, 0, 0, 0],
        [0.7, 1, 0.73, 1, 0, 0.93],
        [0, 0.6, 0, 0.4, 0, 0],
    ]
)

EXPECTED_P2 = np.array(
    [
        [0, 0, 0.2, 0, 1, 0],
        [0, 0, 0.4, 0, 1, 0],
        [0, 0, 0, 0, 0.8, 0],
        [0, 0, 0.2, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [0.8, 0.6, 1, 0.8, 1, 0],
    ]
)

EXPECTED_P3 = np.array(
    [
        [0, 0.75, 0.5, 1, 0.25, 1],
        [0, 0, 0, 0.25, 0, 0.25],
        [0, 0.25, 0, 0.5, 0, 0.5],
        [0, 0, 0, 0, 0, 0],
        [0, 0.5, 0.25, 0.75, 0, 0.75],
        [0, 0, 0, 0, 0, 0],
    ]
)

EXPECTED_P4 = np.array(
    [
        [0, 0, 0, 0, 0.5, 1],
        [0, 0, 0, 0, 0.5, 1],
        [0, 0, 0, 0, 0, 0.5],
        [0, 0, 0.5, 0, 1, 1],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]
)

EXPECTED_P5 = np.array(
    [
        [0, 0, 0, 0, 0.5, 0.5],
        [0.5, 0, 0.5, 0.5, 1, 1],
        [0, 0, 0, 0, 0.5, 0.5],
        [0.5, 0, 0.5, 0, 1, 0.5],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0.5, 0],
    ]
)

EXPECTED_P = np.array(
    [
        [0, 0.32, 0.15, 0.33, 0.45, 0.55],
        [0.10, 0, 0.18, 0.15, 0.50, 0.45],
        [0.00, 0.21, 0, 0.22, 0.26, 0.34],
        [0.10, 0.04, 0.24, 0, 0.60, 0.30],
        [0.14, 0.30, 0.20, 0.35, 0, 0.34],
        [0.16, 0.24, 0.20, 0.24, 0.30, 0],
    ]
)

EXPECTED_PHI_PLUS = np.array([0.3573, 0.2760, 0.2060, 0.2560, 0.2647, 0.2280])
EXPECTED_PHI_MINUS = np.array([0.1000, 0.2213, 0.1927, 0.2573, 0.4220, 0.3947])
EXPECTED_PHI_NET = np.array([0.2573, 0.0547, 0.0133, -0.0013, -0.1573, -0.1667])


@pytest.fixture
def car_problem() -> ProblemData:
    return car_purchase_example()


def test_unicriterion_preference_matrices(car_problem):
    result = compute_promethee(car_problem)
    assert result.alternative_names == ALT_ORDER
    np.testing.assert_allclose(result.criterion_matrices["Price"], EXPECTED_P1, atol=0.01)
    np.testing.assert_allclose(result.criterion_matrices["Power"], EXPECTED_P2, atol=0.01)
    np.testing.assert_allclose(result.criterion_matrices["Consumption"], EXPECTED_P3, atol=0.01)
    np.testing.assert_allclose(result.criterion_matrices["Habitability"], EXPECTED_P4, atol=0.01)
    np.testing.assert_allclose(result.criterion_matrices["Comfort"], EXPECTED_P5, atol=0.01)


def test_aggregated_preference_matrix(car_problem):
    result = compute_promethee(car_problem)
    np.testing.assert_allclose(result.aggregated_matrix, EXPECTED_P, atol=0.01)


def test_flows(car_problem):
    result = compute_promethee(car_problem)
    np.testing.assert_allclose(result.phi_plus, EXPECTED_PHI_PLUS, atol=0.001)
    np.testing.assert_allclose(result.phi_minus, EXPECTED_PHI_MINUS, atol=0.001)
    np.testing.assert_allclose(result.phi_net, EXPECTED_PHI_NET, atol=0.001)


def test_rankings(car_problem):
    result = compute_promethee(car_problem)
    assert result.ranking_positive == ["A1", "A2", "A5", "A4", "A6", "A3"]
    assert result.ranking_negative == ["A1", "A3", "A2", "A4", "A6", "A5"]
    assert result.ranking_net == ["A1", "A2", "A3", "A4", "A5", "A6"]


def test_inactive_alternative_excluded(car_problem):
    car_problem.alternatives[-1].active = False  # drop A6
    result = compute_promethee(car_problem)
    assert "A6" not in result.alternative_names
    assert len(result.alternative_names) == 5


def test_weight_normalization(car_problem):
    for c in car_problem.criteria:
        c.weight = 2.0
    weights = car_problem.normalized_weights()
    assert pytest.approx(sum(weights.values())) == 1.0
    assert all(pytest.approx(w) == 1 / 5 for w in weights.values())
