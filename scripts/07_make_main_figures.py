#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Create simple publication-check figures from generated tables.")
    parser.add_argument("--tables", type=Path, default=Path("results/tables"))
    parser.add_argument("--figures", type=Path, default=Path("results/figures"))
    parser.add_argument("--models", nargs="*", default=["gpt4o", "claude_sonnet", "gemini_pro"])
    args = parser.parse_args()
    args.figures.mkdir(parents=True, exist_ok=True)

    cal = pd.read_csv(args.tables / "table_calibration_by_grade.csv")
    plt.figure(figsize=(7, 4))
    for m in args.models:
        col = f"{m}_bias"
        if col in cal.columns:
            plt.plot(cal["grade_num"], cal[col], marker="o", label=m)
    plt.axhline(0, linewidth=1)
    plt.xlabel("Grade")
    plt.ylabel("Holistic bias (LLM - human)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.figures / "fig_calibration_by_grade.png", dpi=200)
    plt.close()
    print(f"Wrote figures to {args.figures}")


if __name__ == "__main__":
    main()
