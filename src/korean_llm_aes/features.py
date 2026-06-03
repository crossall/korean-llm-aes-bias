from __future__ import annotations

import math
import re
from typing import Iterable, List, Sequence

import pandas as pd

_HANGUL_TOKEN_RE = re.compile(r"[가-힣A-Za-z0-9]+")


def simple_korean_tokenize(text: str | None) -> List[str]:
    """A lightweight tokenizer used as a fallback when Mecab is unavailable.

    The manuscript used Mecab morphemes for morpheme count and MATTR. For exact
    replication, install a Korean Mecab binding and replace this tokenizer with
    your institution's Mecab pipeline. This fallback is intentionally simple and
    deterministic so the repository can run in ordinary Python environments.
    """
    if not isinstance(text, str):
        return []
    return _HANGUL_TOKEN_RE.findall(text)


def mattr(tokens: Sequence[str], window: int = 50) -> float:
    """Moving-average type-token ratio."""
    if not tokens:
        return math.nan
    if len(tokens) <= window:
        return len(set(tokens)) / len(tokens)
    ratios = []
    for i in range(0, len(tokens) - window + 1):
        w = tokens[i : i + window]
        ratios.append(len(set(w)) / window)
    return float(sum(ratios) / len(ratios)) if ratios else math.nan


def keyword_density(text: str | None, keyword_string: str | None) -> float:
    if not isinstance(text, str) or not isinstance(keyword_string, str):
        return math.nan
    keywords = [k.strip() for k in re.split(r"[,/;·]+", keyword_string) if k.strip()]
    if not keywords:
        return 0.0
    tokens = simple_korean_tokenize(text)
    denom = max(len(tokens), 1)
    count = 0
    for kw in keywords:
        count += text.count(kw)
    return count / denom


def add_surface_features(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    out = df.copy()
    tokens = out[text_col].fillna("").map(simple_korean_tokenize)
    out["token_count_simple"] = tokens.map(len)
    out["log_token_count_simple"] = out["token_count_simple"].map(lambda x: math.log1p(x))
    out["mattr_simple_w50"] = tokens.map(lambda t: mattr(t, window=50))
    if "keyword" in out.columns:
        out["keyword_density_simple"] = [keyword_density(t, k) for t, k in zip(out[text_col], out["keyword"])]
    return out
