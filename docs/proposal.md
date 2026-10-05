# Exponent — An Open Observatory for Market Scaling Laws

Oct 6, 2026 · @Oliver Mclennan

## Summary

Exponent is an open, reproducible court for the scaling laws that quant finance argues about. It tests every estimator against synthetic markets where the true answer is known, then rules on real, fully public market data.

- **The pitch:** two of the field's biggest live debates hinge on one number estimated from noisy data, and nobody has checked whether the estimators can be trusted. Exponent does that check, in the open.
- **Why now:** fully public, trader-attributed market data now exists (Hyperliquid, Polymarket), and the debates are active in 2026 papers.
- **Why us:** the decisive stage runs on synthetic data, where nobody has a data advantage. Every real-data stage uses free sources only.
- **First two cases:** (1) whether volatility is genuinely rough; (2) whether the square-root law of market impact is universal.
- **Success looks like:** a public benchmark that any future roughness or impact paper is expected to pass, an arXiv paper with a falsifiable verdict per asset class, and citations from both sides of each debate.
- **Honest odds:** low that it shocks the field; decent that it becomes respected infrastructure. It is real research and must be held to that standard.

## The problem

Two debates that move real money are stuck on the same failure: an exponent measured from noisy, finite data with estimators nobody has validated.

### Debate 1: is volatility rough?

The Hurst exponent H measures how jagged a path is. H = 0.5 is ordinary Brownian motion; below 0.5 is rougher.

