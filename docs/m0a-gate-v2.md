# M0a gate, version 2 — registered 2026-10-05, after the v1 results

**Flagged: post-data registration.** Version 1 ([`m0a-gate.md`](m0a-gate.md)) ran and failed on R1 and R2b ([`m0a-results.md`](m0a-results.md)). This file changes those two items, with the user's approval, and says exactly what changed and why. The v1 verdict stands in the record. R2a and R3 passed under v1 and are not re-run. M1 is on hold until R1 v2 and R2b v2 both pass.

## R1 v2 — oracle on exact fractional log-vol

**What changed:** the truth's mean-reversion term is removed (α = 0, so log-vol is ν·fBM). The tolerance now adds Monte Carlo error to the original allowance for estimator bias. The replications rise to 1 000, under a fresh experiment key (`m0a-r1-v2`).

**Why:** R1 checks the estimator, not the RFSV model. v1's diagnostic showed the H = 0.7 miss came mostly from mean reversion at the regression's long lags; with α = 0 the bias on 200 diagnostic paths was −0.009. That diagnostic is the only look taken at α = 0, and it used a different seed key.

- **Truth:** X = 0.3·B^H on a unit grid, n = 4 000, H ∈ {0.05, 0.1, 0.2, 0.3, 0.5, 0.7}.
- **Estimator:** structure-function regression, lags {8, 13, 21, 34, 55, 89}, q ∈ {0.5, 1, 1.5, 2, 3}.
- **Pass:** |mean Ĥ − H| ≤ 0.02 + 3·SE at every H, where SE = sd/√1000. The 0.02 is v1's allowance for finite-sample estimator bias; 3·SE allows for the Monte Carlo error in measuring that bias.
- **Reported, not gating:** the RFSV bias with α = 5·10⁻⁴, from the v1 run. It is a property of the estimator on GJR's own model, and later work must state it rather than hide it.

## R2b v2 — reverse-engineering Cont & Das's realised-vol construction

The paper does not specify how its realised-vol (RV) series was built, and the authors are not being asked. The construction is therefore inferred under a protocol that keeps the inference honest.

### A finding that changes the target

Section 4.2's table and Table 3 report the same model: Brownian OU volatility, γ = θ = σ₀ = 1, L = 300×300, K = 300.
- The 4.2 row at H = 0.5 (one path) gives Ĥ(σ) = **0.507**, consistent with our 0.499.
- Table 3 (2 500 paths) gives a *minimum* of **0.528** and a mean of 0.557.

A single path from the 4.2 construction falling below the minimum of 2 500 Table 3 paths means **the two tables' σ series cannot have been built the same way**. Table 3's σ figure is therefore dropped from the gate (flagged change) and reported only. Their RV figures agree (Table 3 mean 0.137, 4.2 at H = 0.5 = 0.130), so RV is the target.

### Protocol

1. **Exploration, on one target only:** Table 3's Ĥ(RV), mean 0.137, interquartile range 0.128–0.148, for OU-SV. Any construction may be tried. **Every candidate tried is logged** with its result in [`r2b-exploration.md`](r2b-exploration.md), including the failures.
2. **Lock:** choose one construction whose mean Ĥ(RV) on OU-SV lies in [0.128, 0.148]. It must be a single rule — grid sizes, horizon, window, sampling, and the series the estimator is applied to — that is then applied unchanged to every model below. It is committed before step 3 runs.
3. **Held-out validation, run once:**
   - **V1, fractional OU (paper §4.2, Example 7):** H ∈ {0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8}; the paper's single-path values for Ĥ(σ) and Ĥ(RV), 14 numbers. H = 0.5 is excluded because it is the training model.

     | H | 0.1 | 0.2 | 0.3 | 0.4 | 0.6 | 0.7 | 0.8 |
     | --- | --- | --- | --- | --- | --- | --- | --- |
     | σ | 0.130 | 0.215 | 0.310 | 0.413 | 0.601 | 0.678 | 0.756 |
     | RV | 0.190 | 0.250 | 0.258 | 0.207 | 0.087 | 0.061 | 0.052 |
   - **V2, Brownian-modulus volatility (Example 5, σ = |W|):** K = 500, L = 500×500, single-path values Ĥ(RV) = 0.27 and Ĥ(σ) = 0.49.
   - **Rule:** our mean over 100 paths (the paper's §4.2 count) must be within max(0.03, 3·sd) of the paper's single-path value, where sd is our single-path spread. This must hold for all 16 numbers. Because the paper's values are single paths, the tolerance is set by single-path spread, not by the standard error of a mean.
4. **R2b v2 passes** if step 2 finds a construction and step 3 passes. If no construction matches Table 3, or validation fails, R2b v2 fails and is reported. M1 stays on hold and we decide what next.
