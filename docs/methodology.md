# Methodology

## 1. Study area

**Uyo**, the capital of Akwa Ibom State in south-south Nigeria, lies on the coastal plain sands of the Niger Delta region. The city has a humid tropical climate with a long rainy season (roughly March–October) and high annual rainfall. Rapid urban expansion has replaced vegetated land with impervious surfaces. Natural drainage follows small streams and valleys, so low-lying, built-up areas near these channels flood after intense storms.

Boundary: Uyo Local Government Area (LGA), or a buffer around the urban area. See `data_sources.md` for the boundary source.

## 2. Two parts to the analysis

| Part | Question | Method |
|---|---|---|
| A. Rainfall trend | Has rainfall in Uyo changed over time? | Mann–Kendall trend test + Sen's slope on annual (and wet-season) rainfall |
| B. Flood susceptibility | Where is flooding most likely? | GIS multi-criteria analysis, weighted by AHP |

---

## Part A — Rainfall trend analysis

**Data:** CHIRPS v2.0 monthly rainfall (1981–present, ~5 km), extracted for Uyo and summed by year.

**Steps**
1. Extract the monthly CHIRPS value at Uyo (or the mean over the study area).
2. Sum to annual totals, and to wet-season totals (Mar–Oct).
3. Run the **Mann–Kendall test**, a non-parametric test for a monotonic trend, at a 5% significance level.
4. Estimate the trend size with **Sen's slope** (mm per year).
5. Optional: count heavy-rain months or days above a threshold (e.g. the 95th percentile) to check whether extremes are increasing.

**Script:** `scripts/rainfall_trend.py`

**Interpretation:** a significant positive Sen's slope means rainfall is increasing. This supports the link between changing rainfall and flood frequency explored in the B.Sc. thesis.

---

## Part B — Flood susceptibility (multi-criteria analysis)

### 2.1 Conditioning factors

| # | Factor | Source | Why it matters | High susceptibility when… |
|---|---|---|---|---|
| 1 | Elevation | Copernicus DEM 30 m | Water collects in low ground | Low elevation |
| 2 | Slope | Derived from DEM | Flat land drains slowly | Gentle slope |
| 3 | Topographic Wetness Index (TWI) | Derived from DEM | Shows where water accumulates | High TWI |
| 4 | Distance to drainage | OSM waterways + DEM-derived streams | Land near channels floods first | Close to drainage |
| 5 | Rainfall | CHIRPS mean annual | More rain means more runoff | High rainfall |
| 6 | Land use / land cover | ESA WorldCover 10 m | Built-up surfaces stop infiltration | Built-up / bare |

All layers are clipped to the study area, projected to **WGS 84 / UTM zone 32N (EPSG:32632)** and resampled to the same 30 m grid.

### 2.2 Reclassification

Each factor is reclassified to a common scale: **1 = very low** to **5 = very high** susceptibility.

| Factor | 5 (very high) | 4 | 3 | 2 | 1 (very low) |
|---|---|---|---|---|---|
| Elevation | lowest 20% | 20–40% | 40–60% | 60–80% | highest 20% |
| Slope (°) | 0–2 | 2–5 | 5–10 | 10–15 | > 15 |
| TWI | highest 20% | 60–80% | 40–60% | 20–40% | lowest 20% |
| Distance to drainage (m) | 0–100 | 100–250 | 250–500 | 500–1000 | > 1000 |
| Rainfall | highest 20% | 60–80% | 40–60% | 20–40% | lowest 20% |
| Land cover | Built-up, bare | Cropland | Grassland | Shrubland | Tree cover |

Percentile classes (quantiles) are used for elevation, TWI and rainfall because their ranges differ between study areas. The fixed thresholds for slope and distance follow common practice in the flood-susceptibility literature. Adjust them to local knowledge and record any changes.

### 2.3 Weighting with AHP

Factor weights come from the **Analytic Hierarchy Process (AHP)** (Saaty, 1980):

1. Compare each pair of factors on Saaty's 1–9 scale (e.g. "distance to drainage is moderately more important than rainfall" = 3).
2. Compute weights from the comparison matrix (principal eigenvector).
3. Check the **Consistency Ratio (CR)**. **CR < 0.10** means the judgements are acceptably consistent.

The matrix in `scripts/ahp_weights.py` is a **starting point** based on factors commonly ranked in flood studies. Review it against the literature and local knowledge, and document your final choices.

### 2.4 Weighted overlay

```
FSI = Σ (weightᵢ × reclassified_factorᵢ)
```

The Flood Susceptibility Index (FSI) is then grouped into five classes (Very low → Very high) using natural breaks or quantiles.

**Script:** `scripts/flood_susceptibility.py` (or the QGIS Raster Calculator; see `qgis_workflow.md`).

### 2.5 Validation

A susceptibility map is only credible if it is checked. Options:

- **Reported flood points:** collect locations from news reports, NEMA/SEMA reports, social media and field visits. Check what share fall in the High/Very high classes.
- **ROC curve / AUC:** if you have enough flood and non-flood points, compute the area under the ROC curve (AUC > 0.7 is acceptable; > 0.8 is good).
- **Satellite flood extent:** compare with Sentinel-1 radar flood mapping for a known flood event.

Report the validation honestly, including its limits.

### 2.6 Limitations

- 30 m DEMs miss small urban drains and culverts, which control real flooding in cities.
- CHIRPS is a satellite–gauge blend, so it may under- or over-estimate local rainfall compared with NiMet station data.
- AHP weights involve expert judgement. Sensitivity testing (changing weights ±10–20%) shows how robust the map is.
- Susceptibility is not the same as **risk**. Risk also needs exposure (people, buildings) and vulnerability, which is a possible next stage.

## References

- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259.
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. *JASA*, 63(324), 1379–1389.
- Funk, C. et al. (2015). The climate hazards infrared precipitation with stations (CHIRPS). *Scientific Data*, 2, 150066.
- Beven, K. J. & Kirkby, M. J. (1979). A physically based, variable contributing area model of basin hydrology. *Hydrological Sciences Bulletin*, 24(1), 43–69.
