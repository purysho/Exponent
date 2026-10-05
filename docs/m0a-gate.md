# M0a gate — stated before the full runs

Committed before any full-size M0a run, so the pass criteria cannot drift towards the results. Results go in [`m0a-results.md`](m0a-results.md). The git timestamp is author-controlled; external timestamping (Zenodo) starts at M1, when real data first enters. That rule was set in the proposal, and M0a is synthetic only.

**Already seen before writing this file (disclosed):**
- A 50-path check of R2a, which passed at every H.
- One path of R2b reading A, giving Ĥ(RV) = 0.527 and Ĥ(σ) = 0.491.
- One rough-Bergomi path at H = 0.1, η = 1.5, Δ = 288, used for timing.

No other output has been looked at.

## R1 — oracle: structure-function regression on exact fractional log-vol

This is not a reproduction of a published number. It checks that our GJR estimator and our fractional generator agree with each other on their home ground.

- **Truth:** RFSV log-volatility (fractional OU, Euler on exact fGn), ν = 0.3, α = 5·10⁻⁴, dt = 1, n = 4 000, H ∈ {0.05, 0.1, 0.2, 0.3, 0.5, 0.7}. 200 replications.
- **Observation:** spot log-vol (the oracle).
- **Estimator:** structure-function regression, lags {8, 13, 21, 34, 55, 89}, q ∈ {0.5, 1, 1.5, 2, 3}.
- **Pass:** |mean Ĥ − H| ≤ 0.02 at every H.

## R2a — Cont & Das (2024), Table 1: normalised p-variation on fBM

- **Truth:** fBM on [0, 1]; L = 300 × 300 = 90 000 steps, K = 300. H ∈ {0.1, 0.3, 0.5, 0.8}, 150 replications (as in the paper).
- **Pass:** our mean Ĥ lies inside the paper's interquartile range at every H: [0.0920, 0.1100], [0.2940, 0.3020], [0.4940, 0.5020], [0.7820, 0.7940].

## R2b — Cont & Das (2024), Table 3: OU-SV, realised vs instantaneous volatility

- **Truth:** σ = σ₀e^Y, dY = −γY dt + θ dB′, σ₀ = γ = θ = 1, T = 1.
- **Estimator:** normalised p-variation with K = 300.
- **Replications:** 200 per reading (the paper used 2 500).

The paper does not pin down how realised volatility is built, so two readings are declared now and both are run:

| Reading | Price grid | Realised vol | σ series |
| --- | --- | --- | --- |
| **A — rolling** | 90 000 steps | √(sum of the last 300 squared returns) at every point ("5-minute moving window", §4.1); 89 700 values | σ at all 90 001 grid points |
| **B — blocks** | 300 × 90 000 = 27 million steps | one value per non-overlapping block of 300 returns; 90 000 values. Consistent with the paper's statement that the log error is i.i.d. | σ at the 90 001 block ends |

- **Pass:** under A or B, mean Ĥ(RV) ∈ [0.128, 0.148] **and** mean Ĥ(σ) ∈ [0.552, 0.563] (the paper's interquartile ranges; paper means 0.137 and 0.557). Matching only one of the two counts as partial, which is a fail.
- **Post hoc, not able to pass the gate:** reading **C**, which is B's realised vol paired with σ averaged over each block. It is included because a positive bias in Ĥ(σ) would be explained by an averaged "instantaneous" series. It is labelled as a guess and reported, but cannot rescue a fail.

## R3 — Lumor (2026), identifiability map

- **Truth:** rough Bergomi via the κ = 0 hybrid scheme, ρ = −0.7, ξ₀ = 0.04, T = 1, n = 2 500 · Δ fine steps.
- **Grid:** η ∈ {0.5, 1.5, 2.5, 3.5}; Δ ∈ {48, 96, 288}; true H ∈ {0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60}. 40 replications per cell, giving 84 cells per estimator.
- **Observation:** block log-RV, 2 500 values.
- **Estimators (gating):** structure-function regression; Lumor's p-variation scaling crossing; MF-DFA.
- **Not gating (our addition):** Cont–Das normalised p-variation on the same map.
- **Classification:** Lumor's rules (monotonicity tolerance 0.012, flat-slope floor 0.25, z = 1.96, smooth boundary H = ½).

| Estimator | Lumor's logged status fractions (roughvollab ROADMAP, L1c-MAP-runs) |
| --- | --- |
| structure-function | identified 12%, non-identified 85%, de-biasable 4% |
| MF-DFA | identified 30%, non-identified 61%, de-biasable 10% |
| scaling crossing | non-identified 92%, uncalibrated 8% (identified 0%, de-biasable 0%) |

**Pass:** for each gating estimator, every status fraction is within ±10 percentage points of Lumor's, **and** MF-DFA has the largest identified fraction of the three.

## M0a passes if R1, R2a, R2b and R3 all pass

If R2a passes but R2b fails under both declared readings, the estimator is correct and the gap lies in an unspecified construction. We report it, ask the authors, and do not use either reading as "Cont–Das's" in later work until it is resolved.
