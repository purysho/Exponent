"""Stochastic-volatility truths: the court's ground-truth generators.

Each function returns latent volatility (or variance) on a grid together with
the log-price path it drives, so the same path can be observed both directly
(the oracle) and through a realised-variance proxy (what real data allows).

Time is in the model's own units on [0, T]; grids have n steps and n + 1 points.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import fftconvolve, lfilter

from exponent.domain.generators.fgn import fgn
from exponent.domain.types import FloatArray


@dataclass(frozen=True)
class SimulatedPath:
    """One simulated market path. `variance` and `log_price` share the grid."""

    t: FloatArray
    variance: FloatArray  # instantaneous σ²_t, length n + 1
    log_price: FloatArray  # log S_t, length n + 1


def _log_price(variance: FloatArray, dt: float, dB: FloatArray) -> FloatArray:
    """Log-Euler: d log S = −½σ² dt + σ dB, with σ² taken at the left endpoint."""
    v_left = variance[:-1]
    dlog = -0.5 * v_left * dt + np.sqrt(v_left) * dB
    return np.concatenate([[0.0], np.cumsum(dlog)])


def ou_sv(
    n: int, T: float, gamma: float, theta: float, sigma0: float, rng: np.random.Generator
) -> SimulatedPath:
    """Cont and Das's Example 6 (OU-SV): σ = σ₀ e^Y, dY = −γY dt + θ dB'.

    Y is a Brownian Ornstein–Uhlenbeck process, so volatility is a
    semimartingale with H = 1/2. Y is simulated exactly on the grid.
    """
    dt = T / n
    a = np.exp(-gamma * dt)
    sd = theta * np.sqrt((1.0 - a * a) / (2.0 * gamma))
    shocks = rng.standard_normal(n) * sd
    y = np.concatenate([[0.0], lfilter([1.0], [1.0, -a], shocks)])  # y₀ = 0
    var = (sigma0 * np.exp(y)) ** 2
    dB = rng.standard_normal(n) * np.sqrt(dt)
    return SimulatedPath(np.linspace(0.0, T, n + 1), var, _log_price(var, dt, dB))


def fractional_ou_log_vol(
    n: int, dt: float, H: float, nu: float, alpha: float, mean: float, rng: np.random.Generator
) -> FloatArray:
    """RFSV log-volatility (Gatheral–Jaisson–Rosenbaum): dX = ν dW^H − α(X − m) dt.

    Euler scheme driven by exact fGn increments. With α small relative to the
    lags examined, increments of X behave like those of ν·W^H.
    """
    inc = nu * fgn(n, H, rng)[0] * dt**H
    dev = lfilter([1.0], [1.0, -(1.0 - alpha * dt)], inc)  # (x − m) recursion, x₀ = m
    out: FloatArray = np.concatenate([[mean], mean + dev])
    return out


def hybrid_kernel(n: int, H: float, T: float) -> tuple[FloatArray, FloatArray]:
    """Weights of the κ = 0 hybrid scheme for the Riemann–Liouville kernel.

    Returns g with g_m = (b_m dt)^{H − ½}, b_m the optimal evaluation points of
    Bennedsen, Lunde and Pakkanen (2017), and v_i = Var(W̃_{t_i}) of the
    discretised process, used in the compensator so E[V_t] = ξ₀ holds exactly
    on the grid. Same scheme as Lumor's roughvollab, so reproductions compare
    like with like.
    """
    a = H - 0.5
    dt = T / n
    m = np.arange(1, n + 1, dtype=np.float64)
    if abs(a) < 1e-12:
        g = np.ones(n)
    else:
        b = ((m ** (a + 1) - (m - 1) ** (a + 1)) / (a + 1)) ** (1.0 / a)
        g = (b * dt) ** a
    v = 2.0 * H * dt * np.cumsum(g * g)
    return g, v


def rough_bergomi(
    n: int,
    T: float,
    H: float,
    eta: float,
    rho: float,
    xi0: float,
    rng: np.random.Generator,
) -> SimulatedPath:
    """Rough Bergomi: V_t = ξ₀ exp(η W̃_t − ½η² Var W̃_t), W̃ = √(2H) ∫ (t−s)^{H−½} dW_s.

    At H = ½ the kernel is flat, W̃ is Brownian motion and log-variance is a
    (non-mean-reverting) semimartingale: the smooth null used by Lumor.
    """
    if not 0.0 < H < 1.0:
        raise ValueError(f"H must be in (0, 1), got {H}")
    dt = T / n
    dW1 = rng.standard_normal(n) * np.sqrt(dt)
    dW2 = rng.standard_normal(n) * np.sqrt(dt)
    g, v = hybrid_kernel(n, H, T)
    w_tilde = np.sqrt(2.0 * H) * fftconvolve(dW1, g)[:n]
    var = np.empty(n + 1)
    var[0] = xi0
    var[1:] = xi0 * np.exp(eta * w_tilde - 0.5 * eta * eta * v)
    dB = rho * dW1 + np.sqrt(1.0 - rho * rho) * dW2
    return SimulatedPath(np.linspace(0.0, T, n + 1), var, _log_price(var, dt, dB))


@dataclass(frozen=True)
class BlockObservedPath:
    """A path observed only through non-overlapping blocks of `sub` fine steps."""

    vol_at_block_ends: FloatArray  # σ at the n_blocks + 1 block boundaries
    vol_block_mean: FloatArray  # mean of σ over each block's fine steps
    block_rv: FloatArray  # √(Σ squared fine log-returns) per block, volatility units


def ou_sv_blocks(
    n_blocks: int,
    sub: int,
    T: float,
    gamma: float,
    theta: float,
    sigma0: float,
    rng: np.random.Generator,
    chunk: int = 1000,
) -> BlockObservedPath:
    """The OU-SV model of `ou_sv`, simulated on n_blocks · sub fine steps.

    Only block-level quantities are kept, and the fine path is generated in
    chunks, so 90 000 blocks of 300 steps (27 million steps) fit in memory.
    """
    n = n_blocks * sub
    dt = T / n
    a = np.exp(-gamma * dt)
    sd = theta * np.sqrt((1.0 - a * a) / (2.0 * gamma))
    ends = np.empty(n_blocks + 1)
    means = np.empty(n_blocks)
    rv = np.empty(n_blocks)
    ends[0] = sigma0
    y_last = 0.0
    for start in range(0, n_blocks, chunk):
        nb = min(chunk, n_blocks - start)
        shocks = rng.standard_normal(nb * sub) * sd
        y, _ = lfilter([1.0], [1.0, -a], shocks, zi=[a * y_last])
        y_left = np.concatenate([[y_last], y[:-1]])  # σ at each step's left endpoint
        vol_left = sigma0 * np.exp(y_left)
        r = vol_left * np.sqrt(dt) * rng.standard_normal(nb * sub) - 0.5 * vol_left**2 * dt
        blocks = slice(start, start + nb)
        rv[blocks] = np.sqrt(np.sum((r * r).reshape(nb, sub), axis=1))
        means[blocks] = vol_left.reshape(nb, sub).mean(axis=1)
        ends[start + 1 : start + nb + 1] = sigma0 * np.exp(y[sub - 1 :: sub])
        y_last = float(y[-1])
    return BlockObservedPath(ends, means, rv)


def _observe_blocks(
    vol_left: FloatArray, dt: float, sub: int, rng: np.random.Generator
) -> tuple[FloatArray, FloatArray]:
    """Block RV and block-mean σ from σ at each fine step's left endpoint."""
    nb = vol_left.size // sub
    r = vol_left * np.sqrt(dt) * rng.standard_normal(vol_left.size) - 0.5 * vol_left**2 * dt
    rv = np.sqrt(np.sum((r * r).reshape(nb, sub), axis=1))
    return rv, vol_left.reshape(nb, sub).mean(axis=1)


