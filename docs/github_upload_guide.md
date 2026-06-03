# GitHub upload guide

## Recommended public repository structure

Upload the code, configuration, documentation, and manuscript. Do not upload raw student response archives unless the original data license permits redistribution.

Recommended command-line workflow:

```bash
git init
git add README.md LICENSE CITATION.cff pyproject.toml requirements.txt .gitignore .env.example
git add src scripts configs docs tests metadata data/raw/README.md data/raw/archives/.gitkeep data/processed/.gitkeep results notebooks
git commit -m "Initial release for Korean LLM-AES bias analysis"
git branch -M main
git remote add origin https://github.com/<your-id>/korean-llm-aes.git
git push -u origin main
```

## If you must share data

Use one of the following instead of committing raw archives directly:

1. Cite the AI Hub dataset page and tell users to download it themselves.
2. Upload a non-sensitive derived metadata table only.
3. Use a private OSF/Zenodo/GitHub Release if the license allows it.
4. If using GitHub for large files, use Git LFS and keep the repository private unless redistribution is allowed.

## Before making the repository public

- Confirm that AI Hub terms allow redistribution.
- Confirm that student response data does not contain personally identifiable information.
- Remove `.env` and API keys.
- Keep `results/llm_scores/*.jsonl` private if they contain full student responses or prompts.
