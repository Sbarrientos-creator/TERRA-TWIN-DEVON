import numpy as np
from scipy.stats import wasserstein_distance, ks_2samp


def overlap_coefficient(a, b, bins=50):
    """Shared area of two normalized histograms (0 = disjoint, 1 = identical)."""
    lo = min(np.nanpercentile(a, 1), np.nanpercentile(b, 1))
    hi = max(np.nanpercentile(a, 99), np.nanpercentile(b, 99))
    if hi <= lo:
        hi = lo + 1e-9
    edges = np.linspace(lo, hi, bins + 1)
    pa, _ = np.histogram(a, edges)
    pb, _ = np.histogram(b, edges)
    pa = pa / max(pa.sum(), 1)
    pb = pb / max(pb.sum(), 1)
    return float(np.minimum(pa, pb).sum())


def compare(layers_a, layers_b, max_samples=200_000, seed=0):
    """Terrain-distribution comparison only. Not total planetary similarity."""
    rng = np.random.default_rng(seed)  # fixed seed -> reproducible
    rows = []
    for var in layers_a:
        a, b = layers_a[var], layers_b[var]
        a = rng.choice(a, min(len(a), max_samples), replace=False)
        b = rng.choice(b, min(len(b), max_samples), replace=False)
        rows.append({
            "variable": var,
            "overlap": overlap_coefficient(a, b),
            "wasserstein": float(wasserstein_distance(a, b)),
            "ks_stat": float(ks_2samp(a, b).statistic),
        })
    return rows
