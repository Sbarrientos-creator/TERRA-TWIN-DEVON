"""Run first. Tells you which accounts or dataset IDs are broken."""
import os

import earthaccess
import ee

project = os.environ["GEE_PROJECT"]
ee.Initialize(project=project)
for ds in ["COPERNICUS/DEM/GLO30", "MODIS/061/MOD11A1",
           "MODIS/061/MOD13A2", "UCSB-CHG/CHIRPS/DAILY"]:
    try:
        n = ee.ImageCollection(ds).size().getInfo()
        print("OK  ", ds, n, "images")
    except Exception as e:
        print("FAIL", ds, "->", str(e)[:120])   # fix the ID in the Earth Engine Data Catalog

auth = earthaccess.login(strategy="environment")
print("Earthdata login:", "OK" if auth and auth.authenticated else "FAILED")
