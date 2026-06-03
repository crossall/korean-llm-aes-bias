from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional

TRAITS = [
    "holistic",
    "task_1",
    "content_1",
    "content_2",
    "content_3",
    "organization_1",
    "organization_2",
    "expression_1",
    "expression_2",
]

ANALYTIC_TRAITS = [t for t in TRAITS if t != "holistic"]

GRADE_TO_NUM = {"초5": 5, "초6": 6, "중1": 7, "중3": 9, "중2": 8}
SUBJECT_TO_CODE = {"국어": "kor", "사회": "soc", "과학": "sci", "수학": "math"}


@dataclass(frozen=True)
class NestedFile:
    outer_zip: str
    outer_index: int
    inner_zip: str
    inner_index: int
    inner_path: str
    split: str
    payload: bytes


def decode_zip_name(name: str) -> str:
    """Decode zip names that may have been written in CP949 but read as CP437.

    Korean AI Hub archives sometimes display mojibake such as '├╩5'. This function
    attempts CP437 -> CP949 recovery while leaving normal Unicode names unchanged.
    """
    try:
        recovered = name.encode("cp437").decode("cp949")
        # Prefer recovered names if they contain Hangul or if the original looks mojibake.
        if re.search(r"[가-힣]", recovered) or re.search(r"[╩├░╟]", name):
            return recovered
    except Exception:
        pass
    return name


