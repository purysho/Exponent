"""Two p-variation roughness estimators that are often conflated.

`cont_das` is the normalised p-th variation of Cont and Das (2024), eqs. 5–7:

    W(p) = Σ_i  |X(t^K_{i+1}) − X(t^K_i)|^p / Σ_{j ∈ block i} |X(t^L_{j+1}) − X(t^L_j)|^p · Δt^K

with the fine partition π^L the observation grid and the coarse partition π^K
its K equal blocks. The roughness index is H = 1/p̂ where W(p̂) = T. Heuristic:
the ratio scales like (L/K)^{pH − 1}, so log W crosses zero at p = 1/H.

`scaling_crossing` is the estimator Lumor's roughvollab ships under the name
"Cont-Das": it regresses log Σ|x_{t+s} − x_t|^p on log s and finds the p at
which that slope, (1 − pH), changes sign. It is a different statistic, so the
court registers it under its own name.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.special import logsumexp

from exponent.domain.estimators.roughness._series import log_series, raw_series
from exponent.domain.types import Estimate, Observation, Status

H_SCAN = np.linspace(0.005, 0.995, 397)


def _log_w(p: float, log_coarse: np.ndarray, log_fine: np.ndarray) -> float:
    """log W(p) with T = 1, so Δt^K = 1/K and W is a mean over blocks."""
    log_ratio = p * log_coarse - logsumexp(p * log_fine, axis=1)
    return float(logsumexp(log_ratio) - np.log(log_ratio.size))


def normalized_pvariation(x: np.ndarray, K: int) -> Estimate:
    n_fine = x.size - 1
    m = n_fine // K
    if K < 2 or m < 2:
        return Estimate(Status.FAILED, None, note=f"need ≥2 blocks of ≥2 steps; n={x.size}")
    x = x[: K * m + 1]
    with np.errstate(divide="ignore"):
        log_fine = np.log(np.abs(np.diff(x))).reshape(K, m)
        log_coarse = np.log(np.abs(x[m::m] - x[:-m:m]))
    keep = np.isfinite(log_fine).any(axis=1)  # a block of exact zeros has no scale
    log_fine, log_coarse = log_fine[keep], log_coarse[keep]

    f = np.array([_log_w(1.0 / h, log_coarse, log_fine) for h in H_SCAN])
    s = np.sign(f)
    idx = np.flatnonzero(s[:-1] * s[1:] < 0)
    if idx.size == 0:
        return Estimate(Status.NO_ROOT, None, {"min_abs_log_w": float(np.min(np.abs(f)))})
    roots = [
        brentq(lambda h: _log_w(1.0 / h, log_coarse, log_fine), H_SCAN[i], H_SCAN[i + 1])
        for i in idx
    ]
    if len(roots) > 1:
        return Estimate(
            Status.AMBIGUOUS, None, {"n_roots": float(len(roots)), "first_root": roots[0]}
        )
    return Estimate.ok(float(roots[0]), K=float(K), m=float(m))


def cont_das(obs: Observation, K: int | None = None) -> Estimate:
    """Model-free: applied to the series as observed (σ, RV, or log-vol)."""
    x = raw_series(obs)
    return normalized_pvariation(x, K or int(np.sqrt(x.size - 1)))


# ── Lumor's variant (ported from roughvollab, MIT licence; see NOTICE) ─────────

P_GRID = np.linspace(1.0, 22.0, 85)


def _scaling_exponent(x: np.ndarray, p: float, max_scale: int = 64) -> float:
    n = x.size - 1
    scales = np.unique(np.round(np.logspace(0, np.log10(max_scale), 12)).astype(int))
    scales = scales[scales < n // 4]
    if scales.size < 3:
        return np.nan
    vals = np.array([np.sum(np.abs(x[s::s] - x[:-s:s]) ** p) for s in scales])
    good = vals > 0
    if good.sum() < 3:
        return np.nan
    return float(np.polyfit(np.log(scales[good]), np.log(vals[good]), 1)[0])


def scaling_crossing(obs: Observation) -> Estimate:
    x = log_series(obs)
    exps = np.array([_scaling_exponent(x, p) for p in P_GRID])
    ok = np.isfinite(exps)
    pg, e = P_GRID[ok], exps[ok]
    cross = np.flatnonzero(np.diff(np.sign(e)) != 0)
    if cross.size == 0:
        return Estimate(Status.NO_ROOT, None)
    j = int(cross[0])  # Lumor takes the first crossing; we record how many there were
    p_star = pg[j] - e[j] * (pg[j + 1] - pg[j]) / (e[j + 1] - e[j])
    if p_star <= 0:
        return Estimate(Status.FAILED, None, note="non-positive critical power")
    return Estimate.ok(1.0 / p_star, n_crossings=float(cross.size))
