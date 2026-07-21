"""Import/export for PROMETHEE problems.

Two formats are supported:

- **Excel** (.xlsx, 3 sheets: Meta / Criteria / Data) round-trips the full
  problem: name, description, every criterion setting (direction, weight,
  preference function, thresholds, active flag) and the raw data matrix.
  Import is deliberately lenient about hand-edited files: a missing column,
  or a blank cell in an optional column, is filled with the same default
  the Problem Setup page would use, and reported back as a note rather than
  raising. Only a missing name or an unparseable value (e.g. a typo in
  ``direction``) fails the import, with a message identifying the sheet,
  row and column at fault.
- **CSV** covers only the raw data matrix (alternatives x criteria values),
  for quick data exchange; imported criteria get default settings (max,
  Usual preference function, weight 1) that the user then adjusts in the
  Problem Setup page.
"""
from __future__ import annotations

import io
from typing import Callable

import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from promethee_core.model import Alternative, Criterion, Direction, PreferenceFunctionType, ProblemData

REQUIRED_SHEETS = ("Meta", "Criteria", "Data")


def export_to_excel(problem: ProblemData) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        meta_df = pd.DataFrame({"key": ["name", "description"], "value": [problem.name, problem.description]})
        meta_df.to_excel(writer, sheet_name="Meta", index=False)

        criteria_df = pd.DataFrame(
            [
                {
                    "name": c.name,
                    "direction": c.direction.value,
                    "weight": c.weight,
                    "preference_function": c.preference_function.value,
                    "q": c.q,
                    "p": c.p,
                    "s": c.s,
                    "active": int(c.active),
                    "color": c.color,
                }
                for c in problem.criteria
            ]
        )
        criteria_df.to_excel(writer, sheet_name="Criteria", index=False)

        # Constrain the preference_function column to a dropdown of valid values, so a
        # hand-edited file can't introduce a typo that would fail on re-import. Also
        # cover a couple of extra blank rows below the data, for criteria added by hand.
        if not criteria_df.empty:
            pref_col = get_column_letter(list(criteria_df.columns).index("preference_function") + 1)
            allowed = ",".join(pf.value for pf in PreferenceFunctionType)
            validation = DataValidation(type="list", formula1=f'"{allowed}"', allow_blank=False)
            validation.error = f"Choose one of: {allowed}"
            validation.errorTitle = "Invalid preference function"
            criteria_sheet = writer.sheets["Criteria"]
            criteria_sheet.add_data_validation(validation)
            validation.add(f"{pref_col}2:{pref_col}{len(criteria_df) + 20}")

        data_rows = []
        for a in problem.alternatives:
            row = {"name": a.name, "description": a.description, "active": int(a.active), "color": a.color}
            for c in problem.criteria:
                value = 0.0
                if a.name in problem.values.index and c.name in problem.values.columns:
                    value = problem.values.loc[a.name, c.name]
                row[c.name] = value
            data_rows.append(row)
        pd.DataFrame(data_rows).to_excel(writer, sheet_name="Data", index=False)

    return buffer.getvalue()


def _cast_direction(value) -> Direction:
    try:
        return Direction(value)
    except ValueError:
        valid = ", ".join(d.value for d in Direction)
        raise ValueError(f"'{value}' is not a valid direction (expected one of: {valid}).") from None


def _cast_preference_function(value) -> PreferenceFunctionType:
    try:
        return PreferenceFunctionType(value)
    except ValueError:
        valid = ", ".join(p.value for p in PreferenceFunctionType)
        raise ValueError(f"'{value}' is not a valid preference function (expected one of: {valid}).") from None


def _cast_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in ("true", "yes", "y", "1"):
        return True
    if text in ("false", "no", "n", "0"):
        return False
    raise ValueError(f"'{value}' is not a true/false value (expected e.g. TRUE/FALSE, yes/no, 1/0).")


def _read_column(df: pd.DataFrame, col: str, cast: Callable, default, label: str, sheet: str, notes: list[str]):
    """Read a column, filling missing/blank cells with ``default`` and noting it.

    A column missing entirely is one note; individual blank cells within an
    otherwise-present column are another. A value that IS present but fails
    ``cast`` (e.g. a typo) raises, since that's a mistake worth surfacing
    rather than silently overriding.
    """
    n = len(df)
    if col not in df.columns:
        notes.append(f"{sheet} sheet: no '{label}' column — used the default ({default}) for every row.")
        return [default] * n

    values = []
    blank_rows: list[int] = []
    for i, raw in enumerate(df[col]):
        if pd.isna(raw):
            values.append(default)
            blank_rows.append(i + 2)  # +2: 1-based, plus the header row
            continue
        try:
            values.append(cast(raw))
        except ValueError as exc:
            raise ValueError(f"{sheet} sheet, row {i + 2}, column '{label}': {exc}") from exc

    if blank_rows:
        rows_text = ", ".join(str(r) for r in blank_rows)
        notes.append(f"{sheet} sheet: '{label}' was blank in row(s) {rows_text} — used the default ({default}).")
    return values


