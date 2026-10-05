# M0a gate results (code d6fdec6)

## R1 oracle (structure-function): FAIL

```
shape: (6, 12)
┌──────┬──────────────┬────────────────────┬─────┬──────┬──────────┬──────────┬──────────┬──────────┬──────┬───────────┬───────┐
│ cell ┆ observation  ┆ estimator          ┆ n   ┆ n_ok ┆ mean     ┆ sd       ┆ q25      ┆ q75      ┆ H    ┆ bias      ┆ pass_ │
│ ---  ┆ ---          ┆ ---                ┆ --- ┆ ---  ┆ ---      ┆ ---      ┆ ---      ┆ ---      ┆ ---  ┆ ---       ┆ ---   │
│ i64  ┆ str          ┆ str                ┆ u32 ┆ u32  ┆ f64      ┆ f64      ┆ f64      ┆ f64      ┆ f64  ┆ f64       ┆ bool  │
╞══════╪══════════════╪════════════════════╪═════╪══════╪══════════╪══════════╪══════════╪══════════╪══════╪═══════════╪═══════╡
│ 0    ┆ spot_log_vol ┆ structure-function ┆ 200 ┆ 200  ┆ 0.050858 ┆ 0.0089   ┆ 0.043934 ┆ 0.058032 ┆ 0.05 ┆ 0.000858  ┆ true  │
│ 1    ┆ spot_log_vol ┆ structure-function ┆ 200 ┆ 200  ┆ 0.098133 ┆ 0.014343 ┆ 0.088186 ┆ 0.107905 ┆ 0.1  ┆ -0.001867 ┆ true  │
│ 2    ┆ spot_log_vol ┆ structure-function ┆ 200 ┆ 200  ┆ 0.194566 ┆ 0.021654 ┆ 0.18036  ┆ 0.208769 ┆ 0.2  ┆ -0.005434 ┆ true  │
│ 3    ┆ spot_log_vol ┆ structure-function ┆ 200 ┆ 200  ┆ 0.296751 ┆ 0.028621 ┆ 0.279846 ┆ 0.314034 ┆ 0.3  ┆ -0.003249 ┆ true  │
│ 4    ┆ spot_log_vol ┆ structure-function ┆ 200 ┆ 200  ┆ 0.489696 ┆ 0.03612  ┆ 0.462339 ┆ 0.512099 ┆ 0.5  ┆ -0.010304 ┆ true  │
│ 5    ┆ spot_log_vol ┆ structure-function ┆ 200 ┆ 200  ┆ 0.673256 ┆ 0.035877 ┆ 0.650394 ┆ 0.694571 ┆ 0.7  ┆ -0.026744 ┆ false │
└──────┴──────────────┴────────────────────┴─────┴──────┴──────────┴──────────┴──────────┴──────────┴──────┴───────────┴───────┘
```

## R2a Cont–Das Table 1 (fBM): PASS

```
shape: (4, 14)
┌──────┬─────────────┬───────────────────────┬─────┬──────┬──────────┬──────────┬──────────┬──────────┬─────┬────────────┬───────────┬───────────┬───────┐
│ cell ┆ observation ┆ estimator             ┆ n   ┆ n_ok ┆ mean     ┆ sd       ┆ q25      ┆ q75      ┆ H   ┆ paper_mean ┆ paper_q25 ┆ paper_q75 ┆ pass_ │
│ ---  ┆ ---         ┆ ---                   ┆ --- ┆ ---  ┆ ---      ┆ ---      ┆ ---      ┆ ---      ┆ --- ┆ ---        ┆ ---       ┆ ---       ┆ ---   │
│ i64  ┆ str         ┆ str                   ┆ u32 ┆ u32  ┆ f64      ┆ f64      ┆ f64      ┆ f64      ┆ f64 ┆ f64        ┆ f64       ┆ f64       ┆ bool  │
╞══════╪═════════════╪═══════════════════════╪═════╪══════╪══════════╪══════════╪══════════╪══════════╪═════╪════════════╪═══════════╪═══════════╪═══════╡
│ 0    ┆ fbm         ┆ normalized-pvariation ┆ 150 ┆ 150  ┆ 0.103008 ┆ 0.012952 ┆ 0.093452 ┆ 0.112227 ┆ 0.1 ┆ 0.1009     ┆ 0.092     ┆ 0.11      ┆ true  │
│ 1    ┆ fbm         ┆ normalized-pvariation ┆ 150 ┆ 150  ┆ 0.300279 ┆ 0.007539 ┆ 0.295454 ┆ 0.305586 ┆ 0.3 ┆ 0.2976     ┆ 0.294     ┆ 0.302     ┆ true  │
│ 2    ┆ fbm         ┆ normalized-pvariation ┆ 150 ┆ 150  ┆ 0.500142 ┆ 0.006394 ┆ 0.496058 ┆ 0.504862 ┆ 0.5 ┆ 0.4978     ┆ 0.494     ┆ 0.502     ┆ true  │
│ 3    ┆ fbm         ┆ normalized-pvariation ┆ 150 ┆ 150  ┆ 0.790879 ┆ 0.013519 ┆ 0.780956 ┆ 0.799865 ┆ 0.8 ┆ 0.7891     ┆ 0.782     ┆ 0.794     ┆ true  │
└──────┴─────────────┴───────────────────────┴─────┴──────┴──────────┴──────────┴──────────┴──────────┴─────┴────────────┴───────────┴───────────┴───────┘
```

