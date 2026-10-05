# M0a results — 2026-10-05

Run against the criteria in [`m0a-gate.md`](m0a-gate.md) (committed in `d58964c`, before the runs). Code `d6fdec6`. Reproduce with `uv run exponent m0a` (about 9 minutes on 4 cores). The full output is in [`results/m0a/report.md`](../results/m0a/report.md). A second run from the clean commit matched the first number for number.

## Verdict: **the M0a gate fails as stated**

| Item | Result | In one line |
| --- | --- | --- |
| R1 oracle | **FAIL** | Unbiased on the rough range (\|bias\| ≤ 0.006 for H ≤ 0.3), but −0.027 at H = 0.7, outside the 0.02 tolerance |
| R2a Cont–Das Table 1 | PASS | All four means inside the paper's interquartile ranges |
| R2b Cont–Das Table 3 | **FAIL** | Not reproduced under either declared reading of how realised vol was built |
| R3 Lumor map | PASS | Every status fraction within 3 points of Lumor's; MF-DFA identifies most |

The harness reproduces the two results whose setup is fully specified: Cont–Das Table 1 and Lumor's map. Both failures are explained below. Neither explanation changes the verdict; changing a criterion after seeing results requires a new, dated registration.

## R1 — failed on the smooth control, H = 0.7

| True H | 0.05 | 0.1 | 0.2 | 0.3 | 0.5 | 0.7 |
| --- | --- | --- | --- | --- | --- | --- |
| Mean Ĥ | 0.051 | 0.098 | 0.195 | 0.297 | 0.490 | **0.673** |
| Bias | +0.001 | −0.002 | −0.005 | −0.003 | −0.010 | **−0.027** |

**Diagnosis** (a diagnostic run, not a re-run of the gate): with the mean-reversion term switched off (α = 0), the H = 0.7 bias falls from −0.022 to −0.009 (standard error 0.003) on 200 fresh paths. The failure therefore comes mostly from the truth I chose: RFSV's mean reversion damps increments at the long lags (up to 89) used by the regression, and that matters more the smoother the path. A small remaining finite-sample bias at high H is genuine.

**Consequence:** the structure-function estimator is sound across the rough range where the debate sits. The registered tolerance was too tight for the smooth controls given this truth. A corrected R1 (α = 0 or lags matched to α, with a tolerance derived from Monte Carlo error) must be registered as a new, dated version. The proposed fix is in "Decisions needed" below.

## R2b — Cont & Das Table 3 not reproduced

Normalised p-variation, K = 300, 200 paths per reading.

| Series | Ours | Paper (mean, interquartile range) |
| --- | --- | --- |
| Reading A, rolling RV (overlapping 300-step windows on 90 000 steps) | **0.548** | 0.137 (0.128–0.148) |
| Reading B, block RV (non-overlapping 300-step blocks on 27 million steps) | **0.065** | 0.137 |
| σ on the grid (both readings) | **0.499** | 0.557 (0.552–0.563) |
| Reading C, block-mean σ (post hoc, cannot pass) | 0.534 | 0.557 |

- **The estimator is not the problem.** R2a reproduces Table 1 with the same code, and our σ estimate (0.499) matches what Table 1 says the estimator gives on any H = ½ diffusion (0.498). The paper's 0.557 for σ implies its "instantaneous volatility" series was not the plain diffusion sampled on the grid. Averaging σ over blocks (reading C) moves it towards 0.557 but not into range.
- **The artefact depends on how realised vol is built.**
  - Rolling, overlapping windows (A) do **not** make realised vol look rough: 0.548, which is smoother than σ itself.
  - Non-overlapping blocks (B) make it look **much rougher** than the paper reports: 0.065.
  - The paper's qualitative claim — a smooth σ gives a rough-looking realised vol — holds under B, the reading consistent with its "i.i.d. log error" remark, but not under A.

  For the project this is a finding in itself. "The realised-vol proxy" is not one object, and the court must register proxy construction as a separate axis.
- **Action, as the gate file requires:** ask the authors for their construction (draft below). Until they answer, neither reading is labelled "Cont–Das's" in later work.

> *Draft to R. Cont and P. Das:* We are reproducing Table 3 of "Rough volatility: fact or artefact?" (OU-SV, L = 300×300, K = 300). Our normalised p-variation reproduces your Table 1 within its interquartile ranges, but for Table 3 we get Ĥ(σ) ≈ 0.499 rather than 0.557. Ĥ(RV) comes out at 0.548 with rolling 300-point windows and 0.065 with non-overlapping 300-point blocks, against your 0.137. Could you tell us how the realised-volatility and instantaneous-volatility series were sampled, or share the simulation code? Our code and results: [repository link].

## R3 — Lumor's identifiability map reproduced

84 cells per estimator: η ∈ {0.5, 1.5, 2.5, 3.5} × Δ ∈ {48, 96, 288} × 7 true H, 40 paths per cell.

| Estimator | Identified | Non-identified | De-biasable | Uncalibrated | Lumor (id / non-id / de-bias / uncal) |
| --- | --- | --- | --- | --- | --- |
| structure-function | 12% | 86% | 2% | 0% | 12 / 85 / 4 / 0 |
| MF-DFA | 27% | 61% | 12% | 0% | 30 / 61 / 10 / 0 |
| scaling crossing (Lumor's "Cont-Das") | 0% | 93% | 0% | 7% | 0 / 92 / 0 / 8 |
| *normalised p-variation (true Cont–Das; ours, not gating)* | *0%* | *98%* | *2%* | *0%* | — |

- Roughness is identified only at the finest sampling (Δ = 288, i.e. 5-minute RV) and high vol-of-vol (η ≥ 1.5 for MF-DFA, η ≥ 2.5 for structure-function), plus MF-DFA at η = 3.5 for every Δ.
- At η = 1.5 and Δ = 288, every bias curve is hump-shaped: the reading rises with true H and then falls. For example, the true Cont–Das estimator reads 0.20 at H = 0.05 but **0.13 at H = 0.6**. A smooth truth produces a reading at the empirical "rough" level of about 0.1–0.14. This is the fact-vs-artefact ambiguity, visible directly in our own harness.
- Addition beyond Lumor: Cont and Das's own estimator identifies roughness nowhere on this map from daily log-RV. Lumor's audit did not include it, because the estimator called "Cont-Das" there is a different statistic.

## Decisions needed (the gate is the user's call)

1. **R1:** register **R1 v2** — the same test with α = 0, plus a separate check of RFSV bias at the lags actually used — and re-run. It is flagged as a post-data change in any paper. Recommended.
2. **R2b:** send the draft to Cont and Das. Proceed to M1 without depending on their Table 3, since the proxy-construction finding stands either way. Recommended.
3. **Proceed to M1 now**, given that the only failures are an over-tight criterion and an underspecified external result? Or hold M1 until both are closed?
