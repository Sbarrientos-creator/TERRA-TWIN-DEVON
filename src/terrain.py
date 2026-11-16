import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from scipy import ndimage

# Mean radii in meters (used for the local projection of Mars and the Moon)
BODY_RADIUS = {"mars": 3_396_190.0, "moon": 1_737_400.0}


def local_crs(body: str, lon: float, lat: float) -> CRS:
    """Equal-area, meter-based CRS centered on the study site."""
    if body == "earth":
        return CRS.from_proj4(
            f"+proj=laea +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs")
    r = BODY_RADIUS[body]
    return CRS.from_proj4(
        f"+proj=laea +lat_0={lat} +lon_0={lon} +R={r} +units=m +no_defs")


def load_window(path, body, lon, lat, size_km=30.0, res_m=100.0):
    """Read a DEM and resample it onto a square local grid (meters).
    Returns (elevation array in meters with NaN for nodata, res_m, metadata)."""
    n = int(size_km * 1000 / res_m)
    half = size_km * 1000 / 2
    dst_transform = from_origin(-half, half, res_m, res_m)
    dst = np.full((n, n), np.nan, dtype="float32")

    with rasterio.open(path) as src:
        if src.crs is None:
            raise ValueError("DEM has no CRS; cannot reproject safely.")
        native_res = abs(src.transform.a)  # in source units (m or deg)
        # Bilinear when upsampling, average when downsampling
        resampling = Resampling.average if native_res < res_m else Resampling.bilinear
        reproject(
            source=rasterio.band(src, 1),
            destination=dst,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=dst_transform,
            dst_crs=local_crs(body, lon, lat),
            dst_nodata=np.nan,
            resampling=resampling,
        )
        scale = src.scales[0] if src.scales else 1.0
        offset = src.offsets[0] if src.offsets else 0.0
        meta = {"src_crs": str(src.crs), "src_res": native_res,
                "nodata": src.nodata, "scale": scale, "offset": offset}

    dst = dst * scale + offset
    valid_frac = float(np.isfinite(dst).mean())
    meta["valid_fraction"] = valid_frac
    if valid_frac < 0.8:
        raise ValueError(f"Only {valid_frac:.0%} valid pixels: wrong coordinates or tile?")
    return dst, res_m, meta


def detrend_plane(z):
    """Remove best-fit plane (regional tilt / datum differences)."""
    yy, xx = np.indices(z.shape)
    m = np.isfinite(z)
    A = np.c_[xx[m], yy[m], np.ones(m.sum())]
    coef, *_ = np.linalg.lstsq(A, z[m], rcond=None)
    plane = coef[0] * xx + coef[1] * yy + coef[2]
    return z - plane


def slope_deg(z, res_m):
    dzdy, dzdx = np.gradient(z, res_m)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy)))


def _filled(z):
    return np.where(np.isfinite(z), z, np.nanmedian(z))


def local_relief(z, res_m, window_m=1000.0):
    """Max - min elevation inside a moving window."""
    k = max(3, int(window_m / res_m) | 1)
    zf = _filled(z)
    return ndimage.maximum_filter(zf, size=k) - ndimage.minimum_filter(zf, size=k)


def roughness(z, res_m, window_m=500.0):
    """Local standard deviation of detrended elevation in a moving window."""
    k = max(3, int(window_m / res_m) | 1)
    zf = _filled(z)
    mean = ndimage.uniform_filter(zf, k)
    mean2 = ndimage.uniform_filter(zf ** 2, k)
    return np.sqrt(np.clip(mean2 - mean ** 2, 0, None))


def analyze(z, res_m):
    zd = detrend_plane(z)
    mask = np.isfinite(z)
    layers = {
        "slope_deg": slope_deg(z, res_m),
        "elev_detrended_m": zd,
        "local_relief_m": local_relief(z, res_m),
        "roughness_m": roughness(zd, res_m),
    }
    layers = {k: v[mask] for k, v in layers.items()}  # flat arrays of valid pixels
    stats = {}
    for k, v in layers.items():
        v = v[np.isfinite(v)]
        stats[k] = {"mean": float(v.mean()), "median": float(np.median(v)),
                    "std": float(v.std()),
                    "p5": float(np.percentile(v, 5)), "p95": float(np.percentile(v, 95))}
    return layers, stats
