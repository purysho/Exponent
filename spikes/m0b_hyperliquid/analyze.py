"""M0b spike: are Hyperliquid TWAP parents recoverable from public data, and
how well does a Barone–Lillo-style reconstruction recover them blind?

Throwaway code (docs/build-plan.md). Inputs: the trade tape captured by
capture.py, plus two public per-address endpoints for every address that
took liquidity with a zero-hash trade:

  userTwapSliceFills  slice fills with their parent twapId (≤ 2000 most recent)
  twapHistory         parent orders: coin, side, intended size, minutes (≤ 2000)

    uv run python spikes/m0b_hyperliquid/analyze.py
"""

from __future__ import annotations

import gzip
import json
import math
import time
import urllib.request
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
DATA = HERE / "data"
API = DATA / "api"
INFO = "https://api.hyperliquid.xyz/info"
ZERO = "0x" + "0" * 64
GAPS_MIN = (1.0, 5.0, 15.0)  # reconstruction: max gap between child orders
MIN_CHILDREN = 10  # Barone & Lillo's threshold for statistical metaorders


def post(body: dict) -> object:
    req = urllib.request.Request(
        INFO, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    for attempt in range(5):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:  # rate limit or transient: back off
            time.sleep(2**attempt)
    raise RuntimeError(f"API failed: {body}")


def cached(kind: str, user: str) -> list:
    API.mkdir(parents=True, exist_ok=True)
    f = API / f"{kind}-{user}.json"
    if not f.exists():
        f.write_text(json.dumps(post({"type": kind, "user": user})))
        time.sleep(1.1)  # stay well inside the public rate limit
    return json.loads(f.read_text())


def load_tape() -> list[dict]:
    rows = []
    for f in sorted(DATA.glob("trades-*.jsonl.gz")):
        try:
            with gzip.open(f, "rt") as fh:
                for line in fh:
                    rows.append(json.loads(line))
        except (EOFError, json.JSONDecodeError):
            pass  # a file still being written ends mid-block
    rows.sort(key=lambda t: (t["time"], t["tid"]))
    return rows


def taker(t: dict) -> str:
    # users = [buyer, seller]; side is the aggressor's side (verified on a known slice)
    return t["users"][0] if t["side"] == "B" else t["users"][1]


def child_orders(tape: list[dict], users: set[str]) -> list[dict]:
    """Collapse trades into taker child orders: one aggressive order can hit several makers."""
    agg: dict[tuple, dict] = {}
    for t in tape:
        u = taker(t)
        if u not in users:
            continue
        k = (u, t["coin"], t["side"], t["time"])
        c = agg.setdefault(
            k,
            {
                "user": u,
                "coin": t["coin"],
                "side": t["side"],
                "time": t["time"],
                "sz": 0.0,
                "ntl": 0.0,
                "tids": [],
                "zero": t["hash"] == ZERO,
            },
        )
        sz, px = float(t["sz"]), float(t["px"])
        c["sz"] += sz
        c["ntl"] += sz * px
        c["tids"].append(t["tid"])
    return sorted(agg.values(), key=lambda c: (c["user"], c["coin"], c["side"], c["time"]))


def reconstruct(children: list[dict], gap_min: float) -> list[list[int]]:
    """Runs of same (user, coin, side) children with gaps ≤ gap; ≥ MIN_CHILDREN kept."""
    out, run = [], []
    prev = None
    for i, c in enumerate(children):
        key = (c["user"], c["coin"], c["side"])
        if prev and key == prev[0] and c["time"] - prev[1] <= gap_min * 60_000:
            run.append(i)
        else:
            if len(run) >= MIN_CHILDREN:
                out.append(run)
            run = [i]
        prev = (key, c["time"])
    if len(run) >= MIN_CHILDREN:
        out.append(run)
    return out


def pair_scores(groups: list[list[int]], label: dict[int, int]) -> tuple[float, float]:
    """Pairwise precision/recall of reconstructed groups against TWAP parents.

    Only labelled (TWAP) children enter the pairs.
    """
    same_true = Counter(label.values())
    true_pairs = sum(n * (n - 1) // 2 for n in same_true.values())
    found_pairs = correct = 0
    for g in groups:
        lab = [label[i] for i in g if i in label]
        found_pairs += len(lab) * (len(lab) - 1) // 2
        for n in Counter(lab).values():
            correct += n * (n - 1) // 2
    prec = correct / found_pairs if found_pairs else math.nan
    rec = correct / true_pairs if true_pairs else math.nan
    return prec, rec


def last_price_before(series: dict[str, tuple[np.ndarray, np.ndarray]], coin: str, t: int) -> float:
    ts, px = series[coin]
    i = np.searchsorted(ts, t, side="left") - 1
    return float(px[i]) if i >= 0 else math.nan


def last_price_at(series: dict[str, tuple[np.ndarray, np.ndarray]], coin: str, t: int) -> float:
    ts, px = series[coin]
    i = np.searchsorted(ts, t, side="right") - 1
    return float(px[i]) if i >= 0 else math.nan


def impact_fit(points: list[tuple[float, float]], n_bins: int = 8) -> tuple[float, float, int]:
    """Slope of log mean impact vs log Q/V over log bins with positive mean impact."""
    if len(points) < 2 * n_bins:
        return math.nan, math.nan, len(points)
    x = np.log(np.array([p[0] for p in points]))
    y = np.array([p[1] for p in points])
    edges = np.quantile(x, np.linspace(0, 1, n_bins + 1))
    bx, by = [], []
    for lo, hi in pairwise(edges):
        m = (x >= lo) & (x <= hi)
        if m.sum() >= 5 and y[m].mean() > 0:
            bx.append(x[m].mean())
            by.append(np.log(y[m].mean()))
    if len(bx) < 3:
        return math.nan, math.nan, len(points)
    slope, icpt = np.polyfit(bx, by, 1)
    return float(slope), float(icpt), len(points)


def main() -> None:
    tape = load_tape()
    t0, t1 = tape[0]["time"], tape[-1]["time"]
    hours = (t1 - t0) / 3.6e6
    coins = sorted({t["coin"] for t in tape})
    print(f"tape: {len(tape):,} trades, {len(coins)} coins, {hours:.2f} h")

    zero = [t for t in tape if t["hash"] == ZERO]
    zero_users = sorted({taker(t) for t in zero})
    print(
        f"zero-hash trades: {len(zero):,} ({len(zero) / len(tape):.1%}), "
        f"taker addresses: {len(zero_users)}"
    )

    # ── labels from the public per-address API ────────────────────────────────
    slice_tid: dict[int, int] = {}
    cover_from: dict[str, int] = {}
    parents: dict[int, dict] = {}
    truncated = 0
    for u in zero_users:
        fills = cached("userTwapSliceFills", u)
        if len(fills) >= 2000:
            truncated += 1
        for f in fills:
            slice_tid[f["fill"]["tid"]] = f["twapId"]
        cover_from[u] = min((f["fill"]["time"] for f in fills), default=t1 + 1)
        for h in cached("twapHistory", u):
            if h.get("twapId") is not None:
                parents[h["twapId"]] = h
    print(
        f"API: {len(slice_tid):,} labelled slice fills, {len(parents):,} parent records, "
        f"{truncated} addresses at the 2000-fill cap"
    )

    # ── is the zero hash a TWAP marker? ───────────────────────────────────────
    covered = [t for t in zero if t["time"] >= cover_from[taker(t)]]
    hit = sum(t["tid"] in slice_tid for t in covered)
    tape_tids = {t["tid"]: t for t in tape}
    in_window = [tid for tid in slice_tid if tid in tape_tids]
    nonzero_slices = sum(tape_tids[tid]["hash"] != ZERO for tid in in_window)
    print("\n[marker]")
    print(
        f"  zero-hash trades within each address's API coverage: {len(covered):,}; "
        f"labelled as TWAP slices: {hit:,} ({hit / max(len(covered), 1):.1%})"
    )
    print(
        f"  labelled slices present in the tape: {len(in_window):,}; "
        f"with a non-zero hash: {nonzero_slices}"
    )

    # ── reconstruction, labels hidden ────────────────────────────────────────
    children = child_orders(tape, set(zero_users))
    label = {}
    for i, c in enumerate(children):
        ids = {slice_tid[t] for t in c["tids"] if t in slice_tid}
        if len(ids) == 1:
            label[i] = ids.pop()
    twap_ids_seen = Counter(label.values())
    multi = [k for k, n in twap_ids_seen.items() if n >= MIN_CHILDREN]
    print("\n[parents in window]")
    print(f"  child orders of these addresses: {len(children):,}; TWAP-labelled: {len(label):,}")
    print(
        f"  TWAP parents with ≥{MIN_CHILDREN} slices in window: {len(multi)} "
        f"→ ≈ {len(multi) / hours * 24 * 30:,.0f} per month at this rate (top {len(coins)} coins)"
    )

    # concurrent same-side parents per (user, coin, side): merging is unavoidable for any heuristic
    spans = defaultdict(list)
    for i, tid in label.items():
        c = children[i]
        spans[(c["user"], c["coin"], c["side"], tid)].append(c["time"])
    by_stream = defaultdict(list)
    for (u, coin, side, _tid), ts in spans.items():
        by_stream[(u, coin, side)].append((min(ts), max(ts)))
    overlapping = 0
    for iv in by_stream.values():
        iv.sort()
        overlapping += sum(b[0] <= a[1] for a, b in pairwise(iv))
    print(
        f"  same-address, same-side TWAP parents overlapping in time: {overlapping} "
        f"(of {len(spans)} parent-streams)"
    )

    print("\n[blind reconstruction vs TWAP labels]  (pairwise, labelled children only)")
    recs = {}
    for g in GAPS_MIN:
        groups = reconstruct(children, g)
        recs[g] = groups
        prec, rec = pair_scores(groups, label)
        mixed = sum(
            any(i in label for i in grp) and any(i not in label for i in grp) for grp in groups
        )
        print(
            f"  gap ≤ {g:>4.0f} min: {len(groups):>5} metaorders; "
            f"precision {prec:.3f}, recall {rec:.3f}; "
            f"{mixed} mix TWAP and non-TWAP children"
        )

    # ── naive impact curves ───────────────────────────────────────────────────
    series = {}
    for coin in coins:
        tc = [t for t in tape if t["coin"] == coin]
        series[coin] = (np.array([t["time"] for t in tc]), np.array([float(t["px"]) for t in tc]))
    ctx = post({"type": "metaAndAssetCtxs"})
    vol_day = {
        u["name"]: float(c["dayNtlVlm"]) for u, c in zip(ctx[0]["universe"], ctx[1], strict=True)
    }
    sigma_day = {}
    for coin in coins:
        ts, px = series[coin]
        grid = np.arange(ts[0], ts[-1], 60_000)
        p = px[np.searchsorted(ts, grid, side="right") - 1]
        r = np.diff(np.log(p))
        sigma_day[coin] = float(r.std() * math.sqrt(1440)) if r.size > 30 else math.nan

    def point(idx: list[int]) -> tuple[float, float] | None:
        cs = [children[i] for i in idx]
        coin, side = cs[0]["coin"], cs[0]["side"]
        p0 = last_price_before(series, coin, cs[0]["time"])
        p1 = last_price_at(series, coin, cs[-1]["time"])
        s = sigma_day.get(coin, math.nan)
        if not (p0 > 0 and p1 > 0 and s > 0 and vol_day.get(coin, 0) > 0):
            return None
        eps = 1.0 if side == "B" else -1.0
        q = sum(c["ntl"] for c in cs) / vol_day[coin]
        return q, eps * math.log(p1 / p0) / s

    twap_groups = defaultdict(list)
    for i, tid in label.items():
        twap_groups[tid].append(i)

    def complete(tid: int) -> bool:
        """Parent started and was scheduled to finish inside the capture window."""
        h = parents.get(tid)
        if not h:
            return False
        start = h["state"]["timestamp"]
        return start >= t0 and start + h["state"]["minutes"] * 60_000 <= t1

    twap_pts = [
        p
        for tid, g in twap_groups.items()
        if len(g) >= MIN_CHILDREN and complete(tid) and (p := point(sorted(g)))
    ]
    n_partial = sum(
        1 for tid, g in twap_groups.items() if len(g) >= MIN_CHILDREN and not complete(tid)
    )
    print(
        f"\n  TWAP parents complete in window: {len(twap_pts)}; "
        f"partial, excluded from the TWAP curve: {n_partial}"
    )
    print(
        "\n[naive impact: I/σ_D vs (Q/V_D)^δ, log-binned; a few hours of data, so indicative only]"
    )
    for name, pts in [("TWAP parents, complete", twap_pts)] + [
        (f"reconstructed, gap ≤ {g:.0f} min", [p for grp in recs[g] if (p := point(grp))])
        for g in GAPS_MIN
    ]:
        d, _, n = impact_fit(pts)
        print(
            f"  {name:<32} n={n:>5}  δ̂ = {d:.2f}"
            if not math.isnan(d)
            else f"  {name:<32} n={n:>5}  δ̂ = n/a"
        )

    # how far intended parent size differs from what executed in-window
    ratios = []
    for tid, g in twap_groups.items():
        h = parents.get(tid)
        if h and len(g) >= MIN_CHILDREN:
            ratios.append(sum(children[i]["sz"] for i in g) / float(h["state"]["sz"]))
    if ratios:
        q = np.quantile(ratios, [0.1, 0.5, 0.9])
        print(
            "\n[parent size] executed-in-window / intended size: "
            f"p10 {q[0]:.2f}, median {q[1]:.2f}, p90 {q[2]:.2f}"
        )


if __name__ == "__main__":
    main()