- **Rough:** Gatheral, Jaisson and Rosenbaum estimated H ≈ 0.1 for log-volatility. A generation of rough-volatility pricing models rests on it.
- **Artefact:** Cont and Das showed that realized volatility looks rough even when true volatility is smooth, and argue the roughness comes from estimation error ([arXiv:2203.13820](https://arxiv.org/abs/2203.13820)).
- **Path-dependent:** Guyon and Lekeufack found that up to 90% of the variance of equity-index implied volatility is explained by past returns, and list "spurious roughness" among their keywords ([SSRN 4174589](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4174589)).
- **Still open in 2026:** a June 2026 paper frames it as an unsolved statistical problem ([arXiv:2606.25771](https://arxiv.org/html/2606.25771)); a Bitcoin study found roughness estimation fails outright ([arXiv:2507.00575](https://arxiv.org/html/2507.00575v3)).

### Debate 2: is the square-root law of impact universal?

The law says a trade's price impact grows with the square root of its size.

- **Universal:** an eight-year survey of the Tokyo Stock Exchange gave the strongest evidence yet for a universal exponent of ½ ([Physics, 2025](https://physics.aps.org/articles/v18/196)).
- **Not universal:** a June 2026 study of Hyperliquid, where every trade carries a wallet address, found an exponent well below ½ and no single law ([arXiv:2606.15715](https://arxiv.org/html/2606.15715v1)).
- **Origin unsettled:** whether impact is mechanical or information-driven is still debated ([Quantitative Finance, 2026](https://www.tandfonline.com/doi/abs/10.1080/14697688.2026.2615106)).

### The shared failure

Power-law exponents are easy to get wrong: finite samples, noise and fitting-range choices can all manufacture one. Each paper builds its own pipeline on its own data, so results cannot be compared and estimators are never tested against a known truth.

## Research questions and hypotheses

Each question has a pre-stated result that would count as a loss, so the project cannot quietly redefine success.

| # | Question | Hypothesis to test | Counts as a loss for the hypothesis |
| --- | --- | --- | --- |
| Q1 | Can any published roughness estimator tell H = 0.1 from H = 0.5 under realistic, non-IID microstructure noise? | At least one estimator separates them at the sample sizes real data provides. | Every estimator's error bars overlap both values at realistic noise. |
| Q2 | Once only validated estimators are used, is volatility rough, smooth, or path-dependent, by asset class? | The verdict differs by asset class (equity index vs crypto). | One verdict holds across all classes, or no validated estimator exists (then Q2 reports "undecidable at current data"). |
| Q3 | Which volatility model forecasts later realized volatility best, out of sample? | Rough, path-dependent and classical one-factor models differ measurably. | No model beats the others beyond pre-registered tolerance. |
| Q4 | Is Hyperliquid's sub-½ impact exponent real, or produced by the estimation method? | The low exponent survives estimators validated on synthetic order books. | Validated estimators recover ½ on the same data. |
| Q5 | Does the square-root law hold when the price is a probability bounded in \[0, 1\] and the outcome is known (Polymarket)? | Impact is concave but bends near 0 and 1. | Impact is linear or shows no stable shape. (Q5 is provisional until a literature check confirms nobody has tested it.) |

Q1 gates everything. If it fails, the honest result is a paper saying the debate cannot be settled with current estimators, which is still publishable.

## Prior work and positioning

Exponent's edge is neutrality and reproducibility, not data or a new estimator. Better-resourced groups own the data; nobody owns the referee role.

**Ideas checked and dropped before this proposal:**

- **Formally verified quant finance:** done. An open Lean 4 library already proves Black–Scholes, Itô calculus and the Fundamental Theorem of Asset Pricing ([formal-mathfin](https://github.com/oxarbitrage/formal-mathfin)).
- **Descriptive Polymarket microstructure:** crowded. 2026 papers already cover 30 billion order-book events ([arXiv:2604.24366](https://arxiv.org/abs/2604.24366)), NBA arbitrage ([arXiv:2605.00864](https://arxiv.org/abs/2605.00864)) and a full trade archive ([arXiv:2606.04217](https://arxiv.org/abs/2606.04217)).

**What Exponent deliberately does not do:**

- Propose a new estimator as its headline. It may add one, but only judged by the same court as everyone else's.
- Use proprietary data. Every real-data result must be reproducible from free sources.
- Sell trading signals. The output is measurement, not alpha.

**Where it sits:** existing papers each test one estimator on one dataset. Exponent is the shared test bench they all run through: same synthetic ground truth, same noise models, same scoring, same public data.

## Data sources

All data is free. The most important source is the one we generate ourselves.

| Source | What it gives | Coverage | Used for | Limits |
| --- | --- | --- | --- | --- |
| Synthetic generator (ours) | Price and order-flow paths with known H and known impact exponent, plus configurable noise | Unlimited | Q1, estimator validation for Q4 and Q5 | Only as realistic as the noise models; noise models must be documented and varied |
| [Hyperliquid](https://arxiv.org/html/2606.15715v1) | On-chain order book with every trade tied to a wallet | Trades longer; order-book snapshots from Dec 15, 2025 only | Q4, crypto side of Q2 and Q3 | Under a year of book history; crypto perps only |
| [Polymarket-v1 archive](https://arxiv.org/abs/2606.04217) | Every on-chain trade of the first-generation exchange, with known outcomes | Nov 21, 2022 to Apr 28, 2026 | Q5 | Off-chain cancellations missing; v2 exchange needs separate capture |
| Binance public trade files | Historical crypto tick data | Multi-year, many pairs | Q2 and Q3 crypto volatility | Single venue; licensing to be confirmed before redistribution |
| Equity-index data (to be chosen) | Daily or intraday index levels and implied volatility | Varies by source | Equity side of Q2 and Q3 | Free intraday equity data is scarce; may limit Q2 to daily scales for equities |

Rule: the repository ships download scripts and checksums, never redistributed raw data, unless a source's licence allows it.

## Methodology

Every claim passes three stages in order, and a stage's failure stops the claim rather than being worked around.

1. **Synthetic validation (the court).** Generate paths where the truth is known, contaminate them, and score each estimator.
   - Ground truths: fractional volatility with H in {0.05, 0.1, 0.2, 0.3, 0.5}; path-dependent volatility (Guyon–Lekeufack form); classical one-factor stochastic volatility; order flow with impact exponents in {0.3, 0.4, 0.5, 0.6}.
   - Noise models: IID noise, bid–ask bounce, price discreteness, and the path-dependent noise Cont and Das argue matters. Each at several strengths.
   - Scoring per estimator: bias, variance, coverage of stated confidence intervals, and the smallest sample at which it separates the hypotheses that matter (H = 0.1 vs 0.5; exponent 0.4 vs 0.5).
   - An estimator passes only if it meets pre-registered thresholds across all noise models at realistic sample sizes.
2. **Historic measurement.** Apply only passing estimators to the public data, per asset class, reporting a verdict with error bars, or "undecidable" where error bars span the hypotheses.
3. **Out-of-sample prediction.** Fit each competing model on an early window, then predict a later window it never saw: realized volatility for Q3, execution cost of large trades for Q4. The model that predicts better wins, not the one that fits better.

**Pre-registration discipline (protects against backtest overfitting):**

- Estimators, parameter grids, fitting windows, pass thresholds and scoring rules are committed to the repository, with a timestamp, before any real data is analysed.
- The final 20% of each historic dataset is a sealed holdout, opened once, at the end.
- Every run is reported, including failures. Changing a rule after seeing data requires a new, dated registration and is flagged in the paper.

The out-of-sample score for volatility forecasts is QLIKE, which is robust to noise in the realized-volatility proxy:

```latex
\mathrm{QLIKE}(\hat\sigma^2, \sigma^2) = \frac{\sigma^2}{\hat\sigma^2} - \log\frac{\sigma^2}{\hat\sigma^2} - 1
```

## Required architecture

A small Python codebase with the mathematics kept free of all input and output, so every estimator is testable in milliseconds and every result is reproducible from one command.

&#91;embedded content: Exponent data flow · court, measurement, out-of-sample test\]

Real data enters only through adapters, and only estimators that passed the court are allowed to run on it.

### Layers

Dependencies point inward: interfaces → application → domain ← infrastructure.

- **Domain (pure maths, no I/O):** path generators, noise models, the estimator registry, scoring functions, volatility and impact models. Every function is deterministic given a seed.
- **Ports:** one `DataSource` interface (fetch, verify checksum, return a typed frame) and one `ResultStore` interface. Each has a real adapter and a fake for tests.
- **Infrastructure:** one adapter per data source (Hyperliquid, Polymarket-v1, Binance, equity index), plus a Parquet result store with a hash manifest.
- **Application:** the court runner, the measurement pipeline and the out-of-sample pipeline. Each reads a pre-registered config and refuses to run if the config changed after registration.
- **Interfaces:** a command-line tool (`exponent court`, `exponent measure`, `exponent reproduce fig3`) and a static leaderboard site.

### Technology

| Part | Choice | Why |
| --- | --- | --- |
| Language | Python 3.12 | The field's lingua franca; reviewers can read it |
| Simulation | NumPy, SciPy, Numba | Fast Monte Carlo without leaving Python |
| Data | Polars, Parquet, DuckDB | Columnar, fast, file-based, no server |
| Configs and pre-registration | YAML, hashed and committed with a timestamp | The hash is stamped on every result |
| Environment | uv lockfile | Exact reproduction of dependencies |
| Quality | pytest, Hypothesis property tests, ruff, mypy | Property tests check estimator invariants; static analysis on adapters |
| CI | GitHub Actions | Lint, type-check, tests, and a small reproduction run on every push |
| Site and paper | Static site with charts; LaTeX via Quarto | Figures generated by the same code as the paper |

### Repository layout

```
exponent/
  domain/          generators, noise, estimators, scoring, models
  ports/           DataSource, ResultStore interfaces
  adapters/        hyperliquid, polymarket, binance, equity (+ fakes)
  app/             court, measure, oos pipelines
  cli/             command-line entry points
registry/          pre-registered configs, hashed and dated
results/           Parquet outputs + manifest (git-ignored, reproducible)
site/              leaderboard
paper/             manuscript and figure scripts
tests/             unit, property, one end-to-end reproduction
```

### Reproducibility and compute

- Every result row carries the config hash, code commit, seed and data checksum.
- Monte Carlo grids start coarse on a laptop. A capped cloud budget is used only for the final grids, if needed.

## Project outline and milestones

The riskiest question goes first: if the harness cannot reproduce a known result, nothing after it is trustworthy, and we find out before spending anything on data.

&#91;embedded content: Milestones M0–M5 with stop gates\]

Milestones run top to bottom; each gate is checked before the next milestone starts, and a failed gate is reported publicly, not hidden.

**What deliberately waits:** the leaderboard site, the hosted API and any business work wait until M3 ships. Following the house standard, comfortable infrastructure is earned after the hard question is answered, not before.

**Effort:** not estimated yet. M0 is small enough to size after a first session; later milestones are sized from what M0 reveals.

## Risks and mitigations

The largest risk is scientific, not technical: getting a wrong answer with confidence.

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Synthetic noise models are unrealistic | Estimators pass a test that real data would fail | Vary noise models widely; calibrate their strength to measured spreads and tick sizes in the real data; report sensitivity |
| Researching our way into a preferred answer | Credibility lost with both sides | Pre-registration, sealed holdouts, every run reported |
| Better-resourced groups publish first | Novelty reduced | The benchmark stays useful even if the verdict is scooped; publish the harness early as a preprint |
| Experts find a mathematical error | Reputation damage | Invite named researchers from each camp to review the harness before the verdict is released |
| Hyperliquid book history is short (since Dec 2025) | Q4 has wide error bars | Report the uncertainty honestly; extend the analysis as history accumulates |
| Data licences restrict redistribution | Results not reproducible by others | Ship download scripts and checksums, not data |
| Scope creep into a general quant library | Nothing ships | Two cases only until both have verdicts |
| Compute cost of large Monte Carlo grids | Slow iteration | Vectorised simulation, fixed seeds, cached results; start with coarse grids |

## Deliverables, audience and business model

The open benchmark is the product people find; credibility is what it earns; paid work grows from that credibility.

**Deliverables:**

- **The repository:** generators, estimator registry, court, pipelines, and a one-command reproduction of every published figure.
- **A public leaderboard page:** each estimator's scores under each noise model, plus the current verdict per asset class.
- **Two arXiv papers:** the benchmark and roughness verdict first; the impact verdict second.
- **A plain-language explainer** for non-specialists, with interactive charts.

**Audience:**

- Researchers on both sides of each debate (they cite or contest it).
- Quant desks and execution teams (impact laws set trading costs).
- Students and practitioners learning stochastic volatility and microstructure.

**Business model (only after both verdicts ship):**

- Validation-as-a-service: run a firm's private estimator or execution-cost model through the court and certify it.
- Execution-cost models fitted on public crypto and prediction-market data, sold as a hosted API.
- Sponsorship from data providers and exchanges that benefit from rigorous use of their data.
- Consulting and teaching built on the published work.

## Open decisions

- [ ] Confirm the name "Exponent" (check for clashes on GitHub and PyPI).
- [ ] Licence: MIT for code is the default; decide whether results and figures are CC BY.
- [ ] Run the outstanding literature check on Q5 (square-root law on Polymarket) before committing to it.
- [ ] Choose the equity-index data source and confirm what intraday data is free.
- [ ] Confirm Binance's terms for research use of its public trade files.
- [ ] Decide whether to approach researchers from each camp for review at Milestone 2 or wait for Milestone 3.
- [ ] Compute budget: local machine only, or a capped cloud spend for large grids.