## R2b Cont–Das Table 3 (OU-SV): FAIL

```
shape: (5, 9)
┌──────┬──────────────┬───────────────────────┬─────┬──────┬──────────┬──────────┬──────────┬──────────┐
│ cell ┆ observation  ┆ estimator             ┆ n   ┆ n_ok ┆ mean     ┆ sd       ┆ q25      ┆ q75      │
│ ---  ┆ ---          ┆ ---                   ┆ --- ┆ ---  ┆ ---      ┆ ---      ┆ ---      ┆ ---      │
│ i64  ┆ str          ┆ str                   ┆ u32 ┆ u32  ┆ f64      ┆ f64      ┆ f64      ┆ f64      │
╞══════╪══════════════╪═══════════════════════╪═════╪══════╪══════════╪══════════╪══════════╪══════════╡
│ 0    ┆ A:rv         ┆ normalized-pvariation ┆ 200 ┆ 200  ┆ 0.548124 ┆ 0.007744 ┆ 0.541916 ┆ 0.553595 │
│ 0    ┆ A:sigma      ┆ normalized-pvariation ┆ 200 ┆ 200  ┆ 0.499521 ┆ 0.007254 ┆ 0.495526 ┆ 0.503752 │
│ 0    ┆ B:rv         ┆ normalized-pvariation ┆ 200 ┆ 200  ┆ 0.065087 ┆ 0.016963 ┆ 0.055499 ┆ 0.07709  │
│ 0    ┆ B:sigma      ┆ normalized-pvariation ┆ 200 ┆ 200  ┆ 0.498912 ┆ 0.007744 ┆ 0.493685 ┆ 0.503904 │
│ 0    ┆ C:sigma_mean ┆ normalized-pvariation ┆ 200 ┆ 200  ┆ 0.534497 ┆ 0.00726  ┆ 0.530264 ┆ 0.539488 │
└──────┴──────────────┴───────────────────────┴─────┴──────┴──────────┴──────────┴──────────┴──────────┘
```
- reading A: Ĥ(RV) mean 0.5481242696103217, Ĥ(σ) mean 0.49952094645347955 -> no match
- reading B: Ĥ(RV) mean 0.06508691239973258, Ĥ(σ) mean 0.4989115134775336 -> no match
- reading C (post hoc, cannot pass): Ĥ(RV) 0.06508691239973258, Ĥ(block-mean σ) 0.5344973820906567

## R3 Lumor identifiability map: PASS

```
shape: (16, 5)
┌─────────────────────────────┬────────────────┬──────────┬───────┬─────────────┐
│ estimator                   ┆ status         ┆ ours     ┆ lumor ┆ within_10pp │
│ ---                         ┆ ---            ┆ ---      ┆ ---   ┆ ---         │
│ str                         ┆ str            ┆ f64      ┆ f64   ┆ bool        │
╞═════════════════════════════╪════════════════╪══════════╪═══════╪═════════════╡
│ structure-function          ┆ identified     ┆ 0.119048 ┆ 0.12  ┆ true        │
│ structure-function          ┆ de-biasable    ┆ 0.02381  ┆ 0.04  ┆ true        │
│ structure-function          ┆ non-identified ┆ 0.857143 ┆ 0.85  ┆ true        │
│ structure-function          ┆ uncalibrated   ┆ 0.0      ┆ 0.0   ┆ true        │
│ pvariation-scaling-crossing ┆ identified     ┆ 0.0      ┆ 0.0   ┆ true        │
│ pvariation-scaling-crossing ┆ de-biasable    ┆ 0.0      ┆ 0.0   ┆ true        │
│ pvariation-scaling-crossing ┆ non-identified ┆ 0.928571 ┆ 0.92  ┆ true        │
│ pvariation-scaling-crossing ┆ uncalibrated   ┆ 0.071429 ┆ 0.08  ┆ true        │
│ mfdfa                       ┆ identified     ┆ 0.27381  ┆ 0.3   ┆ true        │
│ mfdfa                       ┆ de-biasable    ┆ 0.119048 ┆ 0.1   ┆ true        │
│ mfdfa                       ┆ non-identified ┆ 0.607143 ┆ 0.61  ┆ true        │
│ mfdfa                       ┆ uncalibrated   ┆ 0.0      ┆ 0.0   ┆ true        │
│ normalized-pvariation       ┆ identified     ┆ 0.0      ┆ null  ┆ null        │
│ normalized-pvariation       ┆ de-biasable    ┆ 0.02381  ┆ null  ┆ null        │
│ normalized-pvariation       ┆ non-identified ┆ 0.97619  ┆ null  ┆ null        │
│ normalized-pvariation       ┆ uncalibrated   ┆ 0.0      ┆ null  ┆ null        │
└─────────────────────────────┴────────────────┴──────────┴───────┴─────────────┘
```
- MF-DFA has the largest identified fraction of the gating three: True
