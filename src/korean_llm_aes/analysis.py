from __future__ import annotations

from typing import Iterable, List

import numpy as np
import pandas as pd

from .metrics import quadratic_weighted_kappa


def add_bias_columns(df: pd.DataFrame, model_prefixes: Iterable[str], human_col: str = "human_holistic_mean") -> pd.DataFrame:
    out = df.copy()
    for m in model_prefixes:
        score_col = f"{m}_holistic"
        if score_col in out.columns:
            out[f"{m}_holistic_bias"] = out[score_col] - out[human_col]
    return out


def calibration_table(df: pd.DataFrame, model_prefixes: List[str], grade_col: str = "grade_num") -> pd.DataFrame:
    rows = []
    for grade, g in df.groupby(grade_col):
        row = {"grade_num": grade, "n": len(g), "human_mean": g["human_holistic_mean"].mean()}
        for m in model_prefixes:
            if f"{m}_holistic" in g.columns:
                row[f"{m}_mean"] = g[f"{m}_holistic"].mean()
                row[f"{m}_bias"] = g[f"{m}_holistic"].mean() - g["human_holistic_mean"].mean()
        rows.append(row)
    return pd.DataFrame(rows).sort_values("grade_num")


def score_level(x: float) -> str:
    if pd.isna(x):
        return "missing"
    if x <= 2:
        return "Low"
    if x <= 3.5:
        return "Mid"
    return "High"


def central_tendency_table(df: pd.DataFrame, model_prefixes: List[str]) -> pd.DataFrame:
    work = df.copy()
    work["human_score_level"] = work["human_holistic_mean"].map(score_level)
    rows = []
    for (grade, level), g in work.groupby(["grade_num", "human_score_level"]):
        row = {"grade_num": grade, "level": level, "n": len(g)}
        for m in model_prefixes:
            bias_col = f"{m}_holistic_bias"
            if bias_col in g.columns:
                row[f"{m}_bias"] = g[bias_col].mean()
        rows.append(row)
    order = {"Low": 0, "Mid": 1, "High": 2, "missing": 3}
    out = pd.DataFrame(rows)
    if len(out):
        out["level_order"] = out["level"].map(order)
        out = out.sort_values(["grade_num", "level_order"]).drop(columns=["level_order"])
    return out


def qwk_table(df: pd.DataFrame, model_prefixes: List[str]) -> pd.DataFrame:
    pairs = []
    for grade, g in df.groupby("grade_num"):
        pairs.append({
            "grade_num": grade,
            "pair": "Human1-Human2",
            "qwk": quadratic_weighted_kappa(g["human_holistic_rater1"], g["human_holistic_rater2"], 1, 4),
        })
        for m in model_prefixes:
            col = f"{m}_holistic"
            if col in g.columns:
                pairs.append({
                    "grade_num": grade,
                    "pair": f"HumanMean-{m}",
                    "qwk": quadratic_weighted_kappa(np.rint(g["human_holistic_mean"]), g[col], 1, 4),
                })
        for i, m1 in enumerate(model_prefixes):
            for m2 in model_prefixes[i + 1 :]:
                c1, c2 = f"{m1}_holistic", f"{m2}_holistic"
                if c1 in g.columns and c2 in g.columns:
                    pairs.append({
                        "grade_num": grade,
                        "pair": f"{m1}-{m2}",
                        "qwk": quadratic_weighted_kappa(g[c1], g[c2], 1, 4),
                    })
    return pd.DataFrame(pairs)
