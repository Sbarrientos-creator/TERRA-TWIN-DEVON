"""Sanity-check data/processed/earth_features.csv before trusting any ranking."""
import pandas as pd

df = pd.read_csv("data/processed/earth_features.csv")
print(df.describe().T[["count", "min", "50%", "max"]])
cols = ["slope_deg", "roughness_m", "temp_mean_C", "ndvi", "precip_mm"]
print(df[cols].corr().round(2))


def near(lon, lat, d=2):
    return df[(abs(df.lon - lon) < d) & (abs(df.lat - lat) < d)]


# Atacama should show NDVI near 0.05 or below and very low precipitation.
print("Atacama points:\n", near(-69.2, -24.5)[["ndvi", "precip_mm"]].describe().T)
