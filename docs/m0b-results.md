# M0b results — Hyperliquid TWAP spike, 2026-10-05

The question, from [`build-plan.md`](build-plan.md): can Hyperliquid's native TWAP parents be recovered from public data, in enough numbers to give the impact track a real-data ground truth?

The full output is in [`spikes/m0b_hyperliquid/analysis-2026-10-05.txt`](../spikes/m0b_hyperliquid/analysis-2026-10-05.txt), and the code in [`spikes/m0b_hyperliquid/`](../spikes/m0b_hyperliquid/). The raw tape is not committed, so this run cannot be reproduced exactly. Re-running `capture.py` produces a new sample.

## Verdict: **labels pass; impact is undetermined**

| Gate part | Result |
| --- | --- |
| TWAP slices identifiable in the public tape | **Yes.** An all-zero transaction hash marks them: 99.8% of 31 764 zero-hash trades are confirmed slices, and 0 of 31 531 confirmed slices lack the marker. |
| Parent order of each slice recoverable | **Yes, live.** `userTwapSliceFills` gives each slice's `twapId`. `twapHistory` gives the parent's intended size, duration, side and start time, so the true Q is known, not reconstructed. |
| Enough parents | **Yes.** 279 parents with ≥ 10 slices in 2.1 hours across the top 40 perps, about 94 000 a month. Target: thousands. |
| A first impact curve | **No.** Only 83 parents both started and finished inside the window, too few for a binned exponent fit. The exponents fitted to reconstructed metaorders (−0.27 to 0.00) are not meaningful at this sample size. |

## What was measured

- **Data:**
  - 196 458 trades from the public websocket over 2.14 hours (20:42–22:51 UTC). The capture was stopped by the environment's 2-hour background limit, not the planned 3 hours.
  - 40 coins by daily volume.
  - For all 180 wallets that took liquidity in a zero-hash trade: their TWAP slice fills and parent records, fetched after the capture.
- **Marker test:** zero-hash trades were checked against each wallet's labelled slice fills, within the time span those labels cover. The 0.2% of zero-hash trades left unlabelled are probably other protocol-generated trades (e.g. liquidations); this was not checked.
- **Blind reconstruction:** a Barone–Lillo-style rule was applied to each wallet's taker child orders with the labels hidden: same wallet, coin and side; gaps ≤ G; ≥ 10 child orders. It was scored pairwise against the true parents.

| Max gap G | Metaorders | Precision | Recall | Groups mixing TWAP and other fills |
| --- | --- | --- | --- | --- |
| 1 min | 226 | 0.43 | 0.85 | 21 |
| 5 min | 200 | 0.46 | 1.00 | 29 |
| 15 min | 224 | 0.46 | 1.00 | 33 |

**Recall is near-perfect, but more than half of the pairs the heuristic groups belong to different parents.** The cause is visible directly: 61 of 414 wallet/coin/side streams ran overlapping TWAPs on the same side, which no address-and-gap rule can separate. A merged metaorder overstates Q, and Q sits on the x-axis of every impact fit. This is the method-driven bias that the impact track exists to measure, now shown on real labelled data.

## Limits

- **History:**
  - The per-wallet API returns only the 2 000 most recent slice fills and parent records, and 150 of 180 wallets hit that cap. Labels can therefore be collected **live**, but not backfilled through the API.
  - Bulk history is in Hyperliquid's S3 archive, which is requester-pays, as is the free mirror. Whether archived fills keep the zero hash and the parent id is unverified.
  - This environment has no AWS credentials.
- **Window:** two hours is enough to answer the labels question and nowhere near enough for impact. Most parents run far longer: the median parent executed only 14% of its intended size inside the window.
- **Taker side only:** maker fills were not used.

## What it means for the impact track

- **The core claim of the impact track holds:** real metaorders with known parents exist in public data at volume.
- **Two ways to get enough history for impact estimates:**
  - A **continuous live collector**, about a month at the rates seen here, labelling as it goes.
  - **S3 access**, with an AWS account, costing cents to dollars, then a check of whether archived fills carry the marker and the parent id.
- **The reconstruction bias** (precision ≈ 0.45) is the first result worth registering for the impact track's I1 question.
