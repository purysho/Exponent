"""Small, fast versions of the M0a reproductions, kept as regression tests.

The full-size gates run via `exponent m0a` (docs/m0a-gate.md). These use
fewer replications, so tolerances are widened by the larger Monte Carlo error;
they catch regressions, they do not re-decide the gate.
"""

import json

import polars as pl

from exponent.app import m0a
from exponent.app.court import run, summarise


def test_r1_structure_function_recovers_h_small() -> None:
    s = summarise(run(m0a.r1(reps=12, n=4000), workers=1))
    for params, mean in zip(s["params"], s["mean"], strict=True):
        H = json.loads(params)["H"]
        assert abs(mean - H) < 0.035, (H, mean)


def test_r2a_cont_das_table1_small() -> None:
    df = run(m0a.r2a(reps=6), workers=1)
    s = m0a.gate_r2a(df).table
    for mean, paper in zip(s["mean"], s["paper_mean"], strict=True):
        assert abs(mean - paper) < 0.015, (mean, paper)


def test_r3_classification_runs_on_a_tiny_map() -> None:
    df = run(m0a.r3(reps=2, n_obs=500), workers=1)
    st = m0a.map_statuses(df)
    assert st.height == 4 * 3 * 7 * 4
    assert set(st["status"].unique()) <= {
        "identified",
        "de-biasable",
        "non-identified",
        "uncalibrated",
    }
    assert isinstance(m0a.gate_r3(df).table, pl.DataFrame)
