import numpy as np
import pytest

from exponent.domain.generators.fgn import fbm, fgn, fgn_autocovariance
from exponent.domain.generators.vol_models import (
    hybrid_kernel,
    ou_sv,
    ou_sv_blocks,
    rough_bergomi,
)
from exponent.domain.observe.proxies import block_log_rv, rolling_realized_vol
from exponent.domain.rng import cell_rng


@pytest.mark.parametrize("H", [0.05, 0.1, 0.3, 0.5, 0.8])
def test_fgn_matches_theoretical_autocovariance(H: float) -> None:
    n_paths, n = 400, 512
    x = fgn(n, H, cell_rng("fgn-cov", int(H * 100)), n_paths)
    theory = fgn_autocovariance(4, H)
    for k in range(4):
        prod = x[:, : n - k] * x[:, k:]
        emp = prod.mean()
        se = prod.mean(axis=1).std() / np.sqrt(n_paths)
        assert abs(emp - theory[k]) < 5 * se + 1e-3, (k, emp, theory[k])


def test_fbm_has_variance_t_to_the_2h() -> None:
    n, H = 256, 0.2
    paths = fbm(n, H, 1.0 / n, cell_rng("fbm-var"), n_paths=4000)
    assert paths[:, 0].tolist() == [0.0] * 4000
    assert abs(paths[:, -1].var() - 1.0) < 0.07


def test_fgn_rejects_h_outside_unit_interval() -> None:
    with pytest.raises(ValueError):
        fgn(10, 1.0, cell_rng("x"))


def test_hybrid_kernel_is_brownian_at_half() -> None:
    g, v = hybrid_kernel(100, 0.5, 1.0)
    np.testing.assert_allclose(g, 1.0)
    np.testing.assert_allclose(v, np.arange(1, 101) / 100)


def test_rough_bergomi_log_variance_has_the_compensated_law() -> None:
    # log(V_T/ξ₀) = ηW̃_T − ½η²v_T is Gaussian with mean −½η²v_T and variance η²v_T,
    # which is what makes E[V_T] = ξ₀ exact. Testing the Gaussian is far sharper
    # than averaging the heavy-tailed lognormal itself.
    eta, n, reps = 1.5, 500, 3000
    v_T = hybrid_kernel(n, 0.1, 1.0)[1][-1]
    logs = np.array(
        [
            np.log(
                rough_bergomi(n, 1.0, 0.1, eta, -0.7, 0.04, cell_rng("rb", i)).variance[-1] / 0.04
            )
            for i in range(reps)
        ]
    )
    se = np.sqrt(eta**2 * v_T / reps)
    assert abs(logs.mean() + 0.5 * eta**2 * v_T) < 4 * se
    assert abs(logs.var() / (eta**2 * v_T) - 1.0) < 0.1


def test_ou_sv_blocks_rv_tracks_volatility() -> None:
    b = ou_sv_blocks(2000, 50, 1.0, 1.0, 1.0, 1.0, cell_rng("blocks"), chunk=137)
    ratio = b.block_rv / (b.vol_block_mean * np.sqrt(1.0 / 2000))
    assert abs(ratio.mean() - 1.0) < 0.01
    assert b.vol_at_block_ends.size == 2001


def test_rolling_rv_matches_naive_sum() -> None:
    path = ou_sv(1000, 1.0, 1.0, 1.0, 1.0, cell_rng("roll"))
    rv = rolling_realized_vol(path.log_price, 30)
    r = np.diff(path.log_price)
    naive = np.sqrt([np.sum(r[i : i + 30] ** 2) for i in range(r.size - 30 + 1)])
    np.testing.assert_allclose(rv.values, naive, rtol=1e-9)


def test_block_log_rv_drops_partial_block() -> None:
    x = np.cumsum(np.ones(105))
    obs = block_log_rv(x, 10)
    assert obs.values.size == 10  # 104 returns → 10 full blocks
    np.testing.assert_allclose(obs.values, np.log(10.0))
