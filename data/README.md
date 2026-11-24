# Data folder

- `raw/` — original downloads (DEM tiles, CHIRPS, WorldCover). Not committed to Git because the files are large.
- `processed/` — clipped, projected (EPSG:32632) and aligned layers, plus `uyo_annual_rainfall.csv`.

See [`../docs/data_sources.md`](../docs/data_sources.md) for download links.

Expected rainfall CSV format:

```
year,rainfall_mm,wet_season_mm
1981,2450.3,2101.7
1982,2390.8,2050.2
...
```
(`wet_season_mm` is optional.)
