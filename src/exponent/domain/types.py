"""Core types: what an estimator sees, and what it returns.

The design rests on one separation (docs/architecture.md): estimators never
see the truth, only an observation of it. Observation kinds are distinct
types so that an estimator built for spot volatility cannot silently be fed a
realised-variance proxy — the confusion at the heart of Cont and Das's
critique.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


class Estimand(Enum):
    H_LOG_VOL = "Hurst exponent of log volatility"
    IMPACT_EXPONENT = "δ in I(Q) ∝ (Q/V)^δ"


@dataclass(frozen=True)
class SpotLogVol:
    """The latent log-volatility (or log-variance — affine, same H) on a grid.

    Only a simulator can produce this. Real data never can.
    """

    log_vol: FloatArray


@dataclass(frozen=True)
class SpotVol:
    """Latent volatility σ_t itself (not its log), on a grid."""

    vol: FloatArray


@dataclass(frozen=True)
class VolProxy:
    """A realised-volatility proxy series built from prices.

    `window` is the number of fine price returns behind each proxy value;
    `kind` names the construction so results can be grouped by it; `scale`
    says whether `values` are volatility levels ("vol") or log-variance
    ("log_var"). Log-based estimators convert; model-free ones take the
    series as given.
    """

    values: FloatArray
    window: int
    kind: str
    scale: str

    def log_series(self) -> FloatArray:
        """The proxy as log-variance (affine in log-vol, so the same H)."""
        if self.scale == "log_var":
            return self.values
        if self.scale == "vol":
            out: FloatArray = 2.0 * np.log(self.values)
            return out
        raise ValueError(f"unknown proxy scale {self.scale!r}")


Observation = SpotLogVol | SpotVol | VolProxy


class Status(Enum):
    """Non-answers are outcomes. They are counted, never dropped as NaN."""

    OK = "ok"
    NO_ROOT = "no_root"
    AMBIGUOUS = "ambiguous"  # more than one root
    FAILED = "failed"


@dataclass(frozen=True)
class Estimate:
    status: Status
    value: float | None
    diagnostics: Mapping[str, float] = field(default_factory=dict)
    note: str = ""

    def __post_init__(self) -> None:
        if (self.status is Status.OK) != (self.value is not None):
            raise ValueError("an Estimate has a value exactly when its status is OK")

    @staticmethod
    def ok(value: float, **diagnostics: float) -> Estimate:
        if not np.isfinite(value):
            return Estimate(Status.FAILED, None, diagnostics, note="non-finite value")
        return Estimate(Status.OK, float(value), diagnostics)


EstimatorFn = Callable[[Any], Estimate]


@dataclass(frozen=True)
class EstimatorSpec:
    """A registry entry. The leaderboard key is (name, version).

    `consumes` lists the observation types the estimator is defined on. The
    court refuses any other pairing.
    """

    name: str
    version: str
    citation: str
    estimates: Estimand
    consumes: tuple[type, ...]
    fn: EstimatorFn

    def __call__(self, obs: Observation) -> Estimate:
        if not isinstance(obs, self.consumes):
            raise TypeError(
                f"{self.name} consumes {[c.__name__ for c in self.consumes]}, "
                f"got {type(obs).__name__}"
            )
        try:
            with np.errstate(all="ignore"):
                return self.fn(obs)
        except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
            # Degenerate input (e.g. a constant segment) is a recorded failure,
            # not a crash of the whole grid. Programming errors still raise.
            return Estimate(Status.FAILED, None, note=f"{type(exc).__name__}: {exc}")
