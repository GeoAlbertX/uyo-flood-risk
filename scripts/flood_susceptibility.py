"""
Flood susceptibility index (FSI) by AHP-weighted overlay.

Reads aligned factor rasters (same CRS, extent and 30 m grid; see
docs/qgis_workflow.md, Step 7), reclassifies each to 1-5, applies the AHP
weights and writes:
  outputs/flood_susceptibility_index.tif   (continuous FSI)
  outputs/flood_susceptibility_class.tif   (1 = very low ... 5 = very high)
  outputs/class_areas.csv                  (area per class, km2)

Usage:
    python scripts/flood_susceptibility.py
Edit CONFIG below to match your file names.
"""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
OUT = ROOT / "outputs"

# method: "quantile_low"  -> low values  = high susceptibility (5)
#         "quantile_high" -> high values = high susceptibility (5)
#         "breaks_low"    -> fixed breaks, low values  = 5
#         "table"         -> category lookup (land cover codes)
CONFIG = {
    "distance_to_drainage": {"file": "dist_drainage.tif", "method": "breaks_low",
                             "breaks": [100, 250, 500, 1000]},
    "elevation":            {"file": "dem_filled.tif",    "method": "quantile_low"},
    "twi":                  {"file": "twi.tif",           "method": "quantile_high"},
    "slope":                {"file": "slope.tif",         "method": "breaks_low",
                             "breaks": [2, 5, 10, 15]},
    "land_cover":           {"file": "landcover.tif",     "method": "table",
                             # ESA WorldCover codes -> susceptibility
                             "table": {10: 1, 20: 2, 30: 3, 40: 4, 50: 5,
                                       60: 5, 80: 5, 90: 2, 95: 2, 100: 2}},
    "rainfall":             {"file": "rainfall.tif",      "method": "quantile_high"},
}


# ---------- core functions (pure numpy, testable without GIS files) ----------

def reclass_breaks_low(a, breaks):
    """Values below breaks[0] -> 5, ..., above breaks[-1] -> 1."""
    cls = 5 - np.digitize(a, breaks, right=False)
    return np.where(np.isnan(a), np.nan, cls).astype(float)


def reclass_quantile(a, high_is_bad):
    """Quintiles (20/40/60/80%). high_is_bad=True -> top 20% = 5."""
    valid = a[~np.isnan(a)]
    q = np.percentile(valid, [20, 40, 60, 80])
    if np.unique(q).size < 4:  # flat data: fall back to equal intervals
        q = np.linspace(valid.min(), valid.max(), 6)[1:-1]
    rank = np.digitize(a, q, right=False) + 1  # 1..5, low -> high
    cls = rank if high_is_bad else 6 - rank
    return np.where(np.isnan(a), np.nan, cls).astype(float)


def reclass_table(a, table):
    out = np.full(a.shape, np.nan)
    for code, value in table.items():
        out[a == code] = value
    return out


def reclassify(a, cfg):
    m = cfg["method"]
    if m == "breaks_low":
        return reclass_breaks_low(a, cfg["breaks"])
    if m == "quantile_low":
        return reclass_quantile(a, high_is_bad=False)
    if m == "quantile_high":
        return reclass_quantile(a, high_is_bad=True)
    if m == "table":
        return reclass_table(a, cfg["table"])
    raise ValueError(f"Unknown method: {m}")


def weighted_overlay(layers, weights):
    """layers: dict name -> reclassified array; weights: dict name -> weight."""
    total = sum(weights[n] for n in layers)
    fsi = sum(layers[n] * (weights[n] / total) for n in layers)
    return fsi  # NaN wherever any input is NaN


def classify_fsi(fsi):
    """Five susceptibility classes by quantile."""
    return reclass_quantile(fsi, high_is_bad=True)


# ---------- I/O (needs rasterio) ----------

def main():
    import rasterio  # imported here so the core functions work without it

    weights_file = OUT / "ahp_weights.json"
    if not weights_file.exists():
        raise SystemExit("Run scripts/ahp_weights.py first to create outputs/ahp_weights.json")
    weights = json.loads(weights_file.read_text())["weights"]

    layers, profile, pixel_area = {}, None, None
    for name, cfg in CONFIG.items():
        with rasterio.open(DATA / cfg["file"]) as src:
            a = src.read(1).astype(float)
            if src.nodata is not None:
                a[a == src.nodata] = np.nan
            if profile is None:
                profile = src.profile
                pixel_area = abs(src.transform.a * src.transform.e)
            elif a.shape != (profile["height"], profile["width"]):
                raise SystemExit(f"{cfg['file']} is not aligned. Run 'Align rasters' first.")
        layers[name] = reclassify(a, cfg)
        print(f"Reclassified {name}")

    fsi = weighted_overlay(layers, weights)
    classes = classify_fsi(fsi)

    OUT.mkdir(parents=True, exist_ok=True)
    profile.update(dtype="float32", count=1, nodata=-9999, compress="lzw")
    for arr, fname in [(fsi, "flood_susceptibility_index.tif"),
                       (classes, "flood_susceptibility_class.tif")]:
        with rasterio.open(OUT / fname, "w", **profile) as dst:
            dst.write(np.where(np.isnan(arr), -9999, arr).astype("float32"), 1)
        print(f"Wrote outputs/{fname}")

    labels = {1: "Very low", 2: "Low", 3: "Moderate", 4: "High", 5: "Very high"}
    rows = ["class,label,area_km2,percent"]
    valid = int((~np.isnan(classes)).sum())
    for c, label in labels.items():
        n = int((classes == c).sum())
        rows.append(f"{c},{label},{n * pixel_area / 1e6:.2f},{100 * n / valid:.1f}")
    (OUT / "class_areas.csv").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
