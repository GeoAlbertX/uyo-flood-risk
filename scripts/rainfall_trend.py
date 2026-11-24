"""
Rainfall trend analysis: Mann-Kendall test + Sen's slope.

Input: a CSV with columns `year` and `rainfall_mm` (one row per year).
       Optional extra column `wet_season_mm` is analysed too if present.

Usage:
    python scripts/rainfall_trend.py data/processed/uyo_annual_rainfall.csv

Output: results printed and saved to outputs/rainfall_trend.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm


def mann_kendall(x):
    """Mann-Kendall trend test with tie correction.

    Returns dict with S, variance, Z, p-value (two-sided) and trend label.
    """
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 8:
        raise ValueError("Need at least 8 values for a meaningful trend test.")

    s = 0
    for k in range(n - 1):
        s += np.sign(x[k + 1:] - x[k]).sum()

    _, counts = np.unique(x, return_counts=True)
    ties = counts[counts > 1]
    var_s = (n * (n - 1) * (2 * n + 5)
             - (ties * (ties - 1) * (2 * ties + 5)).sum()) / 18.0

    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0
    p = 2 * (1 - norm.cdf(abs(z)))

    if p < 0.05:
        trend = "increasing" if z > 0 else "decreasing"
    else:
        trend = "no significant trend"
    return {"n": n, "S": int(s), "var_S": var_s, "Z": z, "p_value": p, "trend": trend}


def sens_slope(years, x):
    """Sen's slope: median of all pairwise slopes (units per year)."""
    years = np.asarray(years, dtype=float)
    x = np.asarray(x, dtype=float)
    mask = ~np.isnan(x)
    years, x = years[mask], x[mask]
    slopes = []
    for i in range(len(x) - 1):
        dy = x[i + 1:] - x[i]
        dt = years[i + 1:] - years[i]
        slopes.extend((dy / dt)[dt != 0])
    return float(np.median(slopes))


def analyse(df, column):
    mk = mann_kendall(df[column].values)
    slope = sens_slope(df["year"].values, df[column].values)
    return {
        "variable": column,
        "years": f"{int(df['year'].min())}-{int(df['year'].max())}",
        "n": mk["n"],
        "mean_mm": round(float(df[column].mean()), 1),
        "MK_Z": round(mk["Z"], 3),
        "p_value": round(mk["p_value"], 4),
        "sen_slope_mm_per_year": round(slope, 2),
        "change_per_decade_mm": round(slope * 10, 1),
        "trend": mk["trend"],
    }


def main(path):
    df = pd.read_csv(path).sort_values("year")
    if not {"year", "rainfall_mm"}.issubset(df.columns):
        raise SystemExit("CSV must have columns: year, rainfall_mm")

    columns = ["rainfall_mm"] + [c for c in ["wet_season_mm"] if c in df.columns]
    results = pd.DataFrame([analyse(df, c) for c in columns])

    print(results.to_string(index=False))
    out = Path(__file__).resolve().parent.parent / "outputs" / "rainfall_trend.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(out, index=False)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/rainfall_trend.py <annual_rainfall.csv>")
    main(sys.argv[1])
