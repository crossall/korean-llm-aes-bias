#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from korean_llm_aes.io_aihub import inspect_outer_archive, list_outer_archives


def main() -> None:
    parser = argparse.ArgumentParser(description="Check raw AI Hub outer archives and write a manifest.")
    parser.add_argument("--raw", type=Path, default=Path("data/raw/archives"))
    parser.add_argument("--out", type=Path, default=Path("metadata/raw_archives_manifest.csv"))
    args = parser.parse_args()

    archives = list_outer_archives(args.raw)
    if not archives:
        raise SystemExit(f"No zip archives found in {args.raw}")

    rows = []
    for path in archives:
        info = inspect_outer_archive(path)
        info["duplicate_entries_json"] = json.dumps(info.pop("duplicate_entries"), ensure_ascii=False)
        rows.append(info)
        print(f"{path.name}: {info['entry_count']} entries, {info['duplicate_entry_count']} duplicate-name entries")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
