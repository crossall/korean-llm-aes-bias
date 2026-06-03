#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

SYSTEM_INSTRUCTION = "당신은 연구용 한국어 답안 변환기입니다. 학생 답안의 의미, 핵심 내용, 사실관계는 보존해야 합니다."

PROMPTS = {
    "extend": "아래 학생 답안을 의미와 핵심어는 유지하되 약 1.5배 길이로 자연스럽게 확장하세요. 새로운 주장이나 사실을 추가하지 마세요. 변환된 답안만 출력하세요.",
    "compress": "아래 학생 답안을 의미와 핵심어는 유지하되 약 0.7배 길이로 자연스럽게 압축하세요. 중요한 내용은 삭제하지 마세요. 변환된 답안만 출력하세요.",
    "paraphrase": "아래 학생 답안의 의미, 핵심어, 대략적인 길이를 유지하되 표현과 문장 구조만 자연스럽게 바꾸세요. 변환된 답안만 출력하세요.",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create length/paraphrase manipulation variants with Claude.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/analytic_sample.csv"))
    parser.add_argument("--out", type=Path, default=Path("data/processed/manipulated_variants.csv"))
    parser.add_argument("--condition", choices=PROMPTS.keys(), required=True)
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--grade", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model", default="claude-sonnet-4-5-20250929")
    args = parser.parse_args()

    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    df = pd.read_csv(args.input)
    df = df[df["grade_num"] == args.grade].sample(n=args.n, random_state=args.seed)

    rows = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        prompt = f"{PROMPTS[args.condition]}\n\n[학생 답안]\n{row['text']}"
        response = client.messages.create(
            model=args.model,
            max_tokens=2048,
            temperature=0,
            system=SYSTEM_INSTRUCTION,
            messages=[{"role": "user", "content": prompt}],
        )
        variant_text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text").strip()
        rows.append({
            "record_uid": row["record_uid"],
            "grade_num": row["grade_num"],
            "condition": args.condition,
            "original_text": row["text"],
            "variant_text": variant_text,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out_df = pd.DataFrame(rows)
    if args.out.exists():
        prev = pd.read_csv(args.out)
        out_df = pd.concat([prev, out_df], axis=0, ignore_index=True)
    out_df.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(rows):,} new rows to {args.out}")


if __name__ == "__main__":
    main()
