# Gatekeeping Under Mandate

Data and code for *Gatekeeping Under Mandate: Elite Network Restructuring, Compliance, and Rollback in Corporate Governance* (Shaurya Gupta, manuscript under review, Journal of Computational Social Science).

## Overview

This project tests whether California's board-gender-diversity mandate (SB 826, 2018) produced a detectable change in board-interlock network structure (density, degree centralization) among California-headquartered public companies, relative to a matched control group, both during the compliance period (2018-2021) and after the mandate's enforcement was enjoined in December 2022. The central result is a well-documented null: no statistically significant differential change in network topology at either point, reported alongside an explicit discussion of the sample's statistical power.

## Repository structure

```
docs/       research design, literature review, novelty audit, project log, KPI tracking, manuscript draft
src/        full pipeline: SEC EDGAR retrieval, entity resolution, network construction, statistics, figures
workflows/  LLM-assisted director-name extraction workflow (batch orchestration script)
figures/    generated figures used in the manuscript
data/       intermediate and final derived datasets (raw SEC filings excluded -- see below)
```

## Reproducing the pipeline

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 src/find_candidates.py          # pilot: verify a hand-picked CA firm list against EDGAR
python3 src/fetch_filings.py            # pilot: fetch DEF 14A filings
python3 src/scale_discovery2.py         # scaled: discover matched treated/control panel via EDGAR
python3 src/match_controls.py           # SIC-code matching
python3 src/fetch_filings_scaled.py     # fetch all 576 filings for the matched panel
python3 src/extract_windows_scaled.py   # locate director-section text windows
# director extraction over the located windows uses an LLM-agent workflow
# (workflows/extract_directors_llm.js); see docs/PROJECT_LOG.md for the exact run history
python3 src/build_clean_directors.py    # assemble the clean, extraction-confidence-filtered panel
python3 src/network_metrics.py          # build networks, compute density/centralization
python3 src/stage7_statistics.py        # firm-level DiD + bootstrap network-topology inference
python3 src/stage8_robustness.py        # robustness checks
python3 src/make_figures.py             # regenerate figures/*.png
```

## Data availability

Raw SEC EDGAR filings (628 documents, ~850MB) are excluded from this repository for size, not availability. They are public U.S. government records with no access restriction, and are fully re-fetchable by re-running `src/fetch_filings_scaled.py` against the accession numbers already logged in `data/scaled_fetch_manifest.json` and `data/matched_candidates.json`. All derived datasets (extracted director lists, network metrics, statistical results) used to produce the manuscript's reported numbers are included in `data/` as-is.

## Methodology note

The data-retrieval, entity-resolution, and statistical-analysis code in this repository, and an initial draft of the manuscript, were developed with the assistance of an LLM (Claude, Anthropic) under the author's direction; specific autonomous methodological choices made during execution are documented in the commit history and in `docs/PROJECT_LOG.md`. See the manuscript's Methods section for the full disclosure statement required by the target journal's authorship policy.

## Citation

If you use this code or data, please cite the manuscript (full citation to be added upon publication).

## License

Code in this repository is released under the MIT License (see `LICENSE`). Data derived from SEC EDGAR filings is drawn from U.S. public records with no copyright restriction.

## Contact

Shaurya Gupta — shauryaguptaa8@gmail.com
