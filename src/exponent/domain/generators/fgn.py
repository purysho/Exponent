"""Exact fractional Gaussian noise by circulant embedding (Davies–Harte).

fGn with Hurst H has autocovariance γ(k) = ½(|k+1|^{2H} − 2|k|^{2H} + |k−1|^{2H}).
Embedding γ in a 2n circulant matrix makes it diagonal under the FFT, so an
exact sample of length n costs O(n log n). The embedding is non-negative
definite for every H in (0, 1), so no approximation is involved.
"""

from __future__ import annotations

import numpy as np

from exponent.domain.types import FloatArray


def fgn_autocovariance(n: int, H: float) -> FloatArray:
    """γ(0..n) for unit-spacing, unit-variance fGn."""
    k = np.arange(n + 1, dtype=np.float64)
    h2 = 2.0 * H
    return 0.5 * (np.abs(k + 1) ** h2 - 2.0 * k**h2 + np.abs(k - 1) ** h2)


def fgn(n: int, H: float, rng: np.random.Generator, n_paths: int = 1) -> FloatArray:
    """(n_paths, n) samples of unit-step fGn: each increment has variance 1.

    Scale by dt**H for increments of fBM on a grid of step dt.
    """
    if not 0.0 < H < 1.0:
        raise ValueError(f"H must be in (0, 1), got {H}")
    gamma = fgn_autocovariance(n, H)
    c = np.concatenate([gamma, gamma[-2:0:-1]])  # first row of the 2n circulant
    m = c.size
    lam = np.fft.fft(c).real
    if lam.min() < -1e-8 * lam.max():
        raise ValueError("circulant embedding is not non-negative definite")
    lam = np.clip(lam, 0.0, None)
    z = rng.standard_normal((n_paths, m)) + 1j * rng.standard_normal((n_paths, m))
    w = np.fft.fft(np.sqrt(lam / m) * z, axis=1)
    out: FloatArray = w.real[:, :n]
    return out


def fbm(n: int, H: float, dt: float, rng: np.random.Generator, n_paths: int = 1) -> FloatArray:
    """(n_paths, n + 1) fractional Brownian motion on a grid of step dt, starting at 0."""
    inc = fgn(n, H, rng, n_paths) * dt**H
    return np.concatenate([np.zeros((n_paths, 1)), np.cumsum(inc, axis=1)], axis=1)
