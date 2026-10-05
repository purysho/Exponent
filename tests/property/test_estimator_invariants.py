"""Invariants every roughness estimator must satisfy, whatever the path.

H describes how increments scale with lag, so it cannot depend on the units
of the series (positive rescaling) or its level (adding a constant).
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from exponent.app.court import run_one
from exponent.app.m0a import r1
from exponent.domain.estimators.registry import ROUGHNESS
from exponent.domain.generators.fgn import fbm
from exponent.domain.rng import cell_rng
from exponent.domain.types import SpotLogVol

_PATHS = {h: fbm(6000, h, 1.0, cell_rng("inv", int(h * 100)))[0] for h in (0.1, 0.4, 0.8)}


@settings(max_examples=25, deadline=None)
@given(
    h=st.sampled_from(sorted(_PATHS)),
    scale=st.floats(0.01, 100.0),
    shift=st.floats(-50.0, 50.0),
    name=st.sampled_from(sorted(ROUGHNESS)),
)
def test_invariant_to_units_and_level(h: float, scale: float, shift: float, name: str) -> None:
    x = _PATHS[h]
    a = ROUGHNESS[name](SpotLogVol(x))
    b = ROUGHNESS[name](SpotLogVol(scale * x + shift))
    assert a.status == b.status
    if a.value is not None:
        assert b.value is not None and abs(a.value - b.value) < 1e-6


def test_a_court_cell_is_reproducible_alone() -> None:
    exp = r1(reps=2, n=1000)
    assert run_one(exp, 3, 1) == run_one(exp, 3, 1)
    assert run_one(exp, 3, 0) != run_one(exp, 3, 1)


def test_cell_rng_streams_are_independent_of_order() -> None:
    a = cell_rng("k", 1, 2).standard_normal(5)
    cell_rng("k", 9, 9).standard_normal(1000)
    np.testing.assert_array_equal(a, cell_rng("k", 1, 2).standard_normal(5))
