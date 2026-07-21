import io

import pandas as pd
import pytest

from promethee_core.gaia import compute_gaia, export_gaia_to_excel
from promethee_core.model import Alternative, Criterion, Direction, PreferenceFunctionType, ProblemData


@pytest.fixture
def small_problem() -> ProblemData:
    alternatives = [Alternative(name=n) for n in ["A1", "A2", "A3", "A4"]]
    criteria = [
        Criterion(name="C1", direction=Direction.MAX, weight=1.0,
                  preference_function=PreferenceFunctionType.USUAL),
        Criterion(name="C2", direction=Direction.MIN, weight=2.0,
                  preference_function=PreferenceFunctionType.USUAL),
        Criterion(name="C3", direction=Direction.MAX, weight=1.0,
                  preference_function=PreferenceFunctionType.USUAL),
    ]
    values = pd.DataFrame(
        {"C1": [10, 5, 1, 7], "C2": [1, 8, 6, 3], "C3": [3, 2, 9, 5]},
        index=["A1", "A2", "A3", "A4"],
    )
    return ProblemData(name="Test", alternatives=alternatives, criteria=criteria, values=values)


def test_shapes_and_quality(small_problem):
    gaia = compute_gaia(small_problem)
    assert gaia.alternative_coords.shape == (4, 2)
    assert gaia.criterion_coords.shape == (3, 2)
    assert gaia.pi_vector.shape == (2,)
    assert 0.0 <= gaia.quality <= 1.0 + 1e-9


def test_alternative_coords_are_centered(small_problem):
    gaia = compute_gaia(small_problem)
    # PCA projections of a centered matrix must average to (0, 0).
    assert gaia.alternative_coords.mean(axis=0) == pytest.approx([0.0, 0.0], abs=1e-9)


def test_export_gaia_to_excel_writes_exact_coordinates(small_problem):
    gaia = compute_gaia(small_problem)
    alt_colors = small_problem.alternative_colors()
    crit_colors = small_problem.criterion_colors()
    weights = small_problem.normalized_weights()

    xlsx = export_gaia_to_excel(gaia, alt_colors, crit_colors, weights)

    alt_df = pd.read_excel(io.BytesIO(xlsx), sheet_name="Alternatives")
    assert list(alt_df["alternative"]) == gaia.alternative_names
    assert alt_df["PC1"].to_numpy() == pytest.approx(gaia.alternative_coords[:, 0])
    assert alt_df["PC2"].to_numpy() == pytest.approx(gaia.alternative_coords[:, 1])
    assert list(alt_df["color"]) == [alt_colors[n] for n in gaia.alternative_names]

    crit_df = pd.read_excel(io.BytesIO(xlsx), sheet_name="Criteria")
    assert list(crit_df["criterion"]) == gaia.criterion_names
    assert crit_df["PC1"].to_numpy() == pytest.approx(gaia.criterion_coords[:, 0])
    assert crit_df["PC2"].to_numpy() == pytest.approx(gaia.criterion_coords[:, 1])

    pi_df = pd.read_excel(io.BytesIO(xlsx), sheet_name="Pi vector")
    assert pi_df.loc[0, "PC1"] == pytest.approx(gaia.pi_vector[0])
    assert pi_df.loc[0, "PC2"] == pytest.approx(gaia.pi_vector[1])
