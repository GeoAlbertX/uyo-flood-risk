# Step-by-step QGIS workflow (no coding)

This tutorial builds the Uyo flood susceptibility map using only QGIS 3.x (LTR). Each step gives the exact tool name, so you can search for it in the **Processing Toolbox** (Ctrl+Alt+T).

**Before you start:** install the **QuickOSM** plugin (*Plugins → Manage and Install Plugins*).

---

## Step 1 — Set up the project

1. *Project → New*. Save it as `uyo_flood.qgz` in the repository folder.
2. *Project → Properties → CRS*: choose **EPSG:32632 – WGS 84 / UTM zone 32N**.
3. Load the Uyo LGA boundary. If it's part of a national layer, select Uyo and use **Extract by attribute** to save it as `data/processed/uyo_boundary.gpkg`.
4. Run **Buffer** (1000 m) on the boundary to make `uyo_aoi.gpkg`. The buffer avoids edge effects in the terrain analysis.

## Step 2 — Prepare the DEM

1. Load the Copernicus DEM tile(s). If there are several, use **Merge**.
2. **Warp (reproject)**: target CRS EPSG:32632, resolution 30 m, resampling *Bilinear*.
3. **Clip raster by mask layer**: mask = `uyo_aoi`. Save as `dem_30m.tif`.
4. **Fill sinks (Wang & Liu)** (SAGA): removes small pits so water can flow. Save as `dem_filled.tif`.

## Step 3 — Terrain factors

| Factor | Tool | Input | Output |
|---|---|---|---|
| Elevation | (use the DEM) | `dem_filled.tif` | — |
| Slope | **Slope** (GDAL or Raster terrain analysis), in degrees | `dem_filled.tif` | `slope.tif` |
| TWI | **SAGA Wetness Index** or **Topographic Wetness Index (TWI)** (SAGA) | `dem_filled.tif` | `twi.tif` |
| Stream network | **r.watershed** (GRASS), threshold ≈ 500 cells, then **r.to.vect** | `dem_filled.tif` | `streams.gpkg` |

## Step 4 — Distance to drainage

1. **QuickOSM**: key `waterway`, value *(leave blank)*, "In" Uyo. This fetches rivers, streams, drains and canals. Save as `osm_waterways.gpkg`.
2. **Merge vector layers**: `osm_waterways` + `streams` → `drainage.gpkg`.
3. **Rasterize (vector to raster)**: burn value 1, 30 m, extent = `dem_filled`.
4. **Proximity (raster distance)**: target value 1, distance units *Georeferenced*. Save as `dist_drainage.tif`.

## Step 5 — Rainfall

1. Load the CHIRPS annual (or mean of monthly) rasters for your period, e.g. 1991–2020.
2. **Cell statistics** (or Raster calculator): mean → mean annual rainfall.
3. **Warp** to EPSG:32632 at 30 m (bilinear) and **Clip** to `uyo_aoi`. Save as `rainfall.tif`.

> CHIRPS is ~5 km, so rainfall will look smooth across Uyo. That's expected: it adds the regional rainfall gradient, while the terrain factors add local detail.

## Step 6 — Land cover

1. Load the ESA WorldCover tile.
2. **Warp** to EPSG:32632 at 30 m using **Nearest neighbour** resampling (never bilinear for classes).
3. **Clip** to `uyo_aoi`. Save as `landcover.tif`.

## Step 7 — Align all rasters

Use **Align rasters** (*Raster → Align Rasters*). Reference layer: `dem_filled.tif`, cell size 30 m, and the same extent for every layer. Every layer must line up cell for cell before the overlay.

## Step 8 — Reclassify each factor to 1–5

Use **Reclassify by table** for each factor. For quantile classes, look up the 20/40/60/80 percentiles under *Layer Properties → Information*, or with **Raster layer statistics** / **Raster layer unique values report**.

Example, slope:

| Min | Max | Value |
|---|---|---|
| 0 | 2 | 5 |
| 2 | 5 | 4 |
| 5 | 10 | 3 |
| 10 | 15 | 2 |
| 15 | 90 | 1 |

Example, ESA WorldCover classes:

| WorldCover code | Class | Value |
|---|---|---|
| 50, 60 | Built-up, Bare | 5 |
| 40 | Cropland | 4 |
| 30 | Grassland | 3 |
| 20, 90, 95 | Shrubland, Wetland, Mangroves | 2 |
| 10 | Tree cover | 1 |
| 80 | Permanent water | 5 |

Save as `r_elev.tif`, `r_slope.tif`, `r_twi.tif`, `r_dist.tif`, `r_rain.tif` and `r_lulc.tif`. The full class table is in `methodology.md`.

## Step 9 — AHP weights

Run `python scripts/ahp_weights.py`, or use the default weights it prints, and check that **CR < 0.10**. Write the final weights down; you'll need them in Step 10.

## Step 10 — Weighted overlay

Open the **Raster calculator** and enter the formula below. These are the weights from the default matrix in `ahp_weights.py` (CR = 0.01); replace them if you change the matrix.

```
0.334 * "r_dist@1" + 0.196 * "r_elev@1" + 0.185 * "r_twi@1"
+ 0.108 * "r_slope@1" + 0.108 * "r_lulc@1" + 0.069 * "r_rain@1"
```

Save as `flood_susceptibility_index.tif`.

## Step 11 — Classify and style

1. *Layer Properties → Symbology → Singleband pseudocolor*, mode **Quantile** or **Natural breaks (Jenks)**, 5 classes.
2. Label the classes: Very low, Low, Moderate, High, Very high. A green → red colour ramp works well.
3. Clip to the Uyo boundary (not the buffer) for the final map.
4. Optional: **Polygonize** the classes and compute the area of each class with the **Field calculator** (`$area / 1e6` = km²).

## Step 12 — Validate

Add your flood-point layer, then use **Sample raster values** to read the susceptibility class at each point. Report the percentage of points in High + Very high.

## Step 13 — Map layout

*Project → New Print Layout*. Add the map, legend, scale bar, north arrow, title, data credits and your name. Export to `maps/uyo_flood_susceptibility.png` (300 dpi) and PDF.

---

**Tip:** save each processing step in a **Model Designer** model (*Processing → Graphical Modeler*) and commit the `.model3` file. Others can then rerun your whole workflow in one click.
