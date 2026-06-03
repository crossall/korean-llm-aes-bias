# Reproducibility notes

## Main design implemented in this repository

The pipeline is designed for a cross-grade Korean LLM-AES analysis with four grades:

- Grade 5: 초5
- Grade 6: 초6
- Grade 7: 중1
- Grade 9: 중3

The target sampling design uses stratified random sampling by region, sex/gender, subject, and format, with about 1,000 responses per grade.

## Model settings

The manuscript's scoring procedure is represented in `configs/models.yaml` and `scripts/03_score_with_llms.py`:

| Key | Provider | Model ID | Temperature |
|---|---|---|---|
| `gpt4o` | OpenAI | `gpt-4o-2024-11-20` | 0 |
| `claude_sonnet` | Anthropic | `claude-sonnet-4-5-20250929` | 0 |
| `gemini_pro` | Google | `gemini-2.5-pro` | 0 |

The script writes raw model outputs to JSONL so that interrupted API runs can resume.

## Exact replication caution

This repository includes a lightweight fallback tokenizer for surface features. The manuscript reports Mecab-based morpheme count and MATTR. For exact replication of Korean morpheme features, replace `simple_korean_tokenize()` in `src/korean_llm_aes/features.py` with the same Mecab configuration used in the original analysis environment.

## What can be reproduced from this repository

1. Raw AI Hub nested JSON flattening.
2. Grade-wise stratified analytic sampling.
3. LLM scoring prompts and API scoring workflow.
4. Calibration, bias, central tendency, QWK, and length-bias tables.
5. Length-manipulation/paraphrase experiment scaffolding.

The final numerical values in the manuscript require the same raw files, same random seed/sample, same LLM model versions, and successful API scoring for all selected cases.
