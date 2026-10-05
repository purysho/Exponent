import numpy as np
import pytest

from exponent.domain.estimators.registry import ROUGHNESS
from exponent.domain.estimators.roughness.pvariation import normalized_pvariation
from exponent.domain.generators.fgn import fbm
from exponent.domain.rng import cell_rng
from exponent.domain.types import (
    Estimand,
    Estimate,
    EstimatorSpec,
    SpotLogVol,
    SpotVol,
    Status,
    VolProxy,
)


@pytest.mark.parametrize("name", sorted(ROUGHNESS))
@pytest.mark.parametrize("H", [0.3, 0.7])
def test_recovers_h_on_exact_fbm(name: str, H: float) -> None:
    x = fbm(40_000, H, 1.0, cell_rng("recover", int(H * 10)))[0]
    est = ROUGHNESS[name](SpotLogVol(x))
    assert est.status is Status.OK
    assert est.value is not None and abs(est.value - H) < 0.05


def test_spec_refuses_an_observation_it_does_not_consume() -> None:
    spec = EstimatorSpec(
        "only-spot", "1", "", Estimand.H_LOG_VOL, (SpotVol,), lambda o: Estimate.ok(0.1)
    )
    with pytest.raises(TypeError):
        spec(SpotLogVol(np.zeros(10)))


def test_estimate_value_iff_ok() -> None:
    with pytest.raises(ValueError):
        Estimate(Status.OK, None)
    with pytest.raises(ValueError):
        Estimate(Status.NO_ROOT, 0.1)
    assert Estimate.ok(float("nan")).status is Status.FAILED


def test_pvariation_reports_too_short_as_failed() -> None:
    assert normalized_pvariation(np.arange(5.0), 10).status is Status.FAILED


def test_vol_proxy_log_series_converts_vol_to_log_variance() -> None:
    p = VolProxy(np.array([1.0, np.e]), 1, "test", "vol")
    np.testing.assert_allclose(p.log_series(), [0.0, 2.0])
    with pytest.raises(ValueError):
        VolProxy(np.ones(2), 1, "test", "bogus").log_series()


def test_degenerate_input_is_recorded_not_raised() -> None:
    est = ROUGHNESS["structure-function"](SpotLogVol(np.zeros(1000)))
    assert est.status is not Status.OK