def sha256_file(path: Path, block_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(block_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def split_from_archive_name(name: str) -> str:
    base = Path(name).name
    if base.startswith("TL_"):
        return "train_label"
    if base.startswith("VL_"):
        return "valid_label"
    if base.startswith("TS_"):
        return "train_source"
    if base.startswith("VS_"):
        return "valid_source"
    return "unknown"


def list_outer_archives(raw_dir: Path) -> List[Path]:
    return sorted(Path(raw_dir).glob("*.zip"))


def inspect_outer_archive(path: Path) -> Dict[str, Any]:
    with zipfile.ZipFile(path) as z:
        names = [decode_zip_name(i.filename) for i in z.infolist() if not i.is_dir()]
    counts = Counter(names)
    duplicate_entries = {k: v for k, v in counts.items() if v > 1}
    return {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "entry_count": len(names),
        "unique_entry_count": len(counts),
        "duplicate_entry_count": sum(v - 1 for v in counts.values() if v > 1),
        "duplicate_entries": duplicate_entries,
    }


def iter_nested_files(
    raw_dir: Path,
    extensions: tuple[str, ...] = (".json",),
    label_only: bool = True,
) -> Iterator[NestedFile]:
    """Yield files from nested AI Hub archives without extracting to disk.

    Parameters
    ----------
    raw_dir:
        Directory containing outer grade archives such as '초5(2).zip'.
    extensions:
        Inner file extensions to yield.
    label_only:
        When True, process only TL/VL archives, because JSON label files contain
        response text, scores, feedback, and rubrics.
    """
    for outer in list_outer_archives(raw_dir):
        with zipfile.ZipFile(outer) as oz:
            for outer_index, outer_info in enumerate(oz.infolist()):
                if outer_info.is_dir():
                    continue
                inner_name = decode_zip_name(outer_info.filename).lstrip("/")
                split = split_from_archive_name(inner_name)
                if label_only and split not in {"train_label", "valid_label"}:
                    continue
                if not inner_name.lower().endswith(".zip"):
                    continue
                inner_bytes = oz.read(outer_info)
                try:
                    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as iz:
                        for inner_index, inner_info in enumerate(iz.infolist()):
                            if inner_info.is_dir():
                                continue
                            inner_path = decode_zip_name(inner_info.filename).lstrip("/")
                            if not inner_path.lower().endswith(extensions):
                                continue
                            yield NestedFile(
                                outer_zip=outer.name,
                                outer_index=outer_index,
                                inner_zip=inner_name,
                                inner_index=inner_index,
                                inner_path=inner_path,
                                split=split,
                                payload=iz.read(inner_info),
                            )
                except zipfile.BadZipFile as exc:
                    raise RuntimeError(f"Nested archive could not be opened: {outer}::{inner_name}") from exc


def safe_get(d: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def score_pair_to_columns(value: Any) -> tuple[Optional[float], Optional[float], Optional[float]]:
    if isinstance(value, list) and len(value) >= 2:
        try:
            s1 = float(value[0]) if value[0] is not None else None
            s2 = float(value[1]) if value[1] is not None else None
            mean = (s1 + s2) / 2 if s1 is not None and s2 is not None else None
            return s1, s2, mean
        except Exception:
            return None, None, None
    return None, None, None


def normalize_format(question_type: str | None, rubric_type: str | None) -> str:
    text = " ".join(x for x in [question_type, rubric_type] if x)
    if "논술" in text:
        return "essay"
    if "서술" in text:
        return "descriptive"
    return "unknown"


def parse_json_record(obj: Dict[str, Any], src: NestedFile) -> Dict[str, Any]:
    q = obj.get("essay_question", {}) or {}
    a = obj.get("essay_answer", {}) or {}
    rubric = obj.get("rubric", {}) or {}
    personal = safe_get(obj, "score", "personal", default={}) or {}

    grade = q.get("grade") or a.get("grade")
    subject = q.get("subject") or rubric.get("subject")
    row: Dict[str, Any] = {
        "record_uid": f"{src.outer_zip}::{src.outer_index}::{src.inner_zip}::{src.inner_index}::{src.inner_path}",
        "outer_zip": src.outer_zip,
        "outer_index": src.outer_index,
        "inner_zip": src.inner_zip,
        "inner_index": src.inner_index,
        "inner_path": src.inner_path,
        "split": src.split,
        "question_id": q.get("id"),
        "answer_id": a.get("id"),
        "grade": grade,
        "grade_num": GRADE_TO_NUM.get(str(grade)),
        "subject": subject,
        "subject_code": SUBJECT_TO_CODE.get(str(subject)),
        "topic": q.get("topic"),
        "level": q.get("level"),
        "question_type": q.get("type"),
        "format": normalize_format(q.get("type"), rubric.get("type")),
        "prompt": q.get("prompt"),
        "keyword": q.get("keyword"),
        "question_len_syllable": q.get("len_syllable"),
        "question_len_word": q.get("len_word"),
        "region": a.get("region"),
        "gender": a.get("gender"),
        "reference": a.get("reference"),
        "text": a.get("text"),
        "answer_len_syllable": a.get("len_syllable"),
        "answer_len_word": a.get("len_word"),
        "rubric_type": rubric.get("type"),
        "rubric_purpose": rubric.get("purpose"),
        "rubric_achievement": rubric.get("achievement"),
    }

    for trait in TRAITS:
        if trait == "holistic":
            trait_obj = personal.get("holistic", {}) or {}
        else:
            trait_obj = safe_get(personal, "analytic", trait, default={}) or {}
        s1, s2, mean = score_pair_to_columns(trait_obj.get("score"))
        row[f"human_{trait}_rater1"] = s1
        row[f"human_{trait}_rater2"] = s2
        row[f"human_{trait}_mean"] = mean
        row[f"human_{trait}_feedback"] = trait_obj.get("feedback")
        if trait != "holistic":
            row[f"{trait}_rubric_key"] = trait_obj.get("rubric_key")

    # Flatten rubric text for prompting and reproducibility.
    analytic_rubric = rubric.get("analytic", {}) or {}
    for trait in ANALYTIC_TRAITS:
        trait_r = analytic_rubric.get(trait, {}) or {}
        row[f"rubric_{trait}_name"] = trait_r.get("name")
        for score in range(1, 6):
            row[f"rubric_{trait}_evaluation_{score}"] = trait_r.get(f"evaluation_{score}")

    return row


def flatten_aihub_json(raw_dir: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for i, nested in enumerate(iter_nested_files(raw_dir, extensions=(".json",), label_only=True)):
        if limit is not None and i >= limit:
            break
        try:
            obj = json.loads(nested.payload.decode("utf-8-sig"))
        except UnicodeDecodeError:
            obj = json.loads(nested.payload.decode("cp949"))
        rows.append(parse_json_record(obj, nested))
    return rows


def write_csv(rows: List[Dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No rows to write.")
    fieldnames: List[str] = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
