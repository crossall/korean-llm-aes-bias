from __future__ import annotations

from typing import Iterable, List

import pandas as pd

DEFAULT_STRATA = ["region", "gender", "subject", "format"]


def stratified_sample_by_grade(
    df: pd.DataFrame,
    n_per_grade: int = 1000,
    grade_col: str = "grade_num",
    strata_cols: List[str] | None = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Draw approximately n_per_grade records per grade preserving strata proportions."""
    if strata_cols is None:
        strata_cols = DEFAULT_STRATA
    records = []
    for grade, gdf in df.groupby(grade_col, dropna=False):
        target = min(n_per_grade, len(gdf))
        # Build a composite stratum; missing values are explicit to avoid dropping rows.
        tmp = gdf.copy()
        stratum = tmp[strata_cols].fillna("MISSING").astype(str).agg("|".join, axis=1)
        counts = stratum.value_counts()
        raw_alloc = counts / counts.sum() * target
        alloc = raw_alloc.floor().astype(int)
        remainder = target - int(alloc.sum())
        if remainder > 0:
            for idx in (raw_alloc - alloc).sort_values(ascending=False).index[:remainder]:
                alloc.loc[idx] += 1
        sampled_parts = []
        for s, n in alloc.items():
            if n <= 0:
                continue
            part = tmp[stratum == s]
            sampled_parts.append(part.sample(n=min(n, len(part)), random_state=random_state))
        sampled = pd.concat(sampled_parts, axis=0) if sampled_parts else gdf.head(0)
        # If some allocations were impossible due to tiny strata, top up randomly.
        if len(sampled) < target:
            remain = gdf.drop(index=sampled.index)
            topup = remain.sample(n=target - len(sampled), random_state=random_state) if len(remain) else remain
            sampled = pd.concat([sampled, topup], axis=0)
        records.append(sampled)
    return pd.concat(records, axis=0).sample(frac=1, random_state=random_state).reset_index(drop=True)
