# Uyo Flood Risk Mapping — Open-Source GIS Framework

A reproducible, open-source workflow for mapping **flood susceptibility** in **Uyo, Akwa Ibom State, Nigeria**. It combines terrain analysis, rainfall trends and land use with a GIS multi-criteria (AHP) model, using only **free data** and **free software** (QGIS, GRASS, Python).

This project builds on my B.Sc. research, *"Changing rainfall patterns and its implication for flooding in Uyo"*. It extends that work into a geospatial framework that others in African cities can reuse.

> **Status:** framework and method published. Results and maps for Uyo are being added step by step (see [Roadmap](#roadmap)).

---

## Why this project

Urban flooding is one of the most frequent hazards in southern Nigerian cities. Uyo combines heavy, increasingly intense rainfall with fast urban growth and limited drainage. Many local studies stop at describing the problem. This project aims to:

1. Quantify **how rainfall in Uyo has changed** over recent decades (trend analysis).
2. Map **where flooding is most likely**, by combining terrain, rainfall and land use.
3. Share a **free, step-by-step method** that students and planners elsewhere in Africa can repeat.

## Method at a glance

```
 DEM (Copernicus/SRTM) ──► Elevation, Slope, TWI ──┐
 OSM waterways/drains ──► Distance to drainage ────┤
 CHIRPS rainfall ───────► Mean annual rainfall ────┼─► Reclassify (1–5) ─► AHP weighted overlay ─► Flood susceptibility map
 ESA WorldCover ────────► Land use / land cover ───┘                                              (Very low … Very high)

 CHIRPS rainfall (1981–present) ─► Mann–Kendall trend + Sen's slope ─► Is rainfall in Uyo changing?
```

Full details: [`docs/methodology.md`](docs/methodology.md)

## Repository structure

```
uyo-flood-risk/
├── README.md                 ← you are here
├── docs/
│   ├── methodology.md        ← factors, classes, AHP weighting, validation
│   ├── data_sources.md       ← every dataset, where to download it, licence
│   └── qgis_workflow.md      ← step-by-step QGIS tutorial (no coding needed)
├── scripts/
│   ├── ahp_weights.py        ← computes AHP factor weights + consistency check
│   ├── rainfall_trend.py     ← Mann–Kendall trend test and Sen's slope on rainfall
│   └── flood_susceptibility.py ← reclassify rasters + weighted overlay
├── data/                     ← raw and processed data (large files not committed)
├── maps/                     ← exported map layouts (PNG/PDF)
├── outputs/                  ← tables and results
└── requirements.txt
```

## Quick start

**No coding (QGIS only):** follow [`docs/qgis_workflow.md`](docs/qgis_workflow.md).

**With Python:**

```bash
pip install -r requirements.txt

# 1. Factor weights (edit the comparison matrix inside the script if needed)
python scripts/ahp_weights.py

# 2. Rainfall trend for Uyo (CSV with columns: year, rainfall_mm)
python scripts/rainfall_trend.py data/processed/uyo_annual_rainfall.csv

# 3. Flood susceptibility (paths to aligned rasters in the script config)
python scripts/flood_susceptibility.py
```

## Tools

- [QGIS](https://qgis.org) (3.x LTR) with GRASS and SAGA providers
- Python 3 — `numpy`, `scipy`, `pandas`, `rasterio`
- Free data: Copernicus DEM, CHIRPS, ESA WorldCover, OpenStreetMap

## Roadmap

- [x] Method and framework documented
- [x] AHP weighting and rainfall-trend scripts
- [ ] Download and prepare Uyo datasets
- [ ] Rainfall trend results for Uyo (1981–present)
- [ ] Flood susceptibility map for Uyo
- [ ] Validation against reported flood locations
- [ ] Extend the framework to Lagos

## About me

**Atta Albert** — GIS researcher (climate, flood risk & geomorphology), Lagos, Nigeria.
Member, OSGeo Africa Local Chapter.

- GitHub: [GeoAlbertX](https://github.com/GeoAlbertX)
- LinkedIn: [albert-a-151875236](https://www.linkedin.com/in/albert-a-151875236)

## Licence

Code: [MIT](LICENSE). Documentation and maps: CC BY 4.0. Each dataset keeps its own licence (see [`docs/data_sources.md`](docs/data_sources.md)).
