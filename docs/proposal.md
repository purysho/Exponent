# Exponent — An Open Observatory for Market Scaling Laws

Oliver Mclennan · draft 2, revised 2026-10-05 · changes from draft 1 are explained in [`review.md`](review.md)

## Summary

Exponent is a standing, open court for the scaling laws that quant finance argues about. It scores every estimator against synthetic markets where the true answer is known, maps where each one can and cannot identify the answer, and only then rules on real, fully public market data under pre-registered rules.

- **The pitch:** two live debates — is volatility rough, and is the square-root law of impact universal — each hinge on one exponent estimated from noisy data. Individual papers audit their own estimator on their own simulator; nobody runs a *shared* court that every estimator passes through under the same truths, noise and scoring, and nobody has audited the impact side against real labelled ground truth.
- **Why now:** fully public, trader-attributed market data now exists. Hyperliquid's tape carries wallet addresses *and* labels its protocol-native TWAP orders, so real metaorders with known parents can be used as ground truth. Polymarket's v1 archive gives every trade with a known outcome.
- **Why us:** the decisive stage runs on synthetic data, where nobody has a data advantage, and every real-data stage uses public sources.
- **First two cases:** (1) whether volatility roughness is identifiable, and where it is, whether it is present; (2) whether Hyperliquid's departure from the square-root law survives validated metaorder reconstruction.
- **Success looks like:** a benchmark that new roughness or impact papers are expected to run through, an arXiv paper per case with a falsifiable verdict per asset class, and engagement from both sides of each debate.
- **Honest odds:** the roughness half is now partly scooped (see Prior work), so its value is breadth and permanence, not first-mover novelty. The impact half has a genuinely new angle. Low odds of shocking the field; decent odds of becoming respected infrastructure.

## The problem

Two debates that move real money are stuck on the same failure: an exponent measured from noisy, finite data with estimators that are validated, if at all, only by their own authors on their own simulators.

### Debate 1: is volatility rough?

The Hurst exponent H measures how jagged a path is. H = 0.5 is Brownian motion; below 0.5 is rougher.

