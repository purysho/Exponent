"""M0b spike: capture the public Hyperliquid trade tape for the top-N perps.

Throwaway code (see docs/build-plan.md). Writes one gzipped JSON line per
trade to data/trades-<start>.jsonl.gz. Trades carry both counterparties'
addresses; a zero `hash` is the candidate marker for TWAP slices.

    uv run --with websockets python capture.py --coins 40 --hours 3
"""

from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import time
import urllib.request
from pathlib import Path

INFO = "https://api.hyperliquid.xyz/info"
WS = "wss://api.hyperliquid.xyz/ws"


def top_coins(n: int) -> list[str]:
    req = urllib.request.Request(
        INFO, data=b'{"type":"metaAndAssetCtxs"}', headers={"Content-Type": "application/json"}
    )
    meta, ctxs = json.load(urllib.request.urlopen(req, timeout=30))
    rows = [
        (float(c["dayNtlVlm"]), u["name"])
        for u, c in zip(meta["universe"], ctxs, strict=True)
        if not u.get("isDelisted")
    ]
    return [name for _, name in sorted(rows, reverse=True)[:n]]


async def run(coins: list[str], seconds: float, out: Path) -> None:
    import websockets

    deadline = time.time() + seconds
    n = 0
    with gzip.open(out, "at") as fh:
        while time.time() < deadline:
            try:
                async with websockets.connect(WS, ping_interval=20, max_size=None) as ws:
                    for c in coins:
                        sub = {"method": "subscribe", "subscription": {"type": "trades", "coin": c}}
                        await ws.send(json.dumps(sub))
                    while time.time() < deadline:
                        msg = json.loads(await asyncio.wait_for(ws.recv(), 60))
                        if msg.get("channel") != "trades":
                            continue
                        for t in msg["data"]:
                            fh.write(json.dumps(t) + "\n")
                            n += 1
                        if n and n % 50_000 < len(msg["data"]):
                            print(f"{time.strftime('%H:%M:%S')} {n} trades", flush=True)
            except Exception as exc:  # reconnect on any drop; a gap is logged, not hidden
                print(f"{time.strftime('%H:%M:%S')} reconnect after {exc!r}", flush=True)
                await asyncio.sleep(2)
    print(f"done: {n} trades -> {out}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coins", type=int, default=40)
    ap.add_argument("--hours", type=float, default=3.0)
    args = ap.parse_args()
    coins = top_coins(args.coins)
    out = Path(__file__).parent / "data" / f"trades-{int(time.time())}.jsonl.gz"
    out.parent.mkdir(exist_ok=True)
    print("coins:", ",".join(coins), flush=True)
    asyncio.run(run(coins, args.hours * 3600, out))


if __name__ == "__main__":
    main()
