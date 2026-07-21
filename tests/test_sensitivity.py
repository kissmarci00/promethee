import copy

import numpy as np
import pandas as pd
import pytest

from promethee_core.core import compute_promethee
from promethee_core.model import Alternative, Criterion, Direction, PreferenceFunctionType, ProblemData
from promethee_core.sensitivity import WeightSensitivity, compute_weight_sensitivity


@pytest.fixture
def small_problem() -> ProblemData:
    alternatives = [Alternative(name=n) for n in ["A1", "A2", "A3"]]
    criteria = [
        Criterion(name="C1", direction=Direction.MAX, weight=2.0,
                  preference_function=PreferenceFunctionType.USUAL),
        Criterion(name="C2", direction=Direction.MAX, weight=1.0,
                  preference_function=PreferenceFunctionType.USUAL),
        Criterion(name="C3", direction=Direction.MAX, weight=1.0,
                  preference_function=PreferenceFunctionType.USUAL),
    ]
    values = pd.DataFrame(
        {"C1": [10, 5, 1], "C2": [1, 8, 6], "C3": [3, 2, 9]}, index=["A1", "A2", "A3"]
    )
    return ProblemData(name="Test", alternatives=alternatives, criteria=criteria, values=values)


def test_flow_at_endpoints_match_direct_computation(small_problem):
    result = compute_promethee(small_problem)
    sens = compute_weight_sensitivity(result, "C1")

    # w=1 endpoint: only C1 active => flow_at(1) should equal the unicriterion flow.
    only_c1 = copy.deepcopy(small_problem)
    for c in only_c1.criteria:
        c.active = c.name == "C1"
    unicriterion_result = compute_promethee(only_c1)
    np.testing.assert_allclose(sens.flow_at(1.0), unicriterion_result.phi_net, atol=1e-9)

    # w=0 endpoint: C1 dropped, C2/C3 renormalized.
    without_c1 = copy.deepcopy(small_problem)
    without_c1.criteria = [c for c in without_c1.criteria if c.name != "C1"]
    dropped_result = compute_promethee(without_c1)
    np.testing.assert_allclose(sens.flow_at(0.0), dropped_result.phi_net, atol=1e-9)

    # w = original normalized weight: matches the original aggregated result.
    np.testing.assert_allclose(sens.flow_at(sens.w0), result.phi_net, atol=1e-9)


def test_stability_interval_bounds(small_problem):
    result = compute_promethee(small_problem)
    sens = compute_weight_sensitivity(result, "C1")
    w_low, w_high, crossings = sens.stability_interval(top_x=1)
    assert 0.0 <= w_low <= sens.w0 <= w_high <= 1.0


def test_stability_interval_detects_cascading_overtake():
    # A3 only overtakes the leader A1 by first overtaking A2 (a cascade):
    # f1 = 10 (constant), f2 = 9 - 0.1w, f3 = 8 + 5w.
    # A2/A3 cross at w~=0.196, and only then does A3 cross A1 at w=0.4.
    # A checker that only looks at the originally-adjacent pair (A1, A2)
    # would wrongly report the top-1 ranking as stable for all w in [0, 1].
    C = np.array([10.0, 9.0, 8.0])
    D = np.array([10.0, 8.9, 13.0])
    sens = WeightSensitivity(alt_names=["A1", "A2", "A3"], C=C, D=D, w0=0.0, criterion_name="X")

    w_low, w_high, _ = sens.stability_interval(top_x=1)

    assert w_low == pytest.approx(0.0)
    assert w_high == pytest.approx(0.4)


def test_single_active_criterion_raises(small_problem):
    for c in small_problem.criteria:
        c.active = c.name == "C1"
    result = compute_promethee(small_problem)
    with pytest.raises(ValueError):
        compute_weight_sensitivity(result, "C1")
