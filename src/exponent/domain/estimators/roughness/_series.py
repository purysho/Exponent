"""How each estimator reads an observation."""

from __future__ import annotations

import numpy as np

from exponent.domain.types import FloatArray, Observation, SpotLogVol, SpotVol, VolProxy


def log_series(obs: Observation) -> FloatArray:
    """Log-vol or log-variance — same H, since they differ by an affine map."""
    if isinstance(obs, SpotLogVol):
        return np.asarray(obs.log_vol, dtype=np.float64)
    if isinstance(obs, SpotVol):
        out: FloatArray = np.log(np.asarray(obs.vol, dtype=np.float64))
        return out
    return obs.log_series()


def raw_series(obs: Observation) -> FloatArray:
    """The path exactly as observed, for model-free estimators."""
    if isinstance(obs, SpotLogVol):
        return np.asarray(obs.log_vol, dtype=np.float64)
    if isinstance(obs, SpotVol):
        return np.asarray(obs.vol, dtype=np.float64)
    assert isinstance(obs, VolProxy)
    return np.asarray(obs.values, dtype=np.float64)
