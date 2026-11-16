import numpy as np
import pandas as pd

from src.analog import GROUPS, score
from src.similarity import compare, overlap_coefficient
from src.terrain import analyze, detrend_plane, slope_deg


def test_known_slope():
    res = 100.0
    x = np.arange(100) * res
    z = np.tile(np.tan(np.radians(10)) * x, (100, 1))   # plane tilted 10 deg
    s = slope_deg(z, res)
    assert abs(np.nanmedian(s) - 10) < 0.01


def test_flat_terrain_zero_roughness():
    layers, stats = analyze(np.full((100, 100), 500.0), 100.0)
    assert stats["roughness_m"]["mean"] < 1e-6


def test_detrend_removes_plane():
    yy, xx = np.indices((50, 50))
    z = 3 * xx + 2 * yy + 7.0
    assert np.abs(detrend_plane(z)).max() < 1e-6


def test_overlap_identical_is_one():
    a = np.random.default_rng(0).normal(size=5000)
    assert overlap_coefficient(a, a) > 0.999


def test_compare_is_reproducible():
    rng = np.random.default_rng(1)
    la = {"slope_deg": rng.normal(10, 3, 5000)}
    lb = {"slope_deg": rng.normal(12, 3, 5000)}
    assert compare(la, lb, max_samples=1000) == compare(la, lb, max_samples=1000)


def test_score_prefers_closest_candidate():
    df = pd.DataFrame({
        "slope_deg": [5, 20, 6, 30], "roughness_m": [2, 30, 3, 40],
        "temp_mean_C": [-10, 25, -9, 30], "diurnal_range_C": [20, 10, 21, 8],
        "precip_mm": [10, 800, 12, 1200], "ndvi": [0.02, 0.6, 0.03, 0.7],
        "lon": [0, 1, 2, 3], "lat": [0, 1, 2, 3]})
    target = {"slope_deg": 5, "roughness_m": 2, "temp_mean_C": -10,
              "diurnal_range_C": 20, "precip_mm": 10, "ndvi": 0.02}
    res = score(df, target, {g: 1.0 for g in GROUPS})
    assert res.loc[0, "lon"] == 0
