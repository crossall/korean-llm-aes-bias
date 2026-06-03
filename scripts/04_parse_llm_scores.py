#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from korean_llm_aes.io_aihub import TRAITS


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert LLM JSONL score files into a wide CSV.")
    parser.add_argument("--jsonl-dir", type=Path, default=Path("results/llm_scores"))
    parser.add_argument("--out", type=Path, default=Path("results/llm_scores/llm_scores_wide.csv"))
    args = parser.parse_args()

    rows = []
    for path in sorted(args.jsonl_dir.glob("*_scores.jsonl")):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                model_key = obj["model_key"]
                row = {"record_uid": obj["record_uid"]}
                scores = obj.get("scores", {}) or {}
                for trait in TRAITS:
                    val = scores.get(trait)
                    try:
                        row[f"{model_key}_{trait}"] = int(val)
                    except Exception:
                        row[f"{model_key}_{trait}"] = None
                rows.append(row)
    if not rows:
        raise SystemExit(f"No JSONL score rows found in {args.jsonl_dir}")
    wide = pd.DataFrame(rows).groupby("record_uid", as_index=False).first()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    wide.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(wide):,} rows to {args.out}")


if __name__ == "__main__":
    main()
