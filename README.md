# Korean LLM-AES Bias Analysis Repository

이 저장소는 다음 논문의 분석 재현과 후속 연구를 위한 GitHub용 repository입니다.

> **Robust Biases and Grade-Level Drift in LLM-Based Korean Essay Scoring: A Cross-Grade Multi-Method Comparison of GPT-4o, Claude Sonnet, and Gemini Pro across Four School Grades**

## 1. 연구 개요

본 연구는 AI Hub 한국어 글쓰기 자동 평가 데이터셋을 바탕으로 초5, 초6, 중1, 중3 학생 응답을 분석하고, GPT-4o, Claude Sonnet, Gemini Pro의 한국어 서·논술형 자동채점 편향을 비교합니다.

주요 분석 축은 다음과 같습니다.

1. 학년별 LLM 채점 보정(calibration) 및 과소/과대 채점 편향
2. 인간 점수 수준별 중앙화 경향성(central tendency bias)
3. 응답 길이, 어휘 다양도, 핵심어 밀도 등 표면 변인과 편향의 관계
4. LLM 간 일치도와 인간-LLM 일치도 비교(QWK)
5. 길이 확장/압축 및 paraphrase-only 통제 실험

## 2. 저장소 구조

```text
korean-llm-aes/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── configs/
│   ├── models.yaml
│   └── traits.yaml
├── data/
│   ├── raw/
│   │   ├── README.md
│   │   └── archives/          # 원자료 ZIP 배치 위치, Git 기본 제외
│   └── processed/             # flatten/sample 결과, Git 기본 제외
├── docs/
│   ├── data_schema.md
│   ├── github_upload_guide.md
│   ├── reproducibility.md
│   └── manuscript/
├── metadata/
│   └── uploaded_raw_archives_manifest.csv
├── results/
│   ├── llm_scores/            # API 채점 결과 JSONL/CSV, Git 기본 제외
│   ├── tables/                # 분석표 CSV, Git 기본 제외
│   └── figures/               # 그림 파일, Git 기본 제외
├── scripts/
│   ├── 00_check_raw_archives.py
│   ├── 01_flatten_aihub_json.py
│   ├── 02_make_stratified_sample.py
│   ├── 03_score_with_llms.py
│   ├── 04_parse_llm_scores.py
│   ├── 05_merge_and_analyze.py
│   ├── 06_length_manipulation_experiment.py
│   └── 07_make_main_figures.py
├── src/korean_llm_aes/
└── tests/
```

## 3. 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

개발 모드로 패키지를 설치하려면 다음을 실행합니다.

```bash
pip install -e .
```

## 4. 원자료 배치

원자료 ZIP 파일을 다음 위치에 넣습니다.

```text
data/raw/archives/
├── 초5(2).zip
├── 초6 전체(2).zip
├── 중1(2).zip
└── 중3(2).zip
```

> 주의: `data/raw/archives/*.zip`은 `.gitignore`에 의해 Git에 올라가지 않도록 설정되어 있습니다. 학생 응답 원문과 AI Hub 원자료는 원 제공기관의 이용약관과 라이선스로 인해 해당 repository에 저장되어있지 않습니다.
> aihub에서 다운로드 받으세요.
원자료가 제대로 들어갔는지 확인합니다.

```bash
PYTHONPATH=src python scripts/00_check_raw_archives.py --raw data/raw/archives
```

## 5. 데이터 전처리

### 5.1 AI Hub 중첩 ZIP/JSON flatten

```bash
PYTHONPATH=src python scripts/01_flatten_aihub_json.py \
  --raw data/raw/archives \
  --out data/processed/master_aihub_flat.csv
```

빠른 테스트만 하려면 다음처럼 일부만 파싱합니다.

```bash
PYTHONPATH=src python scripts/01_flatten_aihub_json.py \
  --raw data/raw/archives \
  --out data/processed/master_aihub_flat_smoke.csv \
  --limit 100
```

### 5.2 학년별 층화 표본 생성

```bash
PYTHONPATH=src python scripts/02_make_stratified_sample.py \
  --input data/processed/master_aihub_flat.csv \
  --out data/processed/analytic_sample.csv \
  --n-per-grade 1000 \
  --grades 5 6 7 9 \
  --seed 42
```

층화 기준은 `region`, `gender`, `subject`, `format`입니다.

## 6. LLM 채점 실행

`.env.example`을 `.env`로 복사한 뒤 API 키를 입력합니다.

```bash
cp .env.example .env
```

