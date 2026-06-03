#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from korean_llm_aes.llm_clients import LLMConfig, call_llm
from korean_llm_aes.scoring_prompt import build_scoring_prompt

DEFAULT_MODELS = {
    "gpt4o": {"provider": "openai", "model": "gpt-4o-2024-11-20"},
    "claude_sonnet": {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"},
    "gemini_pro": {"provider": "google", "model": "gemini-2.5-pro"},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Score analytic sample with an LLM and write JSONL results.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/analytic_sample.csv"))
    parser.add_argument("--model-key", choices=DEFAULT_MODELS.keys(), required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    load_dotenv()
    m = DEFAULT_MODELS[args.model_key]
    cfg = LLMConfig(
        provider=m["provider"],
        model=m["model"],
        temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "5")),
        sleep_seconds=float(os.getenv("LLM_SLEEP_SECONDS", "0.5")),
    )
    out_path = args.out or Path(f"results/llm_scores/{args.model_key}_scores.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.input)
    if args.limit is not None:
        df = df.iloc[args.start : args.start + args.limit]
    else:
        df = df.iloc[args.start :]

    completed = set()
    if out_path.exists():
        with out_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    completed.add(json.loads(line)["record_uid"])

    with out_path.open("a", encoding="utf-8") as f:
        for _, row in tqdm(df.iterrows(), total=len(df)):
            record_uid = row["record_uid"]
            if record_uid in completed:
                continue
            prompt = build_scoring_prompt(row.to_dict())
            scores = call_llm(prompt, cfg)
            payload = {
                "record_uid": record_uid,
                "model_key": args.model_key,
                "provider": cfg.provider,
                "model": cfg.model,
                "scores": scores,
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            f.flush()
    print(f"Wrote/resumed {out_path}")


if __name__ == "__main__":
    main()
