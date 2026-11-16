import numpy as np
import pandas as pd

GROUPS = {
    "terrain": ["slope_deg", "roughness_m"],
    "thermal": ["temp_mean_C", "diurnal_range_C"],
    "aridity_biology": ["precip_mm", "ndvi"],
}
LOG_VARS = ["roughness_m", "precip_mm"]


def score(candidates: pd.DataFrame, target: dict, weights: dict) -> pd.DataFrame:
    """Rank Earth candidates by similarity to a target. Each factor group is scored
    separately (0..1), then combined with user weights."""
    df = candidates.copy()
    feats = [f for g in GROUPS.values() for f in g]
    for f in LOG_VARS:
        df[f] = np.log1p(df[f].clip(lower=0))
    t = dict(target)
    for f in LOG_VARS:
        t[f] = np.log1p(max(t[f], 0))
    med = df[feats].median()
    mad = (df[feats] - med).abs().median() * 1.4826 + 1e-9
    for g, cols in GROUPS.items():
        d2 = sum((((df[c] - t[c]) / mad[c]) ** 2) for c in cols) / len(cols)
        df[f"sim_{g}"] = np.exp(-0.5 * d2)
    wsum = sum(weights.values()) or 1.0
    df["sim_total"] = sum(weights[g] * df[f"sim_{g}"] for g in GROUPS) / wsum
    return df.sort_values("sim_total", ascending=False).reset_index(drop=True)