def fou_blocks(
    n_blocks: int,
    sub: int,
    T: float,
    H: float,
    gamma: float,
    theta: float,
    sigma0: float,
    rng: np.random.Generator,
    chunk: int = 1000,
) -> BlockObservedPath:
    """Cont & Das Example 7: σ = σ₀e^Y, dY = −γY dt + θ dB^H, observed in blocks.

    Y is Euler-stepped on all n_blocks · sub fine steps with exact fGn
    increments (memory scales with the fine grid: ~3 GB at 27 million steps);
    prices are then generated and summarised block by block.
    """
    n = n_blocks * sub
    dt = T / n
    inc = theta * fgn(n, H, rng)[0] * dt**H
    y = np.concatenate([[0.0], lfilter([1.0], [1.0, -(1.0 - gamma * dt)], inc)])
    del inc
    ends = sigma0 * np.exp(y[::sub])
    rv = np.empty(n_blocks)
    means = np.empty(n_blocks)
    for start in range(0, n_blocks, chunk):
        nb = min(chunk, n_blocks - start)
        vol_left = sigma0 * np.exp(y[start * sub : (start + nb) * sub])
        rv[start : start + nb], means[start : start + nb] = _observe_blocks(vol_left, dt, sub, rng)
    return BlockObservedPath(ends, means, rv)


def abs_bm_blocks(
    n_blocks: int, sub: int, T: float, rng: np.random.Generator, chunk: int = 1000
) -> BlockObservedPath:
    """Cont & Das Example 5: σ_t = |W_t|, W a Brownian motion from 0, observed in blocks."""
    n = n_blocks * sub
    dt = T / n
    ends = np.empty(n_blocks + 1)
    rv = np.empty(n_blocks)
    means = np.empty(n_blocks)
    ends[0] = 0.0
    w_last = 0.0
    for start in range(0, n_blocks, chunk):
        nb = min(chunk, n_blocks - start)
        w = w_last + np.cumsum(rng.standard_normal(nb * sub) * np.sqrt(dt))
        vol_left = np.abs(np.concatenate([[w_last], w[:-1]]))
        rv[start : start + nb], means[start : start + nb] = _observe_blocks(vol_left, dt, sub, rng)
        ends[start + 1 : start + nb + 1] = np.abs(w[sub - 1 :: sub])
        w_last = float(w[-1])
    return BlockObservedPath(ends, means, rv)
