import numpy as np

from exponent.domain.scoring.idmap import CellStatus, curve_statuses

GRID = [0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60]


def test_faithful_curve_identifies_rough_cells_and_marks_controls() -> None:
    st = curve_statuses(GRID, GRID, [0.01] * 7)
    assert st[:4] == [CellStatus.IDENTIFIED] * 4
    assert st[-1] is CellStatus.DE_BIASABLE  # H ≥ ½ is a control cell


def test_wide_spread_cannot_exclude_the_smooth_null() -> None:
    st = curve_statuses(GRID, GRID, [0.5] * 7)
    assert CellStatus.IDENTIFIED not in st


def test_hump_curve_is_non_identified_everywhere() -> None:
    hump = [0.1, 0.2, 0.3, 0.35, 0.3, 0.2, 0.1]
    assert set(curve_statuses(GRID, hump, [0.01] * 7)) == {CellStatus.NON_IDENTIFIED}


def test_flat_curve_collapses() -> None:
    flat = [0.08 + 0.01 * h for h in GRID]
    assert set(curve_statuses(GRID, flat, [0.001] * 7)) == {CellStatus.NON_IDENTIFIED}


def test_missing_mean_is_uncalibrated() -> None:
    mean = list(GRID)
    mean[2] = np.nan
    assert curve_statuses(GRID, mean, [0.01] * 7)[2] is CellStatus.UNCALIBRATED
