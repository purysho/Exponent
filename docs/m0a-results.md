# M0a results — 2026-10-05

## Current verdict: **M0a passes under gate v2**. Gate v1 failed, and that stays on record.

| Item | v1 ([`m0a-gate.md`](m0a-gate.md)) | v2 ([`m0a-gate-v2.md`](m0a-gate-v2.md), post-data, flagged) |
| --- | --- | --- |
| R1 oracle | **FAIL** — −0.027 at H = 0.7 | **PASS** — α = 0, max \|bias\| 0.011 against a tolerance of 0.024 |
| R2a Cont–Das Table 1 | PASS | (not re-run; passed in v1) |
| R2b Cont–Das Table 3 | **FAIL** — neither declared reading | **PASS** — inferred construction validated on 16 held-out numbers |
| R3 Lumor map | PASS | (not re-run; passed in v1) |

**How v1 became v2:**
- After v1 failed, the user approved two changes:
  - a corrected R1;
  - reverse-engineering Cont and Das's unstated realised-vol construction, instead of asking them.
- Both were registered in a dated, flagged file before running.
- For R2b, every candidate construction tried is logged in [`r2b-exploration.md`](r2b-exploration.md). One was locked on the Table 3 training number, and the lock was committed before the held-out validation ran.
- Validation attempt 1 crashed on a numerical bug in our fGn generator before producing any numbers (logged; fixed in `16d6535`). Attempt 2 is the result below.

**Reproduce:**
- `uv run exponent m0a` (v1, about 9 minutes on 4 cores).
- `--only r1v2` and `--only r2bv2` (v2; about 35 minutes, dominated by 27-million-step fractional-OU paths).
- Outputs: [`results/m0a/`](../results/m0a/). Seeds are fixed, and re-runs from clean commits have matched number for number.

## R2b v2 — held-out validation (code `16d6535`; report stamped `e8ea024`, where `src/` is identical)

Locked construction: non-overlapping 300-return blocks over horizon T = 4. Normalised p-variation; 100 paths per cell. The paper's values are single paths, so the tolerance is max(0.03, 3 × single-path sd).

| Model | Series | H | Paper | Ours | Tolerance |
| --- | --- | --- | --- | --- | --- |
| fOU | RV | 0.1 / 0.2 / 0.3 / 0.4 | 0.190 / 0.250 / 0.258 / 0.207 | 0.179 / 0.237 / 0.243 / 0.198 | 0.052 / 0.033 / 0.030 / 0.030 |
| fOU | RV | 0.6 / 0.7 / 0.8 | 0.087 / 0.061 / 0.052 | 0.092 / 0.052 / 0.032 | 0.051 / 0.055 / 0.045 |
| fOU | σ | 0.1 / 0.2 / 0.3 / 0.4 | 0.130 / 0.215 / 0.310 / 0.413 | 0.085 / 0.189 / 0.296 / 0.399 | 0.066 / 0.043 / 0.030 / 0.030 |
| fOU | σ | 0.6 / 0.7 / 0.8 | 0.601 / 0.678 / 0.756 | 0.597 / 0.692 / 0.783 | 0.030 each |
| \|W\| (Example 5) | RV / σ | — | 0.27 / 0.49 | 0.275 / 0.497 | 0.113 / 0.030 |

**All 16 pass.** The construction reproduces the paper's central picture: realised vol's apparent roughness peaks around 0.24 when true H is about 0.3, then *falls* as true volatility gets smoother, reaching 0.03 at H = 0.8. A smooth truth reads as rough.

**What the pass does not show:**
- **Wide margins on some entries.** Several entries pass because single-path spread makes the tolerance wide: the |W| RV tolerance is 0.11, and fOU σ at H = 0.1 is off by 0.045 against a tolerance of 0.066.
- **Our fOU RV runs slightly low:** 6 of 7 entries fall below the paper, by 0.01–0.02.
- **What the evidence supports:** the inferred construction is consistent with the paper on 16 numbers it was not tuned on. That is not proof it is identical to what Cont and Das did.
- **Table 3's instantaneous-vol figure (0.557)** remains unexplained. The paper's own numbers make it inconsistent with §4.2.

## v1 detail: R1 failed on the smooth control, H = 0.7

| True H | 0.05 | 0.1 | 0.2 | 0.3 | 0.5 | 0.7 |
| --- | --- | --- | --- | --- | --- | --- |
| Mean Ĥ | 0.051 | 0.098 | 0.195 | 0.297 | 0.490 | **0.673** |
| Bias | +0.001 | −0.002 | −0.005 | −0.003 | −0.010 | **−0.027** |

**Diagnosis** (a diagnostic run, not a re-run of the gate): with the mean-reversion term switched off (α = 0), the H = 0.7 bias falls from −0.022 to −0.009 (standard error 0.003) on 200 fresh paths. The failure therefore comes mostly from the truth I chose: RFSV's mean reversion damps increments at the long lags (up to 89) used by the regression, and that matters more the smoother the path. A small remaining finite-sample bias at high H is genuine.

**Consequence:** the structure-function estimator is sound across the rough range where the debate sits. The registered tolerance was too tight for the smooth controls given this truth. A corrected R1 (α = 0 or lags matched to α, with a tolerance derived from Monte Carlo error) must be registered as a new, dated version. The proposed fix is in "Decisions needed" below.

## v1 detail: R2b, Cont & Das Table 3 not reproduced

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

## R3 — Lumor's identifiability map reproduced (v1, unchanged)

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

## Decisions taken

- **R1 v2:** registered and passed.
- **Cont & Das not contacted:** the construction was reverse-engineered and validated instead, so the draft note above is unused.
- **M1:** held until both failures were closed. They now are.
