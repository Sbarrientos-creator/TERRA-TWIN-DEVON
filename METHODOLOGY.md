# Methodology

Owner: Planetary Science Researcher. Complete before trusting any result.

## Research questions

1. Which terrain variables of Haughton Crater resemble Shackleton Crater and a chosen Mars crater?
2. Which Earth locations best match a Moon or Mars target, factor by factor?

## Variables

- Slope distribution (degrees)
- Elevation variability (detrended elevation, m)
- Local relief (max - min in a 1 km window, m)
- Roughness (local std of detrended elevation in a 500 m window, m)

## Comparison approach

- Each DEM is reprojected to a local equal-area, meter-based CRS centered on the site.
- All DEMs are resampled to the same grid and the same window size.
- Raw elevations are never compared (different vertical datums); a best-fit plane is removed.
- Terrain-distribution overlap, Wasserstein distance and KS statistic are reported.
- Analog Finder scores each factor group separately (terrain, thermal, aridity/biology).

## Proposed Devon research zones (boundaries to be set from maps and imagery)

| Zone | Focus |
|---|---|
| A | Haughton impact structure |
| B | Crater rim and rocky terrain |
| C | Canyons and valleys |
| D | Polar desert and ice-related environments |

## Limitations (add more)

- Earth has an atmosphere, different gravity and different radiation; no site is a full analog.
- MOLA is 463 m native; resampling finer adds no real detail.
- Slope and roughness depend on scale; compare at the same scale only.
- CHIRPS does not cover polar latitudes.
- Overlap scores describe terrain morphology only, not total planetary similarity.
