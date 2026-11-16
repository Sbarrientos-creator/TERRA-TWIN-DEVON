# Validation

Owner: Validation and Presentation. Record real results, including failures.

## Automated tests

Run `pytest`. Paste the output and date here.

## Independent slope check

Compare `slope_deg` against GDAL on the same DEM:

```bash
gdaldem slope dem.tif slope_gdal.tif -s 1
```

Record the difference here.

## Known-analog ranking

Run `python pipeline/04_validate.py`. Record where Haughton, Atacama, Death Valley and the
Dry Valleys rank, and explain any poor ranks.

## Checklist

- [ ] All three elevation datasets load
- [ ] Incompatible or missing CRS is detected
- [ ] Pixel dimensions correct
- [ ] Slope matches GDAL
- [ ] Comparison results reproducible
- [ ] Charts match the tables
- [ ] All sources documented
- [ ] Limitations explained

## Known problems

(none recorded yet)
