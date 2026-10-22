# Changelog

Versions follow [Semantic Versioning](https://semver.org/): a new major version renames or removes columns.

## [1.0.0] - 2026-10-22

### Added
- 63,974 stores, their Reclame Aqui profiles (19,335) and search candidates (217,507), 63,933 GPT-3.5 pages, the 2022 census (81,018 domains, 20,284 feeds) and 13,804 imported feeds (Parquet on Kaggle; a sample of 500 stores in CSV here).
- Export, profile and build scripts; validation of the sample in GitHub Actions.
- Data dictionary (EN, PT), methodology, data quality report, figures, exploratory notebook, Kaggle metadata.

### Changed (relative to the author's database)
- Only stores with a confirmed name; platform spellings unified; store names fixed (HTML entities, mojibake); certificate issuer cleaned; GPT pages linked to stores; partners, contact lists, WHOIS, Reclame Aqui documents and author tags not exported; company names of individual micro-entrepreneurs (MEI) on Reclame Aqui emptied.