def _optional_str_column(df: pd.DataFrame, col: str, default: str = "") -> list[str]:
    if col not in df.columns:
        return [default] * len(df)
    return [str(v) if pd.notna(v) else default for v in df[col]]


def _required_name_column(df: pd.DataFrame, sheet: str) -> list[str]:
    if "name" not in df.columns:
        raise ValueError(f"The {sheet} sheet is missing a 'name' column.")
    names = []
    for i, raw in enumerate(df["name"]):
        if pd.isna(raw) or str(raw).strip() == "":
            raise ValueError(f"{sheet} sheet, row {i + 2}: every row needs a name.")
        names.append(str(raw))
    return names


def import_from_excel(file) -> tuple[ProblemData, list[str]]:
    """Import a problem from Excel, returning it alongside a list of notes describing
    any missing/blank values that were filled in with defaults."""
    xls = pd.ExcelFile(file)
    missing_sheets = [s for s in REQUIRED_SHEETS if s not in xls.sheet_names]
    if missing_sheets:
        raise ValueError(
            f"This file is missing sheet(s): {', '.join(missing_sheets)}. "
            f"Expected sheets: {', '.join(REQUIRED_SHEETS)}."
        )

    meta = dict(zip(xls.parse("Meta")["key"], xls.parse("Meta")["value"]))
    criteria_df = xls.parse("Criteria")
    data_df = xls.parse("Data")

    notes: list[str] = []

    criterion_names = _required_name_column(criteria_df, "Criteria")
    directions = _read_column(criteria_df, "direction", _cast_direction, Direction.MAX, "direction", "Criteria", notes)
    weights = _read_column(criteria_df, "weight", float, 1.0, "weight", "Criteria", notes)
    pref_functions = _read_column(
        criteria_df, "preference_function", _cast_preference_function, PreferenceFunctionType.USUAL,
        "preference_function", "Criteria", notes,
    )
    qs = _read_column(criteria_df, "q", float, 0.0, "q", "Criteria", notes)
    ps = _read_column(criteria_df, "p", float, 1.0, "p", "Criteria", notes)
    ss = _read_column(criteria_df, "s", float, 1.0, "s", "Criteria", notes)
    crit_active = _read_column(criteria_df, "active", _cast_bool, True, "active", "Criteria", notes)
    crit_colors = _optional_str_column(criteria_df, "color")

    criteria = [
        Criterion(
            name=name, direction=direction, weight=weight, preference_function=pref, q=q, p=p, s=s,
            active=active, color=color,
        )
        for name, direction, weight, pref, q, p, s, active, color in zip(
            criterion_names, directions, weights, pref_functions, qs, ps, ss, crit_active, crit_colors
        )
    ]

    alt_names = _required_name_column(data_df, "Data")
    alt_active = _read_column(data_df, "active", _cast_bool, True, "active", "Data", notes)
    alt_descriptions = _optional_str_column(data_df, "description")
    alt_colors = _optional_str_column(data_df, "color")

    alternatives = [
        Alternative(name=name, description=desc, active=active, color=color)
        for name, desc, active, color in zip(alt_names, alt_descriptions, alt_active, alt_colors)
    ]

    value_columns = {
        cn: _read_column(data_df, cn, float, 0.0, cn, "Data", notes) for cn in criterion_names
    }
    values = pd.DataFrame(value_columns, index=alt_names).reindex(columns=criterion_names)

    problem = ProblemData(
        name=str(meta.get("name", "Imported problem")),
        description=str(meta.get("description", "")),
        alternatives=alternatives,
        criteria=criteria,
        values=values,
    )
    return problem, notes


def export_data_csv(problem: ProblemData) -> bytes:
    df = problem.values.copy()
    df.insert(0, "alternative", df.index)
    return df.to_csv(index=False).encode("utf-8")


def import_data_csv(file) -> ProblemData:
    df = pd.read_csv(file)
    alt_col = df.columns[0]
    criterion_names = [c for c in df.columns if c != alt_col]

    alt_names = df[alt_col].astype(str).tolist()
    values = df.set_index(alt_col)[criterion_names].astype(float)
    values.index = values.index.astype(str)

    alternatives = [Alternative(name=n) for n in alt_names]
    criteria = [Criterion(name=c) for c in criterion_names]

    return ProblemData(
        name="Imported data", alternatives=alternatives, criteria=criteria, values=values
    )
