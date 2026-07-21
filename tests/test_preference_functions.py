import math

from promethee_core.model import PreferenceFunctionType
from promethee_core.preference_functions import (
    compute_preference,
    gaussian,
    level,
    linear,
    u_shape,
    usual,
    v_shape,
)


def test_usual():
    assert usual(-1) == 0.0
    assert usual(0) == 0.0
    assert usual(0.0001) == 1.0
    assert usual(5) == 1.0


def test_u_shape():
    q = 2.0
    assert u_shape(-1, q=q) == 0.0
    assert u_shape(1.9, q=q) == 0.0
    assert u_shape(2.0, q=q) == 1.0
    assert u_shape(10, q=q) == 1.0


def test_v_shape():
    p = 4.0
    assert v_shape(-1, p=p) == 0.0
    assert v_shape(0, p=p) == 0.0
    assert v_shape(2, p=p) == 0.5
    assert v_shape(4, p=p) == 1.0
    assert v_shape(8, p=p) == 1.0


def test_level():
    q, p = 1.0, 3.0
    assert level(0.5, q=q, p=p) == 0.0
    assert level(2.0, q=q, p=p) == 0.5
    assert level(3.5, q=q, p=p) == 1.0


def test_linear():
    q, p = 1.0, 3.0
    assert linear(0.5, q=q, p=p) == 0.0
    assert linear(2.0, q=q, p=p) == 0.5
    assert linear(3.5, q=q, p=p) == 1.0


def test_gaussian():
    s = 2.0
    assert gaussian(-1, s=s) == 0.0
    assert gaussian(0, s=s) == 0.0
    expected = 1.0 - math.exp(-(3.0 ** 2) / (2.0 * s ** 2))
    assert math.isclose(gaussian(3.0, s=s), expected)


def test_dispatch():
    assert compute_preference(5, PreferenceFunctionType.USUAL) == 1.0
    assert compute_preference(-5, PreferenceFunctionType.GAUSSIAN, s=1.0) == 0.0
