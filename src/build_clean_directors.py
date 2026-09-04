"""
Combine LLM-assisted extraction results (from workflows/extract_directors_llm.js,
run over data/director_windows_scaled.json) with the fetch manifest into the
final data/clean_directors.json consumed by network_metrics.py and
stage7_statistics.py. Reports the real extraction-yield rate -- a first-
class result, not hidden -- rather than silently dropping failed docs.
"""
import json

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"

with open(f"{DATA_DIR}/scaled_fetch_manifest.json") as f:
    manifest = json.load(f)

with open(f"{DATA_DIR}/llm_extraction_results.json") as f:
    extraction = json.load(f)  # list of {doc_id, directors, confidence, note}

extraction_by_id = {e["doc_id"]: e for e in extraction}

clean = {"treated": {"pre": {}, "post": {}, "post2": {}},
         "control": {"pre": {}, "post": {}, "post2": {}}}

n_total = 0
n_high_or_medium = 0
n_low = 0
n_none = 0
n_missing_from_extraction = 0

for firm in manifest:
    group = firm["group"]
    for tag in ["pre", "post", "post2"]:
        info = firm[tag]
        if info["status"] != 200:
            continue
        doc_id = f"{group}_{firm['cik']}_{tag}"
        n_total += 1
        e = extraction_by_id.get(doc_id)
        if e is None:
            n_missing_from_extraction += 1
            continue
        conf = e.get("confidence")
        directors = e.get("directors", [])
        if conf in ("high", "medium") and len(directors) >= 3:
            clean[group][tag][firm["name"]] = directors
            n_high_or_medium += 1
        elif conf == "low":
            n_low += 1  # not included in the clean panel -- too uncertain
        else:
            n_none += 1

print(f"Extraction yield summary:")
print(f"  total documents fetched successfully: {n_total}")
print(f"  clean (high/medium confidence, >=3 directors) included: {n_high_or_medium} "
      f"({n_high_or_medium/n_total*100:.1f}%)")
print(f"  low-confidence, excluded from clean panel: {n_low}")
print(f"  none_found: {n_none}")
print(f"  missing from LLM extraction output entirely: {n_missing_from_extraction}")

for group in ["treated", "control"]:
    for tag in ["pre", "post", "post2"]:
        print(f"  {group}/{tag}: {len(clean[group][tag])} firms with clean director lists")

with open(f"{DATA_DIR}/clean_directors.json", "w") as f:
    json.dump(clean, f, indent=2)
print(f"\nwrote clean_directors.json")

# Also keep ONLY firms present in ALL THREE snapshots per group, since that's
# what the panel-based analyses (turnover, DiD) need -- report how much this
# further restricts the sample, honestly.
for group in ["treated", "control"]:
    common_firms = set(clean[group]["pre"]) & set(clean[group]["post"]) & set(clean[group]["post2"])
    print(f"  {group}: {len(common_firms)} firms with CLEAN data in all 3 snapshots "
          f"(this is the true usable panel size for DiD/turnover analysis)")
