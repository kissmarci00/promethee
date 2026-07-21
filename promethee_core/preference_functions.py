"""The six PROMETHEE preference functions.

Every function takes ``d``, the *already-oriented* difference between two
alternatives on one criterion (positive ``d`` means the first alternative is
preferred). Direction (max/min) is handled by the caller (see
:mod:`promethee_core.core`), which negates the raw value difference for
minimization criteria before calling into this module. This keeps each
function a pure, direction-agnostic formula straight out of the PROMETHEE
specification.

All functions return 0 for ``d <= 0``, matching the specification: a
non-positive difference means the alternative is not preferred.
"""
from __future__ import annotations

import math

from promethee_core.model import PreferenceFunctionType


def usual(d: float, **_) -> float:
    return 1.0 if d > 0 else 0.0


def u_shape(d: float, q: float = 0.0, **_) -> float:
    return 1.0 if d >= q else 0.0


def v_shape(d: float, p: float = 1.0, **_) -> float:
    if d <= 0:
        return 0.0
    if d >= p:
        return 1.0
    return d / p


def level(d: float, q: float = 0.0, p: float = 1.0, **_) -> float:
    if d <= q:
        return 0.0
    if d >= p:
        return 1.0
    return 0.5


def linear(d: float, q: float = 0.0, p: float = 1.0, **_) -> float:
    if d <= q:
        return 0.0
    if d >= p:
        return 1.0
    return (d - q) / (p - q)


def gaussian(d: float, s: float = 1.0, **_) -> float:
    if d <= 0:
        return 0.0
    return 1.0 - math.exp(-(d ** 2) / (2.0 * s ** 2))


_DISPATCH = {
    PreferenceFunctionType.USUAL: usual,
    PreferenceFunctionType.U_SHAPE: u_shape,
    PreferenceFunctionType.V_SHAPE: v_shape,
    PreferenceFunctionType.LEVEL: level,
    PreferenceFunctionType.LINEAR: linear,
    PreferenceFunctionType.GAUSSIAN: gaussian,
}


def compute_preference(
    d: float,
    preference_function: PreferenceFunctionType,
    q: float = 0.0,
    p: float = 1.0,
    s: float = 1.0,
) -> float:
    """Evaluate the requested preference function at oriented difference ``d``."""
    fn = _DISPATCH[preference_function]
    return fn(d, q=q, p=p, s=s)
