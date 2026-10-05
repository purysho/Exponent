"""The estimator registry. The leaderboard key is (name, version).

A version changes whenever an estimator's output can change for the same
input, so that scores from different versions are never pooled.
"""

from __future__ import annotations

from exponent.domain.estimators.roughness.mfdfa import mfdfa
from exponent.domain.estimators.roughness.pvariation import cont_das, scaling_crossing
from exponent.domain.estimators.roughness.structure_function import gjr
from exponent.domain.types import Estimand, EstimatorSpec, SpotLogVol, SpotVol, VolProxy

_ANY_VOL = (SpotLogVol, SpotVol, VolProxy)

ROUGHNESS: dict[str, EstimatorSpec] = {
    s.name: s
    for s in (
        EstimatorSpec(
            name="structure-function",
            version="1",
            citation="Gatheral, Jaisson & Rosenbaum (2018), Quantitative Finance 18(6)",
            estimates=Estimand.H_LOG_VOL,
            consumes=_ANY_VOL,
            fn=gjr,
        ),
        EstimatorSpec(
            name="normalized-pvariation",
            version="1",
            citation="Cont & Das (2024), arXiv:2203.13820, eqs. 5-7; K = sqrt(L)",
            estimates=Estimand.H_LOG_VOL,
            consumes=_ANY_VOL,
            fn=cont_das,
        ),
        EstimatorSpec(
            name="pvariation-scaling-crossing",
            version="1",
            citation="Lumor (2026), roughvollab layer1c (labelled 'Cont-Das' there)",
            estimates=Estimand.H_LOG_VOL,
            consumes=_ANY_VOL,
            fn=scaling_crossing,
        ),
        EstimatorSpec(
            name="mfdfa",
            version="1",
            citation="Kantelhardt et al. (2002); settings from Lumor (2026) roughvollab",
            estimates=Estimand.H_LOG_VOL,
            consumes=_ANY_VOL,
            fn=mfdfa,
        ),
    )
}
