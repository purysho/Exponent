# Review of draft 1 (2026-10-05)

What was wrong with draft 1 of the proposal, what changed in [`proposal.md`](proposal.md), and what remains unverified. Ordered by how much each problem would hurt in front of a referee.

## 1. The central gap claim was no longer true

Draft 1: *"nobody has checked whether the estimators can be trusted."*

- **Lumor, SSRN 7346318 (posted 26 Aug 2026)**, *When is Volatility Roughness Identifiable? A Simulation-Grounded Audit of Hurst Estimation From Realised Variance*, does exactly this for three estimators. It uses rough-Bergomi ground truth and a smooth semimartingale null, maps identifiability over vol-of-vol and sampling window, calibrates to BTC, ETH and the S&P 500, finds nothing identified at daily RV, and releases open code. That covers much of draft 1's Q1 and the daily side of Q2.
- Noise-robust estimators (Fukasawa–Takabatake–Westphal; Bolko–Christensen–Pakkanen–Veliyev) were each validated by simulation, and both still find roughness. Draft 1 did not mention them. They are the rough camp's best evidence, and leaving them out would read as choosing sides.
- Angelini's *Critical review of Hurst exponent estimation* (Annali MEMOTEF) already organises estimator biases into one framework.

**Change:** repositioned. The gap is a *standing, shared* court with common truths, noise and scoring, plus the impact side, where nobody has validated metaorder reconstruction against real labels. Lumor is cited, will be reproduced in M0a, and the roughness half is explicitly described as partly scooped.

## 2. Two citations said something their papers do not

- **arXiv:2507.00575 (Bitcoin).** Draft 1: "roughness estimation fails outright." The paper finds a unique p-variation root in about 90% of configurations, with low estimates (0.054–0.086), and says the estimate is "not invariant to time or measurement design." That is sensitivity, not failure. Corrected.
- **arXiv:2606.25771.** Draft 1: "frames it as an unsolved statistical problem." It is a new estimator (pointwise, noise-robust H(t)). Reframed as a candidate for the court.
- **arXiv:2606.15715 (Hyperliquid).** Roughly right, but it is a sunshine-trading paper by Barone and Lillo, and the impact-shape result is secondary. The finding is that hidden metaorder impact is "strongly curved and saturating", not just "below ½". That matters because a saturating curve fitted with a power law will report a low exponent, so functional form is now part of the question (I2).
- **Quantitative Finance 2026 (10.1080/14697688.2026.2615106)** is Maitrier–Loeper–Kanazawa–Bouchaud arguing for a *mechanical* origin. "Origin unsettled" was fair, but the citation backs one side, so the text now says which.

## 3. The best idea in reach was missing

Hyperliquid's native TWAP orders are **metaorders whose parent is known**. Hide the labels, run any reconstruction heuristic, and you can score it against real ground truth, which no other venue allows. This turns Q4 from "re-measure with another method" into a real-data court for the impact track. It is now the core of I1.

Caveat, stated in the proposal: TWAPs are visible, so they validate reconstruction and fitting bias, not the impact law of hidden orders.

## 4. Research-question design

- **Q1's grid stopped at H = 0.5.** Cont and Das's claim is that *smooth* volatility looks rough, so the smooth side needs H > 0.5 and a semimartingale null. Added.
- **Q1 as pass/fail → identifiability map.** "Can an estimator tell 0.1 from 0.5" depends on vol-of-vol, sampling frequency, noise and sample length. A map over those, with each dataset placed on it by calibration, answers the question that actually matters.
- **Q2 staked a directional hypothesis ("differs by asset class") with no prior for it**, and counted a uniform answer as a loss. A uniform answer is a perfectly good result. Replaced with a symmetric decision rule (rough / smooth / undecidable).
- **Q3 omitted HAR-RV**, the standard realised-vol forecasting baseline; a referee would ask for it first. "Differ measurably beyond tolerance" is replaced by the Model Confidence Set. It also now says plainly that forecasting wins show usefulness, not truth.
- **Q5's interesting angle was buried.** Known outcomes let you split metaorders into ones that turned out right and ones that turned out wrong. That directly tests mechanical vs informational impact, which is the third bullet of Debate 2. Promoted to the question itself (I3), and measured in log-odds.
- **"Q1 gates everything" was wrong.** Roughness estimators have nothing to do with impact estimators. The work is now two independent tracks, each with its own gate.

## 5. Methodology gaps

- **"Passes only if it meets thresholds across *all* noise models"** lets the most extreme noise setting veto everything. Now: pass within the band calibrated from each real dataset, and report sensitivity outside it.
- **Coverage of "stated confidence intervals"**: most of these estimators publish no interval. The court now supplies a uniform bootstrap interval and scores native intervals separately.
- **Overfitting the court itself**: tuning an estimator on the same grid that scores it is backtest overfitting one level up. Added a development/test grid split.
- **Non-answers**: p-variation can have no root and inversions can go out of range (both Lumor and Pontiggia report this). These are now recorded outcomes, not NaNs that get dropped.
- **Pre-registration by git timestamp proves nothing**, because commit dates are set by the author. Registrations are now GitHub releases archived to Zenodo (external timestamp + DOI).
- **A 20% time holdout on about 15 months of Hyperliquid** leaves very little. Track I also holds out whole markets.
- **Multiplicity**: many estimators × classes × frequencies. Now controlled and stated.

## 6. Data facts

- **Hyperliquid book history** does not start on Dec 15, 2025. That date was Barone and Lillo's own download. The official archive has L2 snapshots back to 2023 but is **requester-pays** and warns "data may be missing", so "all data is free" was not quite true. Fills with addresses go back to 2025-03.
- **Equity data**: the Oxford-Man Realized Library, the traditional free source, is discontinued. Equity verdicts are likely daily-only, which is exactly where Lumor finds non-identification. The proposal now says so up front.
- **Implied-vol inputs** for the path-dependent model were unnamed. Added CBOE VIX and Deribit DVOL.

## 7. Smaller points

- The two embedded diagrams (data flow, milestones) did not survive export to Markdown. Both are rebuilt as text and Mermaid in `architecture.md` and `build-plan.md`.
- PyPI `exponent` is taken (an unrelated, dormant package). Proposed distribution name: `exponent-court`.
- Exchange sponsorship conflicts with a product whose value is neutrality, so it is flagged.
- Technology: DuckDB dropped (Polars covers it), and Numba deferred until profiling asks for it. Fewer dependencies, same capability.

## Citation status

Checked by fetching on 2026-10-05: arXiv 2203.13820, 2507.00575, 2606.04217, 2606.15715, 2606.25771; SSRN 7346318; QF 10.1080/14697688.2026.2615106; Hyperliquid historical-data docs.

From memory, **still to verify before anything is published**: Fukasawa–Takabatake–Westphal (quasi-likelihood, *Mathematical Finance* 2022); Bolko–Christensen–Pakkanen–Veliyev (GMM, *J. Econometrics* 2023); Zarinelli et al. 2015 (logarithmic impact); Patton 2011 (QLIKE robustness); Hansen–Lunde–Nason (Model Confidence Set); Oxford-Man library discontinuation date; whether public Hyperliquid fills carry a TWAP id (checked in M0b); Physics 2025 (TSE) and SSRN 4174589, which were not re-fetched.
