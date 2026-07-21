"""Data model for a PROMETHEE decision problem.

This module has no Streamlit dependency: it is the single source of truth
for problem state, shared by every page through ``st.session_state``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import pandas as pd

from promethee_core.palette import default_color


class Direction(str, Enum):
    MAX = "max"
    MIN = "min"


class PreferenceFunctionType(str, Enum):
    USUAL = "usual"
    U_SHAPE = "u_shape"
    V_SHAPE = "v_shape"
    LEVEL = "level"
    LINEAR = "linear"
    GAUSSIAN = "gaussian"


PREFERENCE_FUNCTION_LABELS: dict[PreferenceFunctionType, str] = {
    PreferenceFunctionType.USUAL: "Usual",
    PreferenceFunctionType.U_SHAPE: "U-shape",
    PreferenceFunctionType.V_SHAPE: "V-shape",
    PreferenceFunctionType.LEVEL: "Level",
    PreferenceFunctionType.LINEAR: "Linear (V-shape with indifference)",
    PreferenceFunctionType.GAUSSIAN: "Gaussian",
}

# Which thresholds each preference function actually uses, for UI hints.
PREFERENCE_FUNCTION_PARAMS: dict[PreferenceFunctionType, tuple[str, ...]] = {
    PreferenceFunctionType.USUAL: (),
    PreferenceFunctionType.U_SHAPE: ("q",),
    PreferenceFunctionType.V_SHAPE: ("p",),
    PreferenceFunctionType.LEVEL: ("q", "p"),
    PreferenceFunctionType.LINEAR: ("q", "p"),
    PreferenceFunctionType.GAUSSIAN: ("s",),
}


@dataclass
class Criterion:
    name: str
    direction: Direction = Direction.MAX
    weight: float = 1.0
    preference_function: PreferenceFunctionType = PreferenceFunctionType.USUAL
    q: float = 0.0
    p: float = 1.0
    s: float = 1.0
    active: bool = True
    color: str = ""  # hex color; empty means "use the default palette"


@dataclass
class Alternative:
    name: str
    description: str = ""
    active: bool = True
    color: str = ""  # hex color; empty means "use the default palette"


@dataclass
class ProblemData:
    name: str = "New problem"
    description: str = ""
    alternatives: list[Alternative] = field(default_factory=list)
    criteria: list[Criterion] = field(default_factory=list)
    values: pd.DataFrame = field(default_factory=pd.DataFrame)

    # -- active-only accessors -------------------------------------------------

    def active_alternatives(self) -> list[Alternative]:
        return [a for a in self.alternatives if a.active]

    def active_criteria(self) -> list[Criterion]:
        return [c for c in self.criteria if c.active]

    def active_values(self) -> pd.DataFrame:
        alt_names = [a.name for a in self.active_alternatives()]
        crit_names = [c.name for c in self.active_criteria()]
        return self.values.reindex(index=alt_names, columns=crit_names).astype(float)

    def normalized_weights(self) -> dict[str, float]:
        crits = self.active_criteria()
        total = sum(c.weight for c in crits)
        if total <= 0:
            n = len(crits)
            return {c.name: (1.0 / n if n else 0.0) for c in crits}
        return {c.name: c.weight / total for c in crits}

    def alternative_colors(self) -> dict[str, str]:
        """Each active alternative's display color: its own if set, else the next default."""
        return {a.name: (a.color or default_color(i)) for i, a in enumerate(self.active_alternatives())}

    def criterion_colors(self) -> dict[str, str]:
        """Each active criterion's display color: its own if set, else the next default."""
        return {c.name: (c.color or default_color(i)) for i, c in enumerate(self.active_criteria())}

    # -- mutation helpers (keep `values` in sync with alternatives/criteria) ---

    def add_alternative(self, name: str, description: str = "") -> None:
        self.alternatives.append(Alternative(name=name, description=description))
        if self.values.columns.empty:
            # .loc[name] = 0.0 fails on a column-less frame ("cannot set a
            # frame with no defined columns"), so just extend the index.
            self.values = self.values.reindex(index=[*self.values.index, name])
        else:
            self.values.loc[name] = 0.0

    def remove_alternative(self, name: str) -> None:
        self.alternatives = [a for a in self.alternatives if a.name != name]
        if name in self.values.index:
            self.values = self.values.drop(index=name)

    def add_criterion(self, name: str, **kwargs) -> None:
        self.criteria.append(Criterion(name=name, **kwargs))
        self.values[name] = 0.0

    def remove_criterion(self, name: str) -> None:
        self.criteria = [c for c in self.criteria if c.name != name]
        if name in self.values.columns:
            self.values = self.values.drop(columns=name)

    def rename_alternative(self, old_name: str, new_name: str) -> None:
        if old_name == new_name:
            return
        for a in self.alternatives:
            if a.name == old_name:
                a.name = new_name
        if old_name in self.values.index:
            self.values = self.values.rename(index={old_name: new_name})

    def rename_criterion(self, old_name: str, new_name: str) -> None:
        if old_name == new_name:
            return
        for c in self.criteria:
            if c.name == old_name:
                c.name = new_name
        if old_name in self.values.columns:
            self.values = self.values.rename(columns={old_name: new_name})
