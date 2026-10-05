"""Exact fractional Gaussian noise by circulant embedding (Davies–Harte).

fGn with Hurst H has autocovariance γ(k) = ½(|k+1|^{2H} − 2|k|^{2H} + |k−1|^{2H}).
Embedding γ in a 2n circulant matrix makes it diagonal under the FFT, so an
exact sample of length n costs O(n log n). The embedding is non-negative
definite for every H in (0, 1), so no approximation is involved.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import scipy.fft

from exponent.domain.types import FloatArray

_SERIES_FROM = 64  # lag from which γ(k) is summed as a series, not by subtraction


def fgn_autocovariance(n: int, H: float) -> FloatArray:
    """γ(0..n) for unit-spacing, unit-variance fGn.

    The textbook form ½(|k+1|^{2H} − 2k^{2H} + |k−1|^{2H}) subtracts numbers of
    size k^{2H} to get one of size k^{2H−2}; at k ~ 10⁷ that loses every
    significant digit, and at 27 million steps it made the circulant embedding
    numerically indefinite for H = 0.8. For k ≥ 64 we use the exact expansion,
    with a = 2H and x = 1/k:

        γ(k) = ½ k^a [a(a−1)x² + a(a−1)(a−2)(a−3)x⁴/12 + a(a−1)…(a−5)x⁶/360],

    whose first omitted term is below 10⁻¹⁴ relative at k = 64.
    """
    a = 2.0 * H
    k = np.arange(n + 1, dtype=np.float64)
    out = np.empty(n + 1)
    head = k[: min(_SERIES_FROM, n + 1)]
    out[: head.size] = 0.5 * (np.abs(head + 1) ** a - 2.0 * head**a + np.abs(head - 1) ** a)
    if n + 1 > _SERIES_FROM:
        kt = k[_SERIES_FROM:]
        x2 = 1.0 / (kt * kt)
        c1 = a * (a - 1)
        c2 = c1 * (a - 2) * (a - 3) / 12.0
        c3 = c2 * (a - 4) * (a - 5) / 30.0
        out[_SERIES_FROM:] = 0.5 * kt**a * x2 * (c1 + x2 * (c2 + x2 * c3))
    return out


def fgn(n: int, H: float, rng: np.random.Generator, n_paths: int = 1) -> FloatArray:
    """(n_paths, n) samples of unit-step fGn: each increment has variance 1.

    Scale by dt**H for increments of fBM on a grid of step dt.
    """
    if not 0.0 < H < 1.0:
        raise ValueError(f"H must be in (0, 1), got {H}")
    scale = _circulant_scale(n, H)
    m = scale.size
    z = rng.standard_normal((n_paths, m)) + 1j * rng.standard_normal((n_paths, m))
    z *= scale
    w = scipy.fft.fft(z, axis=1, overwrite_x=True)
    out: FloatArray = w.real[:, :n]
    return out


@lru_cache(maxsize=2)
def _circulant_scale(n: int, H: float) -> FloatArray:
    """√(λ/m) for the 2n circulant embedding. Depends only on (n, H), so it is
    cached: at 27 million steps it is half the cost of a path."""
    gamma = fgn_autocovariance(n, H)
    c = np.concatenate([gamma, gamma[-2:0:-1]])  # first row of the 2n circulant (symmetric)
    m = c.size
    half = scipy.fft.rfft(c).real  # λ_k for k = 0..n; the circulant is symmetric, λ_k = λ_{m−k}
    lam = np.concatenate([half, half[-2:0:-1]])
    if lam.min() < -1e-8 * lam.max():
        raise ValueError("circulant embedding is not non-negative definite")
    scale: FloatArray = np.sqrt(np.clip(lam, 0.0, None) / m)
    scale.setflags(write=False)
    return scale


def fbm(n: int, H: float, dt: float, rng: np.random.Generator, n_paths: int = 1) -> FloatArray:
    """(n_paths, n + 1) fractional Brownian motion on a grid of step dt, starting at 0."""
    inc = fgn(n, H, rng, n_paths) * dt**H
    return np.concatenate([np.zeros((n_paths, 1)), np.cumsum(inc, axis=1)], axis=1)
