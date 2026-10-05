# R2b v2 exploration log

Every construction tried against the single training target (Cont & Das Table 3: mean Ĥ(RV) = 0.137, interquartile range 0.128–0.148, on OU-SV), in the order tried. The protocol is in [`m0a-gate-v2.md`](m0a-gate-v2.md). Nothing is deleted from this log.

| # | Construction | Paths | Mean Ĥ(RV) | sd | In range? | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A: rolling 300-return RV at every point of a 90 000-step price path; T = 1 | 200 | 0.548 | 0.008 | no | from the v1 run |
| 2 | B: non-overlapping 300-return blocks on a 27 000 000-step path (90 000 RV values); T = 1 | 200 | 0.065 | 0.017 | no | from the v1 run |
| 3 | E3: rolling 300-return RV sampled every 3 steps | 40 | 0.454 | 0.008 | no | |
| 4 | E3: … every 10 steps | 40 | 0.353 | 0.010 | no | |
| 5 | E3: … every 30 steps | 40 | 0.259 | 0.009 | no | |
| 6 | E3: … every 100 steps | 40 | 0.157 | 0.009 | no | |
| 7 | E5: non-overlapping 300-blocks, horizon T = 10 | 40 | 0.203 | 0.009 | no | |
| 8 | E5: … T = 100 | 40 | 0.362 | 0.009 | no | |
| 9 | E4: non-overlapping 1 000-return blocks, T = 1 | 40 | 0.130 | 0.013 | **yes** | |
| 10 | E4: non-overlapping 3 000-return blocks, T = 1 | — | — | — | not run | out of memory (270 million steps × 4 workers) |
| 11 | E5b: 300-blocks, T = 2 | 40 | 0.098 | 0.013 | no | |
| 12 | E5b: 300-blocks, T = 3 | 40 | 0.120 | 0.012 | no | |
| 13 | E5b: 300-blocks, T = 4 | 40 | 0.142 | 0.012 | **yes** | |
| 14 | E5b: 300-blocks, T = 5 | 40 | 0.152 | 0.010 | no | |
| 15 | **Locked** (= #13), confirmation run on the domain simulator | 200 | **0.140** | 0.011 | **yes** | interquartile range 0.133–0.148 (paper 0.128–0.148); Ĥ(σ) 0.499 |

## Why this construction was locked

Each family has a continuous knob that controls how strongly realised-vol noise dominates volatility's own movement, so almost any family can be tuned to 0.137. The choice between families was therefore made on the paper's text, before seeing the in-range results of #9 and #13:

- **Rolling windows (E3) are rejected.** They make the realised-vol error strongly autocorrelated, but the paper says the log error is i.i.d. for this model (§4.1, Fig. 12).
- **Separate blocks of 300 returns are kept.** The paper states the window ("300 consecutive data-points"), so the block size is not a free parameter.
- **The horizon T is the free parameter.** It is the one quantity the paper never states for Examples 5–7 (§2.4's [0, 1] refers to the fBM study). It was read off the coarse grid at T = 4 and not refined further, to limit fitting.

Candidate #9 (1 000-return blocks, T = 1) is the same signal-to-noise trade-off reached through the window instead of the horizon. It is rejected because it contradicts the stated window.

## Locked construction (applied unchanged in validation)

| Component | Setting |
| --- | --- |
| Price grid | L × 300 fine steps on [0, T], with T = 4 and L = K² |
| Realised vol | one value per non-overlapping block of 300 fine log-returns, √(Σ r²) |
| σ series | σ at the L + 1 block boundaries |
| Estimator | normalised p-variation, K as stated per example (300 for Example 7, 500 for Example 5) |
| Models | the paper's (γ = θ = σ₀ = 1), with time running over [0, 4] |

## Validation attempts

| Attempt | Code | Outcome |
| --- | --- | --- |
| 1 | `bcb645f` | **Crashed before producing any numbers.** fGn's autocovariance lost all precision to cancellation at 27 million steps, which made the circulant embedding numerically indefinite at H = 0.8 (532 341 negative eigenvalues). Fixed with the exact large-lag series, and a regression test was added. No validation output was seen. The locked construction is unchanged. |
