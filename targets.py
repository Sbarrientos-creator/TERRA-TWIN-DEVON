from src.terrain import load_window, analyze


def terrain_profile(path, body, lon, lat, size_km=30, res_m=250):
    """Median slope and roughness of a Moon/Mars target window (same definitions as Earth)."""
    z, r, _ = load_window(path, body, lon, lat, size_km, res_m)
    layers, stats = analyze(z, r)
    return {"slope_deg": stats["slope_deg"]["median"],
            "roughness_m": stats["roughness_m"]["median"]}


# Thermal values MUST come from Diviner (Moon) / THEMIS or TES (Mars) data for the site,
# or from cited peer-reviewed papers. Fill them in; the app stops while any value is None.
# slope_deg and roughness_m should come from terrain_profile() on LOLA / MOLA.
TARGETS = {
    "Moon: Shackleton rim": {"slope_deg": None, "roughness_m": None,
                             "temp_mean_C": None, "diurnal_range_C": None,
                             "ndvi": 0.0, "precip_mm": 0.0},
    "Mars: Jezero": {"slope_deg": None, "roughness_m": None,
                     "temp_mean_C": None, "diurnal_range_C": None,
                     "ndvi": 0.0, "precip_mm": 0.0},
}
