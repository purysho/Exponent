"""Multifractal detrended fluctuation analysis (Kantelhardt et al.), q = 2.

Profile = cumulative sum of the demeaned series; for each scale s, detrend
non-overlapping windows with an order-`order` polynomial and take the q-th
order fluctuation F_q(s). The slope of log F_q against log s is h(q); the
profile adds one order of integration, so H = h(2) − 1.

Settings follow Lumor's roughvollab (ported, MIT licence; see NOTICE).
"""

from __future__ import annotations

import numpy as np

from exponent.domain.estimators.roughness._series import log_series
from exponent.domain.types import Estimate, Observation, Status


def mfdfa_h(x: np.ndarray, q: float = 2.0, order: int = 1, n_scales: int = 14) -> Estimate:
    n = x.size
    if n < 64:
        return Estimate(Status.FAILED, None, note=f"series too short: {n}")
    profile = np.cumsum(x - x.mean())
    scales = np.unique(np.round(np.logspace(np.log10(8), np.log10(n // 4), n_scales)).astype(int))
    F = np.empty(scales.size)
    for k, s in enumerate(scales):
        n_win = n // s
        segs = profile[: n_win * s].reshape(n_win, s).T  # (s, n_win): one column per window
        t = np.arange(s, dtype=np.float64)
        coef = np.polyfit(t, segs, order)
        resid = segs - np.vander(t, order + 1) @ coef
        segvar = np.mean(resid**2, axis=0)
        F[k] = np.mean(segvar ** (q / 2.0)) ** (1.0 / q)
    good = np.isfinite(F) & (F > 0)
    h = float(np.polyfit(np.log(scales[good]), np.log(F[good]), 1)[0])
    return Estimate.ok(h - 1.0, h_q=h)


def mfdfa(obs: Observation) -> Estimate:
    return mfdfa_h(log_series(obs))
