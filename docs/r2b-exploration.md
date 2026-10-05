# R2b v2 exploration log

Every construction tried against the single training target (Cont & Das Table 3: mean Ĥ(RV) = 0.137, interquartile range 0.128–0.148, on OU-SV), in the order tried. The protocol is in [`m0a-gate-v2.md`](m0a-gate-v2.md). Nothing is deleted from this log.

| # | Construction | Paths | Mean Ĥ(RV) | sd | In range? | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A: rolling 300-return RV at every point of a 90 000-step price path; T = 1 | 200 | 0.548 | 0.008 | no | from the v1 run |
| 2 | B: non-overlapping 300-return blocks on a 27 000 000-step path (90 000 RV values); T = 1 | 200 | 0.065 | 0.017 | no | from the v1 run |