- **Rough:** Gatheral, Jaisson and Rosenbaum estimated H ≈ 0.1 for log-volatility; a generation of rough-volatility pricing models rests on it. Noise-robust estimators that work on high-frequency prices rather than a realised-variance proxy (Fukasawa, Takabatake and Westphal's quasi-likelihood; Bolko, Christensen, Pakkanen and Veliyev's GMM) also report H well below 0.5. This is the rough camp's strongest evidence and any verdict must engage with it.
- **Artefact:** Cont and Das showed realised volatility looks rough even when true volatility is smooth, because the realised-variance proxy injects estimation error ([arXiv:2203.13820](https://arxiv.org/abs/2203.13820)).
- **Path-dependent:** Guyon and Lekeufack found up to 90% of the variance of equity-index implied volatility is explained by past returns ([SSRN 4174589](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4174589)).
- **Still open in 2026:** new estimators keep arriving — e.g. a pointwise, noise-robust H(t) estimator ([arXiv:2606.25771](https://arxiv.org/abs/2606.25771)). A Bitcoin study finds low roughness estimates (≈ 0.05–0.09) but shows they shift with sampling frequency and measurement design ([arXiv:2507.00575](https://arxiv.org/abs/2507.00575)). An August 2026 audit finds that at daily sampling, calibrated to BTC, ETH and the S&P 500, none of three common estimators returns an identified reading ([SSRN 7346318](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7346318)).

### Debate 2: is the square-root law of impact universal?

The law says a metaorder's price impact grows with the square root of its total size.

- **Universal:** an eight-year study of the Tokyo Stock Exchange gave the strongest evidence yet for an exponent of ½ ([Physics, 2025](https://physics.aps.org/articles/v18/196)).
- **Not universal, at least on Hyperliquid:** Barone and Lillo reconstruct 4.3 million hidden metaorders from address-level data and find their temporary impact "strongly curved and saturating", with pooled elasticities below ½; protocol-native TWAPs, by contrast, sit close to a regular power law. In their words, "a single square-root law does not provide a universal description of temporary impact" in that sample ([arXiv:2606.15715](https://arxiv.org/abs/2606.15715)). Their headline is sunshine trading; the impact-shape finding is a side result, which is why it deserves an audit.
- **Functional form is itself contested:** Zarinelli et al. argued a logarithmic form can fit better than any power law; a saturating curve fitted with a power law will report a low exponent.
- **Origin:** Maitrier, Loeper, Kanazawa and Bouchaud argue impact is mechanical rather than information-driven ([Quantitative Finance, 2026](https://www.tandfonline.com/doi/abs/10.1080/14697688.2026.2615106)); information-based theories have not conceded.

### The shared failure

Power-law exponents are easy to get wrong: finite samples, proxy error, noise, fitting-range choices and — for impact — the heuristic that groups trades into metaorders can all manufacture one. Each paper builds its own pipeline on its own data with its own simulator, so results cannot be compared and no estimator is scored by anyone but its authors.

## Research questions

Each question has a pre-stated decision rule, so the project cannot quietly redefine success. Exact thresholds are fixed in the registered config before the relevant data is touched.

The two cases are **independent tracks** with their own gates. A failure on the roughness track does not stop the impact track.

### Track R — roughness

| # | Question | Decision rule |
| --- | --- | --- |
| R1 | For which combinations of true H, vol-of-vol, sampling frequency, noise and sample length can each estimator distinguish rough (H ≤ 0.2) from smooth (a semimartingale null and H ≥ 0.5)? | Output is an **identifiability map** per estimator. R1 "fails" if no estimator's identifiable region contains the operating point of any real dataset — then R2 reports "undecidable at current data", which is still a publishable result. |
| R2 | At each real dataset's calibrated operating point, using only estimators identified there, is volatility rough, smooth or undecidable? | Per asset class and sampling frequency: *rough* if the registered interval lies inside H ≤ 0.2, *smooth* if inside H ≥ 0.4, *undecidable* otherwise. No directional hypothesis is staked in advance. |
| R3 | Which volatility model forecasts later realised volatility best, out of sample? | Candidates: HAR-RV (the standard baseline), rough (RFSV), path-dependent (Guyon–Lekeufack), a classical one-factor SV. Ranked by QLIKE; "differ measurably" means outside the Model Confidence Set at the registered level. R3 tests usefulness, not truth: a model can forecast well for the wrong reason. |

### Track I — impact

| # | Question | Decision rule |
| --- | --- | --- |
| I1 | How much do metaorder-reconstruction heuristics and fitting choices bias the measured impact exponent? | Scored two ways: on synthetic markets with a known exponent, and on Hyperliquid's native TWAPs, whose parent orders are known, by hiding the labels and reconstructing. A reconstruction-plus-fit pipeline passes if it recovers the known exponent within the registered tolerance. |
| I2 | Is Hyperliquid's sub-½, saturating impact real, or produced by the method? | Re-measure with passing pipelines only. *Artefact* if they recover ½ (or a pure power law) where the original method did not; *real* if the departure survives; *undecidable* if intervals span both. Power-law and logarithmic forms are compared, not assumed. |
| I3 *(provisional)* | On Polymarket, where price is a probability in [0, 1] and the outcome is known, is impact concave in log-odds, and do metaorders that turn out to be right impact prices differently *during* execution from those that turn out wrong? | Directly tests the mechanical-vs-information debate: a purely mechanical origin predicts the same impact path during execution regardless of being right, with differences only in permanence. Provisional until a literature check confirms nobody has done it. |

## Prior work and positioning

Exponent's edge is neutrality, breadth and permanence, not data or a new estimator.

**Nearest neighbours, and how Exponent differs:**

| Work | What it does | What it leaves open |
| --- | --- | --- |
| Lumor, *When is volatility roughness identifiable?* (SSRN, Aug 2026) | Rough-Bergomi truth plus a smooth null; three estimators (structure-function, p-variation, MF-DFA); identifiability map over vol-of-vol and sampling window; open code; BTC, ETH, S&P 500 at daily RV. | Daily RV only; no high-frequency noise-robust estimators; no microstructure noise models; a one-off paper, not a standing benchmark; no impact. |
| Angelini, *A critical review of Hurst exponent estimation* (Annali MEMOTEF) | Organises estimators and their biases into one framework. | A review: no shared code, no scoring. |
| Fukasawa et al.; Bolko et al.; Cont and Das | Each validates its own estimator on its own simulations. | Not cross-scored under common truths and noise. |
| Barone and Lillo (arXiv, Jun 2026) | Hyperliquid metaorder impact; TWAP vs hidden. | Reconstruction heuristic not validated against TWAP labels; exponent is a side result. |

**Ideas checked and dropped before this proposal:**

- **Formally verified quant finance:** done — [formal-mathfin](https://github.com/oxarbitrage/formal-mathfin) already proves Black–Scholes, Itô calculus and the FTAP in Lean 4.
- **Descriptive Polymarket microstructure:** crowded — 2026 papers cover 30 billion order-book events ([arXiv:2604.24366](https://arxiv.org/abs/2604.24366)), NBA arbitrage ([arXiv:2605.00864](https://arxiv.org/abs/2605.00864)) and a full trade archive ([arXiv:2606.04217](https://arxiv.org/abs/2606.04217)).
- **A daily-RV roughness audit as the headline:** done by Lumor (above). Exponent must go further — intraday sampling, noise-robust estimators, and a standing leaderboard — or it adds nothing.

**What Exponent deliberately does not do:** propose a new estimator as its headline (it may add one, judged by the same court); use proprietary data; sell trading signals.

## Data sources

All sources are free to licence; one has small transfer costs.

| Source | What it gives | Coverage | Used for | Limits |
| --- | --- | --- | --- | --- |
| Synthetic generators (ours) | Price paths with known H; order flow with known impact law; configurable noise | Unlimited | R1, I1 | Only as realistic as the noise models — so noise strength is calibrated to each real dataset |
| [Hyperliquid archive](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data) | Address-level fills (from 2025-03; block-batched from 2025-07-27); L2 book snapshots; native TWAP executions | Fills ≈ 15 months; book snapshots in the official archive since 2023 | I1, I2; crypto side of R2/R3 | Official S3 is **requester-pays** and "data may be missing"; free community mirrors exist. Barone and Lillo's Dec-2025 book start was their sample choice, not a data limit. Whether TWAP ids are present in public fills is the first thing to verify. |
| [Polymarket-v1 archive](https://arxiv.org/abs/2606.04217) | 1.2 billion on-chain trades across 1.3 million markets, with outcomes | 2022-11-21 to 2026-04-28 | I3 | Off-chain cancellations missing; licence to confirm |
| [Binance public data](https://data.binance.vision) | Trades and klines | Multi-year, many pairs | R2, R3 crypto | Single venue; terms to confirm before redistribution |
| CBOE VIX history; Deribit DVOL | Daily implied-vol indices | Decades (VIX); since 2021 (DVOL) | R3 path-dependent model | Daily only |
| Equity intraday | — | — | Equity side of R2 | No good free source. The Oxford-Man Realized Library is discontinued. Equity R2 is likely limited to daily scales, where Lumor already finds non-identification — say so up front. |

Rule: the repository ships download scripts and checksums, never raw data, unless a licence allows it.

## Methodology

Every claim passes three stages in order; a stage's failure stops the claim rather than being worked around.

1. **Synthetic validation (the court).**
   - *Truths.* Roughness: fractional log-vol with H ∈ {0.05, 0.1, 0.2, 0.3}; smooth alternatives — a semimartingale SV null (H = 0.5) and fractional log-vol with H ∈ {0.5, 0.7, 0.9}, because Cont and Das's argument is that *smooth* volatility produces apparent roughness; path-dependent volatility (Guyon–Lekeufack). Impact: order flow from wallets running metaorders with impact exponent δ ∈ {0.3, 0.4, 0.5, 0.6} and a logarithmic alternative, with realistic schedules (uniform, front-loaded U-shape), overlap, and sub-account splitting.
   - *Observation.* Estimators never see the truth, only an observation of it: realised-variance proxies at several sampling frequencies; microstructure noise (IID, bid–ask bounce, price discreteness, path-dependent noise); for impact, the public fill tape.
   - *Calibration.* Noise strength, vol-of-vol and sample length are measured from each real dataset, which places that dataset on the map. Sensitivity outside the calibrated band is reported, not used to fail estimators.
   - *Scoring.* Bias, RMSE, interval coverage, and power at 5% size to separate the hypotheses that matter (H = 0.1 vs smooth; δ = 0.4 vs 0.5). Many estimators publish no confidence interval, so the court supplies a uniform parametric-bootstrap interval for all of them and scores native intervals separately where they exist. Non-answers ("no root", "out of range") are recorded as outcomes, not dropped.
   - *No overfitting the court.* A development grid (for tuning) and a disjoint test grid (different seeds and parameter points) that is scored once per registered estimator version.
2. **Historic measurement.** Apply only estimators identified at the dataset's operating point; report a verdict with an interval, or "undecidable".
3. **Out-of-sample prediction.** Fit on an early window, predict a later one: realised volatility for R3 (QLIKE, with Model Confidence Set), execution cost of held-out metaorders for I2.

**Pre-registration discipline:**

- Estimators, grids, windows, thresholds and scoring rules are committed before the relevant data is analysed, and each registration is published as a GitHub release archived to Zenodo. Git commit dates are set by the author and prove nothing; the archive's timestamp and DOI are what a sceptic can check.
- The final 20% of each time series is a holdout that the code refuses to load until a final registration exists. Hyperliquid's history is short, so Track I also holds out a registered set of markets.
- Every run is reported, including failures; many estimators × classes means multiplicity is controlled and stated. A rule changed after seeing data needs a new, dated registration and is flagged in the paper.

The out-of-sample score for volatility forecasts is QLIKE, which ranks forecasts consistently even when the realised-volatility proxy is noisy (Patton, 2011):

```latex
\mathrm{QLIKE}(\hat\sigma^2, \sigma^2) = \frac{\sigma^2}{\hat\sigma^2} - \log\frac{\sigma^2}{\hat\sigma^2} - 1
```

## Architecture

A small Python codebase with the mathematics kept free of all I/O, so every estimator is testable in milliseconds and every result is reproducible from one command. Real data enters only through adapters, and only estimators the court identified at a dataset's operating point may run on it. Full outline: [`architecture.md`](architecture.md).

## Milestones

Riskiest first. Each gate is checked before the next milestone starts; a failed gate is reported publicly. Detail and sizing: [`build-plan.md`](build-plan.md).

| | Milestone | Gate |
| --- | --- | --- |
| M0a | Harness reproduces three known roughness results on synthetic data (GJR recovery on spot vol; Cont–Das spurious roughness; Lumor's daily-RV non-identification) | All three reproduced within tolerance |
| M0b | One week of Hyperliquid fills: reconstruct metaorders, check TWAP labels, naive impact curve | TWAP labels present and plentiful enough for I1 |
| M1 | Roughness court v1: ≥ 6 estimators incl. noise-robust high-frequency ones; identifiability maps; registration v1 | Maps stable across seeds; benchmark preprint |
| M2 | Calibrate real datasets onto the map; R2 verdicts; R3 forecasting; paper 1 | Holdout opened once; paper submitted |
| M3 | Impact court: synthetic metaorder market + TWAP-label validation; I2 verdict; paper 2 | Validated pipeline exists, or "undecidable" reported |
| M4 | I3 on Polymarket (if the literature check clears it) | — |

Which track leads paper 1 is decided after M0 (see Open decisions).

**What deliberately waits:** the leaderboard site, the hosted API and any business work wait until the first verdict ships. Comfortable infrastructure is earned after the hard question is answered.

## Risks and mitigations

The largest risk is scientific: getting a wrong answer with confidence.

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Synthetic noise is unrealistic | Estimators pass a test real data would fail | Calibrate noise to each dataset; vary widely; report sensitivity |
| Roughness half already scooped (Lumor, Aug 2026) | Paper 1 looks derivative | Go where Lumor did not: intraday, noise-robust estimators, standing benchmark; cite and reproduce Lumor in M0a; consider leading with Track I |
| Researching into a preferred answer | Credibility lost with both camps | Externally timestamped registration; holdouts enforced in code; every run reported |
| TWAP labels absent or too sparse in public fills | I1's real-data ground truth disappears | M0b checks this first; fall back to synthetic-only validation |
| TWAPs are a different execution regime (visible) | Their labels validate reconstruction, not the hidden-order impact law | State this; use TWAPs only to score detection and fitting bias |
| Experts find a mathematical error | Reputation damage | Invite named researchers from each camp to review the harness before verdicts |
| Data licences or egress costs | Not reproducible by others | Scripts and checksums, not data; document cost (tens of dollars) and free mirrors |
| Scope creep into a general quant library | Nothing ships | Two tracks only until both have verdicts |

## Deliverables, audience and business model

**Deliverables:** the repository with one-command reproduction of every figure; a public leaderboard of estimators × noise models with the current verdict per asset class; two arXiv papers; a plain-language explainer.

**Audience:** researchers in each camp; quant desks and execution teams; students learning rough volatility and microstructure.

**Business model (only after both verdicts ship):** validation-as-a-service for private estimators and execution-cost models; hosted execution-cost models fitted on public crypto and prediction-market data; consulting and teaching. Sponsorship from exchanges whose data the verdicts concern is a conflict of interest for a project selling neutrality — accept it only with a published disclosure, or not at all.

## Open decisions

- [ ] **Paper 1 track.** Roughness is partly scooped; the TWAP-labelled impact audit looks novel. Recommendation: decide after M0, leaning impact if M0b's gate passes.
- [ ] Contact Lumor: reproduce their result in M0a and invite them to submit estimators to the court.
- [ ] Name: `exponent` is taken on PyPI (an unrelated, dormant package). Distribute as `exponent-court`, import as `exponent`.
- [ ] Licence: MIT for code; CC BY for results and figures.
- [ ] Literature check on I3 before committing to it.
- [ ] Confirm licences: Binance public data, Polymarket-v1 archive, Hyperliquid archive.
- [ ] Hyperliquid source: official requester-pays bucket or a free mirror (checksums against the official bucket either way).
- [ ] When to approach reviewers from each camp: after M1 (harness only) is recommended, before any verdict.
- [ ] Compute: laptop for M0–M1; a capped cloud budget only for final grids.
