import io

import pandas as pd
import pytest

from promethee_core.io_utils import export_to_excel, import_from_excel
from promethee_core.model import Alternative, Criterion, Direction, PreferenceFunctionType, ProblemData


def _make_excel(meta_rows, criteria_rows, data_rows) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame(meta_rows).to_excel(writer, sheet_name="Meta", index=False)
        pd.DataFrame(criteria_rows).to_excel(writer, sheet_name="Criteria", index=False)
        pd.DataFrame(data_rows).to_excel(writer, sheet_name="Data", index=False)
    return buffer.getvalue()


def test_missing_optional_columns_get_defaults_and_notes():
    xlsx = _make_excel(
        meta_rows={"key": ["name", "description"], "value": ["T", ""]},
        # no weight, q, p, s, active, direction, preference_function columns at all
        criteria_rows={"name": ["C1", "C2"]},
        data_rows={"name": ["A1", "A2"], "C1": [1.0, 2.0], "C2": [3.0, 4.0]},
    )

    problem, notes = import_from_excel(io.BytesIO(xlsx))

    assert [c.direction for c in problem.criteria] == [Direction.MAX, Direction.MAX]
    assert [c.weight for c in problem.criteria] == [1.0, 1.0]
    assert [c.preference_function for c in problem.criteria] == [PreferenceFunctionType.USUAL] * 2
    assert [c.q for c in problem.criteria] == [0.0, 0.0]
    assert [c.p for c in problem.criteria] == [1.0, 1.0]
    assert [c.s for c in problem.criteria] == [1.0, 1.0]
    assert [c.active for c in problem.criteria] == [True, True]
    assert all(a.active for a in problem.alternatives)
    # one note per missing column that actually affects computation
    assert any("direction" in n for n in notes)
    assert any("weight" in n for n in notes)
    assert any("active" in n for n in notes)


def test_blank_cells_in_present_column_get_defaulted_with_note():
    xlsx = _make_excel(
        meta_rows={"key": ["name"], "value": ["T"]},
        criteria_rows={
            "name": ["C1", "C2"],
            "direction": ["max", "min"],
            "weight": [2.0, None],  # blank weight for C2
            "preference_function": ["usual", "usual"],
            "q": [0.0, 0.0], "p": [1.0, 1.0], "s": [1.0, 1.0],
            "active": [True, True],
        },
        data_rows={"name": ["A1"], "C1": [1.0], "C2": [2.0]},
    )

    problem, notes = import_from_excel(io.BytesIO(xlsx))

    weights = {c.name: c.weight for c in problem.criteria}
    assert weights == {"C1": 2.0, "C2": 1.0}
    assert any("weight" in n and "row(s) 3" in n for n in notes)


def test_missing_active_column_entirely_defaults_everything_active():
    xlsx = _make_excel(
        meta_rows={"key": ["name"], "value": ["T"]},
        criteria_rows={"name": ["C1"], "direction": ["max"], "weight": [1.0],
                        "preference_function": ["usual"], "q": [0.0], "p": [1.0], "s": [1.0]},
        data_rows={"name": ["A1", "A2"], "C1": [1.0, 2.0]},
    )

    problem, notes = import_from_excel(io.BytesIO(xlsx))

    assert all(a.active for a in problem.alternatives)
    assert all(c.active for c in problem.criteria)


def test_missing_name_column_raises_clear_error():
    xlsx = _make_excel(
        meta_rows={"key": ["name"], "value": ["T"]},
        criteria_rows={"direction": ["max"], "weight": [1.0]},
        data_rows={"name": ["A1"], "C1": [1.0]},
    )

    with pytest.raises(ValueError, match="Criteria sheet is missing a 'name' column"):
        import_from_excel(io.BytesIO(xlsx))


def test_invalid_preference_function_value_raises_clear_error():
    xlsx = _make_excel(
        meta_rows={"key": ["name"], "value": ["T"]},
        criteria_rows={
            "name": ["C1"], "direction": ["max"], "weight": [1.0],
            "preference_function": ["not_a_real_function"], "q": [0.0], "p": [1.0], "s": [1.0],
        },
        data_rows={"name": ["A1"], "C1": [1.0]},
    )

    with pytest.raises(ValueError, match="row 2.*preference_function.*not_a_real_function"):
        import_from_excel(io.BytesIO(xlsx))


def test_missing_sheet_raises_clear_error():
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({"key": ["name"], "value": ["T"]}).to_excel(writer, sheet_name="Meta", index=False)
        pd.DataFrame({"name": ["A1"]}).to_excel(writer, sheet_name="Data", index=False)

    with pytest.raises(ValueError, match="missing sheet.*Criteria"):
        import_from_excel(io.BytesIO(buffer.getvalue()))


def test_export_adds_dropdown_validation_on_preference_function_column():
    from openpyxl import load_workbook

    problem = ProblemData(
        name="T",
        alternatives=[Alternative(name="A1")],
        criteria=[Criterion(name="C1"), Criterion(name="C2")],
        values=pd.DataFrame({"C1": [1.0], "C2": [2.0]}, index=["A1"]),
    )
    xlsx = export_to_excel(problem)
    wb = load_workbook(io.BytesIO(xlsx))
    sheet = wb["Criteria"]
    assert len(sheet.data_validations.dataValidation) == 1
    validation = sheet.data_validations.dataValidation[0]
    assert validation.type == "list"
    for pf in PreferenceFunctionType:
        assert pf.value in validation.formula1
