"""Identifiability of a true H through an estimator + observation chain.

For fixed measurement conditions, the bias curve true H ↦ E[Ĥ] (with its
single-path spread σ) defines an inverse problem. A cell (one true H) is:

- NON_IDENTIFIED if the curve is not monotone (a rough and a smooth truth give
  the same Ĥ), or its local slope is below a floor (many truths collapse
  onto one Ĥ);
- IDENTIFIED if, additionally, the truth is rough (H < ½) and its E[Ĥ] differs
  from the smooth null's E[Ĥ | H = ½] by more than z·σ;
- DE_BIASABLE otherwise (a control cell with H ≥ ½, or a rough cell the
  smooth null cannot be told apart from);
- UNCALIBRATED if the estimator returned no value at that truth.

These rules, and their constants, are Lumor's (roughvollab
`identifiability_map.cell_status`, MIT; see NOTICE), ported so the M0a
reproduction classifies cells exactly as the paper did. The court may adopt
different rules later; it will do so under a new name.
"""

from __future__ import annotations

from enum import Enum

import numpy as np
import numpy.typing as npt

MONOTONE_TOL = 0.012
FLAT_SLOPE = 0.25
Z = 1.96
SMOOTH = 0.5


class CellStatus(Enum):
    IDENTIFIED = "identified"
    DE_BIASABLE = "de-biasable"
    NON_IDENTIFIED = "non-identified"
    UNCALIBRATED = "uncalibrated"


def is_monotone(mean: npt.ArrayLike, tol: float = MONOTONE_TOL) -> bool:
    m = np.asarray(mean, float)
    m = m[np.isfinite(m)]
    if m.size < 2:
        return True
    d = np.diff(m)
    return bool(np.all(d >= -tol) or np.all(d <= tol))


def local_slope(grid: npt.ArrayLike, mean: npt.ArrayLike, at: float) -> float:
    g, m = np.asarray(grid, float), np.asarray(mean, float)
    ok = np.isfinite(g) & np.isfinite(m)
    g, m = g[ok], m[ok]
    if g.size < 2:
        return float("nan")
    return float(np.interp(at, g, np.gradient(m, g)))


def cell_status(grid: npt.ArrayLike, mean: npt.ArrayLike, std: npt.ArrayLike, i: int) -> CellStatus:
    g, m, s = (np.asarray(a, float) for a in (grid, mean, std))
    if not np.isfinite(m[i]):
        return CellStatus.UNCALIBRATED
    if not is_monotone(m):
        return CellStatus.NON_IDENTIFIED
    slope = local_slope(g, m, g[i])
    if not np.isfinite(slope) or abs(slope) < FLAT_SLOPE:
        return CellStatus.NON_IDENTIFIED
    if g[i] >= SMOOTH:
        return CellStatus.DE_BIASABLE
    fin = np.isfinite(g) & np.isfinite(m)
    if fin.sum() < 2:
        return CellStatus.DE_BIASABLE
    m_smooth = float(np.interp(SMOOTH, g[fin], m[fin]))
    sigma = float(s[i]) if np.isfinite(s[i]) else 0.0
    return CellStatus.IDENTIFIED if abs(m[i] - m_smooth) > Z * sigma else CellStatus.DE_BIASABLE


def curve_statuses(
    grid: npt.ArrayLike, mean: npt.ArrayLike, std: npt.ArrayLike
) -> list[CellStatus]:
    return [cell_status(grid, mean, std, i) for i in range(np.asarray(grid).size)]
