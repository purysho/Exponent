"""Command-line entry point: `exponent m0a`."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

import polars as pl

from exponent.app import m0a
from exponent.app.court import Experiment, run


def _commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "src"], capture_output=True, text=True
        )
        return out.stdout.strip() + ("+dirty" if dirty.stdout.strip() else "")
    except OSError:
        return "unknown"


def _run(exp: Experiment, out: Path, workers: int | None) -> pl.DataFrame:
    t0 = time.time()
    df = run(exp, workers)
    df = df.with_columns(pl.lit(_commit()).alias("code_commit"))
    df.write_parquet(out / f"{exp.key}.parquet")
    print(f"  {exp.key}: {df.height} rows in {time.time() - t0:.0f}s", flush=True)
    return df


def cmd_m0a(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    wanted = set(args.only.split(",")) if args.only else {"r1", "r2a", "r2b", "r3"}
    gates = []
    if "r1" in wanted:
        gates.append(m0a.gate_r1(_run(m0a.r1(), out, args.workers)))
    if "r2a" in wanted:
        gates.append(m0a.gate_r2a(_run(m0a.r2a(), out, args.workers)))
    if "r2b" in wanted:
        a, b = m0a.r2b()
        gates.append(
            m0a.gate_r2b(pl.concat([_run(a, out, args.workers), _run(b, out, args.workers)]))
        )
    if "r3" in wanted:
        df = _run(m0a.r3(), out, args.workers)
        m0a.map_statuses(df).write_csv(out / "m0a-r3-statuses.csv")
        gates.append(m0a.gate_r3(df))

    lines = [f"# M0a gate results (code {_commit()})", ""]
    for g in gates:
        lines += [f"## {g.name}: {'PASS' if g.passed else 'FAIL'}", "", "```"]
        with pl.Config(tbl_rows=200, tbl_cols=20, tbl_width_chars=160, fmt_str_lengths=60):
            lines.append(str(g.table.drop("params", strict=False)))
        lines += ["```", *[f"- {n}" for n in g.notes], ""]
    report = "\n".join(lines)
    (out / "report.md").write_text(report)
    print(report)
    return 0 if all(g.passed for g in gates) else 1


def main() -> int:
    p = argparse.ArgumentParser(prog="exponent")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("m0a", help="run the M0a reproductions and check their gates")
    m.add_argument("--only", help="comma list of r1,r2a,r2b,r3")
    m.add_argument("--workers", type=int, default=None)
    m.add_argument("--out", default="results/m0a")
    args = p.parse_args()
    if args.cmd == "m0a":
        return cmd_m0a(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
