import io

import pandas as pd
import pytest

from promethee_core.io_utils import export_to_excel, import_from_excel
from promethee_core.model import Alternative, Criterion, ProblemData
from promethee_core.palette import DEFAULT_PALETTE, default_color


@pytest.fixture
def problem() -> ProblemData:
    alternatives = [Alternative(name=n) for n in ["A1", "A2", "A3"]]
    alternatives[1].color = "#123456"
    criteria = [Criterion(name=n) for n in ["C1", "C2"]]
    criteria[0].color = "#abcdef"
    values = pd.DataFrame({"C1": [1, 2, 3], "C2": [3, 2, 1]}, index=["A1", "A2", "A3"])
    return ProblemData(name="Test", alternatives=alternatives, criteria=criteria, values=values)


def test_unset_colors_fall_back_to_default_palette_by_position(problem):
    alt_colors = problem.alternative_colors()
    assert alt_colors["A1"] == default_color(0)
    assert alt_colors["A2"] == "#123456"  # explicit color always wins
    assert alt_colors["A3"] == default_color(2)

    crit_colors = problem.criterion_colors()
    assert crit_colors["C1"] == "#abcdef"
    assert crit_colors["C2"] == default_color(1)


def test_default_color_cycles_through_palette():
    assert default_color(0) == DEFAULT_PALETTE[0]
    assert default_color(len(DEFAULT_PALETTE)) == DEFAULT_PALETTE[0]


def test_color_round_trips_through_excel_export_import(problem):
    xlsx = export_to_excel(problem)
    reloaded, notes = import_from_excel(io.BytesIO(xlsx))

    assert notes == []
    assert {a.name: a.color for a in reloaded.alternatives} == {a.name: a.color for a in problem.alternatives}
    assert {c.name: c.color for c in reloaded.criteria} == {c.name: c.color for c in problem.criteria}