각 모델별 실행 예시는 다음과 같습니다.

```bash
PYTHONPATH=src python scripts/03_score_with_llms.py --model-key gpt4o
PYTHONPATH=src python scripts/03_score_with_llms.py --model-key claude_sonnet
PYTHONPATH=src python scripts/03_score_with_llms.py --model-key gemini_pro
```

기본 모델 ID는 `configs/models.yaml`과 동일합니다.

| Key | Provider | Model ID | Temperature |
|---|---|---|---|
| `gpt4o` | OpenAI | `gpt-4o-2024-11-20` | 0 |
| `claude_sonnet` | Anthropic | `claude-sonnet-4-5-20250929` | 0 |
| `gemini_pro` | Google | `gemini-2.5-pro` | 0 |

API 실행이 중간에 끊겨도 JSONL 파일을 기준으로 resume됩니다.

## 7. 분석표 생성

LLM JSONL 결과를 wide CSV로 변환합니다.

```bash
PYTHONPATH=src python scripts/04_parse_llm_scores.py
```

인간 점수와 LLM 점수를 병합하고 주요 표를 생성합니다.

```bash
PYTHONPATH=src python scripts/05_merge_and_analyze.py
```

생성되는 주요 파일은 다음과 같습니다.

```text
results/tables/analysis_dataset.csv
results/tables/table_calibration_by_grade.csv
results/tables/table_central_tendency.csv
results/tables/table_qwk.csv
results/tables/table_length_bias_correlation.csv
```

그림을 생성하려면 다음을 실행합니다.

```bash
PYTHONPATH=src python scripts/07_make_main_figures.py
```

## 8. 길이 조작 및 paraphrase-only 실험

예: 초5 답안 100개를 확장 조건으로 변환합니다.

```bash
PYTHONPATH=src python scripts/06_length_manipulation_experiment.py \
  --condition extend \
  --grade 5 \
  --n 100
```

지원 조건은 다음과 같습니다.

- `extend`: 의미 보존, 약 1.5배 확장
- `compress`: 의미 보존, 약 0.7배 압축
- `paraphrase`: 의미와 길이 보존, 표현만 수정

생성된 변형 답안은 동일한 scoring pipeline에 넣어 재채점한 뒤 paired t-test 등으로 분석할 수 있습니다.

## 9. 재현성 관련 주의점

1. 논문은 Mecab 기반 형태소 수와 MATTR을 사용했습니다. 이 저장소의 기본 tokenizer는 실행 편의를 위한 fallback입니다. 엄밀 재현이 필요하면 `src/korean_llm_aes/features.py`의 tokenizer를 동일한 Mecab 환경으로 교체하세요.
2. API 모델은 시간이 지나면 제공사의 동작이 변경될 수 있습니다. 결과 재현을 위해 모델 ID, 실행일, temperature, prompt, raw JSONL 출력을 보관하세요.
3. 원자료 ZIP 내부에는 동일한 이름의 중첩 ZIP 항목이 포함될 수 있습니다. 본 repository의 파싱 코드는 `outer_index`, `inner_index`, `record_uid`를 이용하여 중복 이름 항목을 덮어쓰지 않도록 설계했습니다.
4. 원자료와 LLM 채점 결과는 학생 응답 원문을 포함할 수 있으므로 공개 GitHub에 올리지 않는 것을 기본값으로 했습니다.

## 10. 테스트

```bash
PYTHONPATH=src pytest -q
```

## 11. 라이선스

- AI Hub 원자료, 학생 답안, 루브릭, 제3자 자료: 원 제공기관의 라이선스와 이용약관 적용



## Data Availability and License Notice

This repository provides code and documentation for reproducing the analyses reported in the paper.

The original student writing data used in this study were obtained from the AI Hub Korean writing assessment dataset. Due to AI Hub’s data-use terms and redistribution restrictions, the raw data files are **not included** in this repository.

Researchers who wish to reproduce the analysis should obtain the dataset directly from AI Hub after agreeing to the applicable terms of use, and then place the downloaded files in the following directory:

```text
data/raw/archives/
```

Expected raw data archive structure:

```text
data/raw/archives/
├── 초5.zip
├── 초6 전체.zip
├── 중1.zip
└── 중3.zip
```

The scripts in this repository assume that the raw AI Hub data are provided locally by the user. The repository does not redistribute, sublicense, or publicly share any original AI Hub data, student responses, or derived files that may contain student-written text.

Only analysis code, configuration files, documentation, and non-identifiable summary outputs are intended to be shared through this repository.

