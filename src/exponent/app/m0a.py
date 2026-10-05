"""M0a: the harness reproduces known roughness results on synthetic data.

The pass criteria are in docs/m0a-gate.md, committed before these ran. Each
`gate_*` function below encodes that file's criteria. If the two ever
disagree, the file is authoritative and the code is the bug.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np
import polars as pl

from exponent.app.court import Experiment, Params, summarise
from exponent.domain.generators.fgn import fbm
from exponent.domain.generators.vol_models import (
    fractional_ou_log_vol,
    ou_sv,
    ou_sv_blocks,
    rough_bergomi,
)
from exponent.domain.observe.proxies import block_log_rv, rolling_realized_vol
from exponent.domain.scoring.idmap import CellStatus, curve_statuses
from exponent.domain.types import Observation, SpotLogVol, SpotVol, VolProxy


@dataclass
class GateResult:
    name: str
    passed: bool
    table: pl.DataFrame
    notes: list[str] = field(default_factory=list)


# ── R1: oracle ────────────────────────────────────────────────────────────────

R1_TOL = 0.02


def _sim_r1(p: Params, rng: np.random.Generator) -> Mapping[str, Observation]:
    x = fractional_ou_log_vol(p["n"], 1.0, p["H"], 0.3, 5e-4, 0.0, rng)
    return {"spot_log_vol": SpotLogVol(x)}


def r1(reps: int = 200, n: int = 4000) -> Experiment:
    cells = tuple({"H": h, "n": n} for h in (0.05, 0.1, 0.2, 0.3, 0.5, 0.7))
    return Experiment("m0a-r1", cells, reps, _sim_r1, (("spot_log_vol", "structure-function"),))


def gate_r1(df: pl.DataFrame) -> GateResult:
    s = _with_param(summarise(df), "H").with_columns(bias=pl.col("mean") - pl.col("H"))
    s = s.with_columns(pass_=pl.col("bias").abs() <= R1_TOL)
    return GateResult("R1 oracle (structure-function)", bool(s["pass_"].all()), s)


# ── R2a: Cont–Das Table 1 ────────────────────────────────────────────────────

R2A_IQR = {
    0.1: (0.0920, 0.1100),
    0.3: (0.2940, 0.3020),
    0.5: (0.4940, 0.5020),
    0.8: (0.7820, 0.7940),
}
R2A_PAPER_MEAN = {0.1: 0.1009, 0.3: 0.2976, 0.5: 0.4978, 0.8: 0.7891}


def _sim_r2a(p: Params, rng: np.random.Generator) -> Mapping[str, Observation]:
    L = p["L"]
    return {"fbm": SpotLogVol(fbm(L, p["H"], 1.0 / L, rng)[0])}


def r2a(reps: int = 150, L: int = 90_000) -> Experiment:
    cells = tuple({"H": h, "L": L} for h in R2A_IQR)
    return Experiment("m0a-r2a", cells, reps, _sim_r2a, (("fbm", "normalized-pvariation"),))


def gate_r2a(df: pl.DataFrame) -> GateResult:
    s = _with_param(summarise(df), "H")
    lo = pl.col("H").replace_strict({h: v[0] for h, v in R2A_IQR.items()}, return_dtype=pl.Float64)
    hi = pl.col("H").replace_strict({h: v[1] for h, v in R2A_IQR.items()}, return_dtype=pl.Float64)
    paper = pl.col("H").replace_strict(R2A_PAPER_MEAN, return_dtype=pl.Float64)
    s = s.with_columns(paper_mean=paper, paper_q25=lo, paper_q75=hi)
    s = s.with_columns(pass_=(pl.col("mean") >= lo) & (pl.col("mean") <= hi))
    return GateResult("R2a Cont–Das Table 1 (fBM)", bool(s["pass_"].all()), s)


# ── R2b: Cont–Das Table 3 ────────────────────────────────────────────────────

R2B_RV_IQR = (0.128, 0.148)
R2B_SIGMA_IQR = (0.552, 0.563)


def _sim_r2b_rolling(p: Params, rng: np.random.Generator) -> Mapping[str, Observation]:
    path = ou_sv(p["L"], 1.0, 1.0, 1.0, 1.0, rng)
    return {
        "A:rv": rolling_realized_vol(path.log_price, p["window"]),
        "A:sigma": SpotVol(np.sqrt(path.variance)),
    }


def _sim_r2b_blocks(p: Params, rng: np.random.Generator) -> Mapping[str, Observation]:
    b = ou_sv_blocks(p["L"], p["window"], 1.0, 1.0, 1.0, 1.0, rng)
    rv = VolProxy(b.block_rv, p["window"], "block_rv", "vol")
    return {
        "B:rv": rv,
        "B:sigma": SpotVol(b.vol_at_block_ends),
        "C:sigma_mean": SpotVol(b.vol_block_mean),
    }


def r2b(reps: int = 200, L: int = 90_000, window: int = 300) -> tuple[Experiment, Experiment]:
    cells = ({"L": L, "window": window, "K": 300},)
    est = "normalized-pvariation"
    a = Experiment("m0a-r2b-A", cells, reps, _sim_r2b_rolling, (("A:rv", est), ("A:sigma", est)))
    b = Experiment(
        "m0a-r2b-B",
        cells,
        reps,
        _sim_r2b_blocks,
        (("B:rv", est), ("B:sigma", est), ("C:sigma_mean", est)),
    )
    return a, b


def gate_r2b(df: pl.DataFrame) -> GateResult:
    s = summarise(df)
    m = dict(zip(s["observation"], s["mean"], strict=True))

    def inside(x: float | None, iqr: tuple[float, float]) -> bool:
        return x is not None and iqr[0] <= x <= iqr[1]

    readings = {
        r: inside(m.get(f"{r}:rv"), R2B_RV_IQR) and inside(m.get(f"{r}:sigma"), R2B_SIGMA_IQR)
        for r in "AB"
    }
    notes = [
        f"reading {r}: Ĥ(RV) mean {m.get(f'{r}:rv')}, Ĥ(σ) mean {m.get(f'{r}:sigma')} -> "
        f"{'match' if ok else 'no match'}"
        for r, ok in readings.items()
    ]
    notes.append(
        f"reading C (post hoc, cannot pass): Ĥ(RV) {m.get('B:rv')}, "
        f"Ĥ(block-mean σ) {m.get('C:sigma_mean')}"
    )
    return GateResult("R2b Cont–Das Table 3 (OU-SV)", any(readings.values()), s, notes)


# ── R3: Lumor identifiability map ────────────────────────────────────────────

R3_TRUE_H = (0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60)
R3_ETA = (0.5, 1.5, 2.5, 3.5)
R3_WINDOW = (48, 96, 288)
R3_GATING = ("structure-function", "pvariation-scaling-crossing", "mfdfa")
R3_LUMOR = {
    "structure-function": {
        "identified": 0.12,
        "non-identified": 0.85,
        "de-biasable": 0.04,
        "uncalibrated": 0.0,
    },
    "mfdfa": {"identified": 0.30, "non-identified": 0.61, "de-biasable": 0.10, "uncalibrated": 0.0},
    "pvariation-scaling-crossing": {
        "identified": 0.0,
        "non-identified": 0.92,
        "de-biasable": 0.0,
        "uncalibrated": 0.08,
    },
}
R3_TOL = 0.10


def _sim_r3(p: Params, rng: np.random.Generator) -> Mapping[str, Observation]:
    path = rough_bergomi(p["n_obs"] * p["window"], 1.0, p["H"], p["eta"], -0.7, 0.04, rng)
    return {"log_rv": block_log_rv(path.log_price, p["window"])}


def r3(reps: int = 40, n_obs: int = 2500) -> Experiment:
    cells = tuple(
        {"H": h, "eta": e, "window": w, "n_obs": n_obs}
        for e in R3_ETA
        for w in R3_WINDOW
        for h in R3_TRUE_H
    )
    pairs = tuple(("log_rv", e) for e in (*R3_GATING, "normalized-pvariation"))
    return Experiment("m0a-r3", cells, reps, _sim_r3, pairs)


def map_statuses(df: pl.DataFrame) -> pl.DataFrame:
    """One row per (estimator, η, Δ, true H) with Lumor's cell status."""
    s = summarise(df)
    s = s.with_columns(
        pl.col("params")
        .map_elements(lambda j: json.loads(j)["H"], return_dtype=pl.Float64)
        .alias("H"),
        pl.col("params")
        .map_elements(lambda j: json.loads(j)["eta"], return_dtype=pl.Float64)
        .alias("eta"),
        pl.col("params")
        .map_elements(lambda j: json.loads(j)["window"], return_dtype=pl.Int64)
        .alias("window"),
    )
    out = []
    for (est, eta, win), g in s.sort("H").group_by(
        ["estimator", "eta", "window"], maintain_order=True
    ):
        mean = g["mean"].fill_null(np.nan).to_numpy()
        sd = g["sd"].fill_null(np.nan).to_numpy()
        for h, m, st in zip(g["H"], mean, curve_statuses(g["H"].to_numpy(), mean, sd), strict=True):
            out.append(
                {"estimator": est, "eta": eta, "window": win, "H": h, "mean": m, "status": st.value}
            )
    return pl.DataFrame(out).sort("estimator", "eta", "window", "H")


