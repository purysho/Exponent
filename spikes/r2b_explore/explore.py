"""R2b v2 exploration (docs/m0a-gate-v2.md): search for Cont & Das's realised-vol
construction using ONLY the Table 3 training target (OU-SV, mean Ĥ(RV) = 0.137).

Every candidate run here is appended to docs/r2b-exploration.md, whatever the
result. Throwaway search code; the locked construction moves into the domain.

    uv run python spikes/r2b_explore/explore.py E3 --paths 40
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.signal import lfilter

from exponent.domain.estimators.roughness.pvariation import normalized_pvariation
from exponent.domain.rng import cell_rng

L, K = 90_000, 300


def ou_sv_log_price(n: int, T: float, rng: np.random.Generator) -> np.ndarray:
    """OU-SV (σ₀ = γ = θ = 1) log-price on n fine steps; same scheme as vol_models.ou_sv."""
    dt = T / n
    a = np.exp(-dt)
    y = np.concatenate([[0.0], lfilter([1.0], [1.0, -a], rng.standard_normal(n) * np.sqrt((1 - a * a) / 2))])
    v = np.exp(y[:-1])
    return np.concatenate([[0.0], np.cumsum(v * np.sqrt(dt) * rng.standard_normal(n) - 0.5 * v * v * dt)])


def rv_rolling_strided(x: np.ndarray, window: int, stride: int, n_out: int) -> np.ndarray:
    """√(sum of the last `window` squared returns), sampled every `stride` steps."""
    c = np.concatenate([[0.0], np.cumsum(np.diff(x) ** 2)])
    ends = window + stride * np.arange(n_out)
    return np.sqrt(c[ends] - c[ends - window])


def one(args: tuple[str, dict, int]) -> float | None:
    name, p, rep = args
    rng = cell_rng(f"r2b-explore-{name}", rep)
    w, d, T = p["window"], p["stride"], p.get("T", 1.0)
    n_fine = w + d * L
    x = ou_sv_log_price(n_fine, T * n_fine / (d * L), rng)  # RV grid spans [0, T]
    rv = rv_rolling_strided(x, w, d, L + 1)
    return normalized_pvariation(rv, K).value


CANDIDATES = {
    # E3: rolling 300-return windows, RV sampled every d steps (d = 1 is reading A, d = 300 is B)
    "E3": [{"window": 300, "stride": d} for d in (3, 10, 30, 100)],
    # E4: non-overlapping blocks (stride = window) with bigger windows
    "E4": [{"window": w, "stride": w} for w in (1000, 3000)],
    # E5: non-overlapping 300-blocks over a longer horizon (more vol movement per block)
    "E5": [{"window": 300, "stride": 300, "T": t} for t in (10.0, 100.0)],
    # E5b: fit the unstated horizon T inside the textually preferred family (see log)
    "E5b": [{"window": 300, "stride": 300, "T": t} for t in (2.0, 3.0, 4.0, 5.0)],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("family", choices=sorted(CANDIDATES))
    ap.add_argument("--paths", type=int, default=40)
    args = ap.parse_args()
    for p in CANDIDATES[args.family]:
        name = f"{args.family}-" + "-".join(f"{k}{v:g}" for k, v in p.items())
        with ProcessPoolExecutor(4) as pool:
            vals = [v for v in pool.map(one, [(name, p, r) for r in range(args.paths)]) if v is not None]
        a = np.array(vals)
        print(f"{name}: n={a.size}/{args.paths} mean {a.mean():.3f} sd {a.std():.3f}", flush=True)


if __name__ == "__main__":
    main()
