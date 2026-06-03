# Raw data placement

Place the four AI Hub outer archives here:

```text
data/raw/archives/
├── 초5(2).zip
├── 초6 전체(2).zip
├── 중1(2).zip
└── 중3(2).zip
```

The repository is configured to ignore `data/raw/archives/*.zip` by default. This is intentional.
The source dataset contains student writing responses and is governed by the original data provider's terms.
Do not push the raw archives to a public GitHub repository unless the data license explicitly allows redistribution.

A checksum manifest for the files used when this repository was prepared is in:

```text
metadata/uploaded_raw_archives_manifest.csv
```

Run this check after placing the files:

```bash
PYTHONPATH=src python scripts/00_check_raw_archives.py --raw data/raw/archives
```
