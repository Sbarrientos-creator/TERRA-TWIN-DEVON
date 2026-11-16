"""Build the Earth feature table with Google Earth Engine.
Usage: python pipeline/02_earth_features.py 50     (start small, then 3000)

Known limits (document them in docs/METHODOLOGY.md):
- CHIRPS only covers about 50S-50N, so polar points get dropped by dropna().
  Use ERA5-Land precipitation or sample polar sites separately if you need them.
- Random global points include a lot of ocean; oversample about 3x.
- Add known analog sites (Haughton, Atacama, Death Valley, Dry Valleys) as extra rows.
"""
import os
import sys

import ee
import pandas as pd

ee.Initialize(project=os.environ["GEE_PROJECT"])
YEAR = ("2022-01-01", "2023-01-01")


def build_image():
    col = ee.ImageCollection("COPERNICUS/DEM/GLO30").select("DEM")
    proj = col.first().select(0).projection()
    dem = col.mosaic().setDefaultProjection(proj)

    slope = ee.Terrain.slope(dem).rename("slope_deg")
    rough = dem.reduceNeighborhood(ee.Reducer.stdDev(),
                                   ee.Kernel.square(5)).rename("roughness_m")
    terrain = dem.rename("elev_m").addBands([slope, rough])
    # Average the 30 m terrain up to 1 km so it matches MODIS/CHIRPS scale
    terrain = (terrain.reduceResolution(ee.Reducer.mean(), bestEffort=True, maxPixels=1024)
                      .reproject(crs="EPSG:4326", scale=1000))

    lst = ee.ImageCollection("MODIS/061/MOD11A1").filterDate(*YEAR)
    day = lst.select("LST_Day_1km").mean().multiply(0.02).subtract(273.15)
    night = lst.select("LST_Night_1km").mean().multiply(0.02).subtract(273.15)
    thermal = ee.Image.cat([day.add(night).divide(2).rename("temp_mean_C"),
                            day.subtract(night).rename("diurnal_range_C")])

    ndvi = (ee.ImageCollection("MODIS/061/MOD13A2").filterDate(*YEAR)
            .select("NDVI").mean().multiply(0.0001).rename("ndvi"))
    precip = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterDate(*YEAR)
              .sum().rename("precip_mm"))
    return terrain.addBands([thermal, ndvi, precip])


def sample(img, n, seed, bbox):
    region = ee.Geometry.Rectangle(bbox)
    pts = ee.FeatureCollection.randomPoints(region, n, seed)
    out = img.reduceRegions(pts, ee.Reducer.first(), scale=1000, tileScale=4).getInfo()
    return pd.DataFrame([{**f["properties"],
                          "lon": f["geometry"]["coordinates"][0],
                          "lat": f["geometry"]["coordinates"][1]}
                         for f in out["features"]])


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    img = build_image()
    bbox = (-180, -60, 180, 83)
    parts = []
    for i in range(0, total, 250):
        parts.append(sample(img, min(250, total - i), seed=i, bbox=bbox))
        print("batch", i, "done")
    df = pd.concat(parts).dropna()
    df = df[df.elev_m > 0]  # drop oceans
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/earth_features.csv", index=False)
    print(len(df), "rows saved")
