from __future__ import annotations

import numpy as np


def quadratic_weighted_kappa(y_true, y_pred, min_rating=None, max_rating=None) -> float:
    """Compute quadratic weighted kappa for ordinal ratings.

    Parameters are compatible with 1-4 holistic scores or 1-5 analytic scores.
    Missing values are removed pairwise.
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    mask = np.isfinite(yt) & np.isfinite(yp)
    yt = yt[mask].astype(int)
    yp = yp[mask].astype(int)
    if yt.size == 0:
        return np.nan
    if min_rating is None:
        min_rating = int(min(yt.min(), yp.min()))
    if max_rating is None:
        max_rating = int(max(yt.max(), yp.max()))
    ratings = np.arange(min_rating, max_rating + 1)
    n = len(ratings)
    O = np.zeros((n, n), dtype=float)
    for a, b in zip(yt, yp):
        if min_rating <= a <= max_rating and min_rating <= b <= max_rating:
            O[a - min_rating, b - min_rating] += 1
    hist_true = O.sum(axis=1)
    hist_pred = O.sum(axis=0)
    E = np.outer(hist_true, hist_pred) / max(O.sum(), 1)
    W = np.zeros((n, n), dtype=float)
    denom = (n - 1) ** 2
    for i in range(n):
        for j in range(n):
            W[i, j] = ((i - j) ** 2) / denom if denom else 0
    observed = (W * O).sum()
    expected = (W * E).sum()
    return 1 - observed / expected if expected != 0 else np.nan
