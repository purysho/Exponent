"""Gatheral–Jaisson–Rosenbaum structure-function regression.

m(q, Δ) = mean |X_{t+Δ} − X_t|^q ∝ Δ^{ζ_q} with ζ_q = qH for a monofractal
path. ζ_q is the slope of log m against log Δ; H is the slope of ζ_q against q.
"""

from __future__ import annotations

import numpy as np

from exponent.domain.estimators.roughness._series import log_series
from exponent.domain.types import Estimate, Observation, Status

# Lumor's defaults (roughvollab layer1c), kept so reproductions compare like with like.
LAGS = (8, 13, 21, 34, 55, 89)
QS = (0.5, 1.0, 1.5, 2.0, 3.0)


def structure_function(
    x: np.ndarray, lags: tuple[int, ...] = LAGS, qs: tuple[float, ...] = QS
) -> Estimate:
    if x.size <= 4 * max(lags):
        return Estimate(Status.FAILED, None, note=f"series of {x.size} too short for lags")
    loglag = np.log(np.asarray(lags, dtype=np.float64))
    m = np.empty((len(qs), len(lags)))
    for j, lag in enumerate(lags):
        a = np.abs(x[lag:] - x[:-lag])
        for i, q in enumerate(qs):
            m[i, j] = np.mean(a**q)
    zeta = np.polyfit(loglag, np.log(m).T, 1)[0]
    slope, intercept = np.polyfit(np.asarray(qs), zeta, 1)
    fit = slope * np.asarray(qs) + intercept
    ss_tot = float(np.sum((zeta - zeta.mean()) ** 2))
    r2 = 1.0 - float(np.sum((zeta - fit) ** 2)) / ss_tot if ss_tot > 0 else 1.0
    return Estimate.ok(float(slope), monofractal_r2=r2)


def gjr(obs: Observation) -> Estimate:
    return structure_function(log_series(obs))
