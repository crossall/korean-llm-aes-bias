#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from korean_llm_aes.io_aihub import flatten_aihub_json, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten nested AI Hub JSON label files into one CSV.")
    parser.add_argument("--raw", type=Path, default=Path("data/raw/archives"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/master_aihub_flat.csv"))
    parser.add_argument("--limit", type=int, default=None, help="Optional row limit for smoke testing.")
    args = parser.parse_args()

    rows = flatten_aihub_json(args.raw, limit=args.limit)
    if not rows:
        raise SystemExit("No JSON rows were parsed. Check --raw path and archive structure.")
    write_csv(rows, args.out)
    print(f"Wrote {len(rows):,} rows to {args.out}")


if __name__ == "__main__":
    main()
