from __future__ import annotations

from typing import Dict, List

from .io_aihub import ANALYTIC_TRAITS, TRAITS


def build_rubric_block(row: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append(f"과제: {row.get('prompt', '')}")
    lines.append(f"교과: {row.get('subject', '')} / 학년: {row.get('grade', '')} / 유형: {row.get('format', '')}")
    if row.get("keyword"):
        lines.append(f"핵심어: {row.get('keyword')}")
    lines.append("\n[분석적 채점 기준]")
    for trait in ANALYTIC_TRAITS:
        name = row.get(f"rubric_{trait}_name") or trait
        lines.append(f"\n- {trait} ({name})")
        for score in range(5, 0, -1):
            val = row.get(f"rubric_{trait}_evaluation_{score}")
            if val:
                lines.append(f"  {score}점: {val}")
    return "\n".join(lines)


def build_scoring_prompt(row: Dict[str, object]) -> str:
    rubric = build_rubric_block(row)
    text = row.get("text", "")
    return f"""
당신은 한국어 서·논술형 학생 답안을 채점하는 평가자입니다.
아래 지시문, 채점 기준, 학생 답안을 바탕으로 점수를 부여하세요.

중요 원칙:
1. 학생 답안에 명시된 내용만 근거로 채점합니다.
2. 답안 길이, 문체의 세련됨, 문장 수만으로 가산하지 않습니다.
3. 각 분석 기준은 1~5점 정수로, holistic은 1~4점 정수로 채점합니다.
4. 반드시 JSON만 출력합니다. 설명 문장이나 Markdown을 출력하지 않습니다.

{rubric}

[학생 답안]
{text}

[출력 JSON 형식]
{{
  "holistic": 1,
  "task_1": 1,
  "content_1": 1,
  "content_2": 1,
  "content_3": 1,
  "organization_1": 1,
  "organization_2": 1,
  "expression_1": 1,
  "expression_2": 1
}}
""".strip()