def gate_r3(df: pl.DataFrame) -> GateResult:
    st = map_statuses(df)
    rows, ok = [], True
    ident: dict[str, float] = {}
    for est in (*R3_GATING, "normalized-pvariation"):
        g = st.filter(pl.col("estimator") == est)
        for status in CellStatus:
            n_match = g.filter(pl.col("status") == status.value).height
            frac = n_match / g.height if g.height else float("nan")
            ref = R3_LUMOR.get(est, {}).get(status.value)
            within = None if ref is None else abs(frac - ref) <= R3_TOL
            if est in R3_GATING and not within:
                ok = False
            rows.append(
                {
                    "estimator": est,
                    "status": status.value,
                    "ours": frac,
                    "lumor": ref,
                    "within_10pp": within,
                }
            )
            if status is CellStatus.IDENTIFIED:
                ident[est] = frac
    mfdfa_top = ident["mfdfa"] >= max(ident[e] for e in R3_GATING)
    notes = [f"MF-DFA has the largest identified fraction of the gating three: {mfdfa_top}"]
    return GateResult("R3 Lumor identifiability map", ok and mfdfa_top, pl.DataFrame(rows), notes)


def _with_param(s: pl.DataFrame, name: str) -> pl.DataFrame:
    return s.with_columns(
        pl.col("params")
        .map_elements(lambda j: json.loads(j)[name], return_dtype=pl.Float64)
        .alias(name)
    )
