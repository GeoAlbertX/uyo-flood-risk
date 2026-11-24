# Data sources

All data used here is free. Large files are **not** stored in this repository. Download them into `data/raw/` using the links below.

| Layer | Dataset | Resolution | Where to get it | Licence |
|---|---|---|---|---|
| Elevation | Copernicus DEM GLO-30 | 30 m | [OpenTopography](https://portal.opentopography.org) or [Copernicus Data Space](https://dataspace.copernicus.eu) | Free, with attribution |
| Elevation (alternative) | SRTM 1 Arc-Second | 30 m | [USGS EarthExplorer](https://earthexplorer.usgs.gov) | Public domain |
| Rainfall | CHIRPS v2.0 (monthly) | ~5 km | [UCSB Climate Hazards Center](https://data.chc.ucsb.edu/products/CHIRPS-2.0/) | Public domain |
| Land cover | ESA WorldCover 2021 | 10 m | [ESA WorldCover viewer](https://viewer.esa-worldcover.org) | CC BY 4.0 |
| Waterways / drains | OpenStreetMap | Vector | QGIS **QuickOSM** plugin, or [Geofabrik Nigeria extract](https://download.geofabrik.de/africa/nigeria.html) | ODbL |
| Boundary | Nigeria LGA boundaries | Vector | [HDX – Nigeria subnational boundaries](https://data.humdata.org) or [GRID3 Nigeria](https://grid3.org) | Check the dataset page |
| Rainfall (station, optional) | NiMet station records | Point | Nigerian Meteorological Agency (on request) | On request |
| Flood events (validation) | Reported floods | Points | News, NEMA/SEMA reports, field visits | Your own collection |

## Notes

- **Coordinate system:** reproject everything to **EPSG:32632 (WGS 84 / UTM zone 32N)** so distances and slopes are in metres.
- **Copernicus DEM vs SRTM:** Copernicus GLO-30 is generally more accurate. Both are surface models, so buildings and trees raise the elevation in built-up areas.
- **CHIRPS:** monthly GeoTIFFs can be clipped in QGIS. Alternatively, use the [Climate Engine](https://app.climateengine.org) web app to export a time series for a point as CSV.
- **Attribution:** credit every dataset on your maps and in reports.

## Folder layout

```
data/
├── raw/         ← original downloads (not committed)
└── processed/   ← clipped, projected, aligned layers + uyo_annual_rainfall.csv
```
