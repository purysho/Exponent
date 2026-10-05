"""Observation operators: from a price path to the proxy an analyst can compute.

Two constructions are kept distinct because the papers being reproduced use
different ones, and the difference matters to the answer.
"""

from __future__ import annotations

import numpy as np

from exponent.domain.types import VolProxy


def rolling_realized_vol(log_price: np.ndarray, window: int) -> VolProxy:
    """Cont and Das, eq. (12): RV_t = √(Σ of the last `window` squared returns).

    Overlapping, one value per fine grid point from the first full window on,
    in volatility units (not log). Length = len(log_price) − window.
    """
    r2 = np.diff(log_price) ** 2
    c = np.concatenate([[0.0], np.cumsum(r2)])
    rv = np.sqrt(np.maximum(c[window:] - c[:-window], 0.0))
    return VolProxy(rv, window, "rolling_rv", "vol")


def block_log_rv(log_price: np.ndarray, window: int) -> VolProxy:
    """Lumor's proxy: log of RV over non-overlapping blocks of `window` returns.

    This is the daily log-RV series of the empirical literature when one block
    is one day. Trailing returns that do not fill a block are dropped.
    """
    r = np.diff(log_price)
    n_blocks = r.size // window
    rv = np.sum(r[: n_blocks * window].reshape(n_blocks, window) ** 2, axis=1)
    return VolProxy(np.log(rv + 1e-300), window, "block_log_rv", "log_var")
