#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from korean_llm_aes.analysis import add_bias_columns, calibration_table, central_tendency_table, qwk_table
from korean_llm_aes.features import add_surface_features


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge human and LLM scores and create main result tables.")
    parser.add_argument("--sample", type=Path, default=Path("data/processed/analytic_sample.csv"))
    parser.add_argument("--llm", type=Path, default=Path("results/llm_scores/llm_scores_wide.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/tables"))
    parser.add_argument("--models", nargs="*", default=["gpt4o", "claude_sonnet", "gemini_pro"])
    args = parser.parse_args()

    sample = pd.read_csv(args.sample)
    llm = pd.read_csv(args.llm)
    df = sample.merge(llm, on="record_uid", how="inner")
    df = add_surface_features(df)
    df = add_bias_columns(df, args.models)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_dir / "analysis_dataset.csv", index=False, encoding="utf-8-sig")
    calibration_table(df, args.models).to_csv(args.out_dir / "table_calibration_by_grade.csv", index=False, encoding="utf-8-sig")
    central_tendency_table(df, args.models).to_csv(args.out_dir / "table_central_tendency.csv", index=False, encoding="utf-8-sig")
    qwk_table(df, args.models).to_csv(args.out_dir / "table_qwk.csv", index=False, encoding="utf-8-sig")

    corr_rows = []
    for grade, g in df.groupby("grade_num"):
        for m in args.models:
            bias_col = f"{m}_holistic_bias"
            if bias_col in g.columns:
                corr_rows.append({
                    "grade_num": grade,
                    "model": m,
                    "corr_log_length_bias_simple": g["log_token_count_simple"].corr(g[bias_col]),
                })
    pd.DataFrame(corr_rows).to_csv(args.out_dir / "table_length_bias_correlation.csv", index=False, encoding="utf-8-sig")
    print(f"Merged N={len(df):,}. Wrote tables to {args.out_dir}")


if __name__ == "__main__":
    main()
