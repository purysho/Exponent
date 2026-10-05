"""The court runner: truth × observation × estimator × replication → result rows.

An experiment is a list of cells (parameter points), a simulation that turns
one cell and one generator into named observations, and the (observation,
estimator) pairs to score. Every (cell, replication) gets its own generator
from `cell_rng(experiment key, cell, rep)`, so any row can be recomputed alone
and the grid can be split across processes in any order.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

import numpy as np
import polars as pl

from exponent.domain.estimators.registry import ROUGHNESS
from exponent.domain.rng import cell_rng
from exponent.domain.types import Observation

Params = Mapping[str, Any]
Simulate = Callable[[Params, np.random.Generator], Mapping[str, Observation]]


@dataclass(frozen=True)
class Experiment:
    key: str
    cells: tuple[Params, ...]
    reps: int
    simulate: Simulate
    pairs: tuple[tuple[str, str], ...]  # (observation name, estimator name)

    def __post_init__(self) -> None:
        unknown = {e for _, e in self.pairs} - set(ROUGHNESS)
        if unknown:
            raise ValueError(f"unregistered estimators: {sorted(unknown)}")


SCHEMA = {
    "experiment": pl.String,
    "cell": pl.Int64,
    "params": pl.String,
    "rep": pl.Int64,
    "observation": pl.String,
    "estimator": pl.String,
    "version": pl.String,
    "status": pl.String,
    "value": pl.Float64,
    "note": pl.String,
}


def run_one(exp: Experiment, cell: int, rep: int) -> list[dict[str, Any]]:
    params = exp.cells[cell]
    observations = exp.simulate(params, cell_rng(exp.key, cell, rep))
    rows = []
    for obs_name, est_name in exp.pairs:
        spec = ROUGHNESS[est_name]
        est = spec(observations[obs_name])
        rows.append(
            {
                "experiment": exp.key,
                "cell": cell,
                "params": json.dumps(dict(params), sort_keys=True),
                "rep": rep,
                "observation": obs_name,
                "estimator": spec.name,
                "version": spec.version,
                "status": est.status.value,
                "value": est.value,
                "note": est.note,
            }
        )
    return rows


def _run_task(args: tuple[Experiment, int, int]) -> list[dict[str, Any]]:
    return run_one(*args)


def run(exp: Experiment, workers: int | None = None) -> pl.DataFrame:
    tasks = [(exp, c, r) for c in range(len(exp.cells)) for r in range(exp.reps)]
    workers = workers or os.cpu_count() or 1
    rows: list[dict[str, Any]] = []
    if workers == 1:
        for t in tasks:
            rows.extend(_run_task(t))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for out in pool.map(_run_task, tasks, chunksize=max(1, len(tasks) // (workers * 8))):
                rows.extend(out)
    return pl.DataFrame(rows, schema=SCHEMA).sort("cell", "rep", "observation", "estimator")


def summarise(
    df: pl.DataFrame, by: Sequence[str] = ("cell", "observation", "estimator")
) -> pl.DataFrame:
    """Per-group mean, sd and quartiles of OK values, plus how many were not OK."""
    ok = pl.col("status") == "ok"
    return (
        df.group_by([*by, "params"])
        .agg(
            n=pl.len(),
            n_ok=ok.sum(),
            mean=pl.col("value").filter(ok).mean(),
            sd=pl.col("value").filter(ok).std(),
            q25=pl.col("value").filter(ok).quantile(0.25),
            q75=pl.col("value").filter(ok).quantile(0.75),
        )
        .sort(list(by))
    )
