#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from korean_llm_aes.sampling import stratified_sample_by_grade


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a grade-wise stratified analytic sample.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/master_aihub_flat.csv"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/analytic_sample.csv"))
    parser.add_argument("--n-per-grade", type=int, default=1000)
    parser.add_argument("--grades", nargs="*", type=int, default=[5, 6, 7, 9])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df = df[df["grade_num"].isin(args.grades)].copy()
    df = df.dropna(subset=["text", "human_holistic_mean", "region", "gender", "subject", "format"])
    sample = stratified_sample_by_grade(df, n_per_grade=args.n_per_grade, random_state=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(sample.groupby("grade_num").size())
    print(f"Wrote {len(sample):,} rows to {args.out}")


if __name__ == "__main__":
    main()
