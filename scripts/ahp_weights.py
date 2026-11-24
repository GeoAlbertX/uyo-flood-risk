"""
AHP (Analytic Hierarchy Process) weights for flood susceptibility factors.

Computes factor weights from a pairwise comparison matrix using the
principal eigenvector, then checks the Consistency Ratio (CR).
CR < 0.10 means the judgements are acceptably consistent (Saaty, 1980).

Usage:
    python scripts/ahp_weights.py

Edit FACTORS and MATRIX below to reflect your own judgements.
MATRIX[i][j] = how much more important factor i is than factor j (1-9 scale).
The matrix must be reciprocal: MATRIX[j][i] = 1 / MATRIX[i][j].
"""

import json
import sys
from pathlib import Path

import numpy as np

FACTORS = [
    "distance_to_drainage",
    "elevation",
    "twi",
    "slope",
    "land_cover",
    "rainfall",
]

# Starting-point judgements, based on factors commonly ranked in
# flood-susceptibility studies. Review and adjust them for Uyo.
#            dist   elev   twi    slope  lulc   rain
MATRIX = [
    [1,     2,     2,     3,     3,     4],    # distance to drainage
    [1/2,   1,     1,     2,     2,     3],    # elevation
    [1/2,   1,     1,     2,     2,     2],    # TWI
    [1/3,   1/2,   1/2,   1,     1,     2],    # slope
    [1/3,   1/2,   1/2,   1,     1,     2],    # land cover
    [1/4,   1/3,   1/2,   1/2,   1/2,   1],    # rainfall
]

# Saaty's Random Index for matrices of size n
RANDOM_INDEX = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
                7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}


def ahp(matrix):
    """Return (weights, lambda_max, CI, CR) for a pairwise comparison matrix."""
    a = np.asarray(matrix, dtype=float)
    n = a.shape[0]
    if a.shape != (n, n):
        raise ValueError("Matrix must be square.")
    if not np.allclose(a * a.T, 1.0, atol=1e-6):
        raise ValueError("Matrix must be reciprocal: a[j][i] = 1 / a[i][j].")

    eigvals, eigvecs = np.linalg.eig(a)
    idx = int(np.argmax(eigvals.real))
    lambda_max = float(eigvals[idx].real)
    w = np.abs(eigvecs[:, idx].real)
    w = w / w.sum()

    ci = (lambda_max - n) / (n - 1) if n > 2 else 0.0
    ri = RANDOM_INDEX.get(n, 1.49)
    cr = ci / ri if ri > 0 else 0.0
    return w, lambda_max, ci, cr


def main():
    weights, lambda_max, ci, cr = ahp(MATRIX)

    print("AHP factor weights")
    print("-" * 40)
    for name, w in sorted(zip(FACTORS, weights), key=lambda x: -x[1]):
        print(f"{name:<24}{w:>8.3f}  ({w * 100:5.1f}%)")
    print("-" * 40)
    print(f"lambda_max = {lambda_max:.3f}")
    print(f"CI         = {ci:.3f}")
    print(f"CR         = {cr:.3f}  ->  "
          f"{'OK (consistent)' if cr < 0.10 else 'TOO HIGH - revise judgements'}")

    out = Path(__file__).resolve().parent.parent / "outputs" / "ahp_weights.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "weights": {f: round(float(w), 4) for f, w in zip(FACTORS, weights)},
        "lambda_max": round(lambda_max, 4),
        "CI": round(ci, 4),
        "CR": round(cr, 4),
    }, indent=2))
    print(f"\nSaved to {out}")
    return 0 if cr < 0.10 else 1


if __name__ == "__main__":
    sys.exit(main())
