"""
Match control firms to treated firms by SIC code (industry), the
documented method chosen in Stage 3 (exact-SIC-match, simpler and more
transparent than propensity-score matching on financials we don't have
easy access to). For each treated firm, prefer a control with the
identical 4-digit SIC; fall back to the same 2-digit SIC division if no
exact match is available. Reports the match quality achieved, honestly,
rather than asserting a clean 1:1 match if reality is messier.
"""
import json
from collections import defaultdict

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"

with open(f"{DATA_DIR}/scaled_candidates.json") as f:
    cand = json.load(f)

treated = cand["treated"]
control_pool = cand["control"]

by_sic4 = defaultdict(list)
by_sic2 = defaultdict(list)
for c in control_pool:
    sic = c.get("sic") or ""
    if sic:
        by_sic4[sic].append(c)
        by_sic2[sic[:2]].append(c)

used_ciks = set()
matched_pairs = []
match_quality = {"exact_sic4": 0, "sic2_only": 0, "no_match": 0}

for t in treated:
    sic = t.get("sic") or ""
    candidates4 = [c for c in by_sic4.get(sic, []) if c["cik"] not in used_ciks]
    candidates2 = [c for c in by_sic2.get(sic[:2], []) if c["cik"] not in used_ciks]
    if candidates4:
        chosen = candidates4[0]
        used_ciks.add(chosen["cik"])
        matched_pairs.append({"treated": t, "control": chosen, "match_type": "exact_sic4"})
        match_quality["exact_sic4"] += 1
    elif candidates2:
        chosen = candidates2[0]
        used_ciks.add(chosen["cik"])
        matched_pairs.append({"treated": t, "control": chosen, "match_type": "sic2_only"})
        match_quality["sic2_only"] += 1
    else:
        matched_pairs.append({"treated": t, "control": None, "match_type": "no_match"})
        match_quality["no_match"] += 1

matched_treated = [p["treated"] for p in matched_pairs if p["control"] is not None]
matched_control = [p["control"] for p in matched_pairs if p["control"] is not None]

print("Match quality:", match_quality)
print(f"Final matched panel: {len(matched_treated)} treated, {len(matched_control)} control")

out = {"treated": matched_treated, "control": matched_control,
       "match_quality": match_quality,
       "unmatched_treated": [p["treated"]["name"] for p in matched_pairs if p["control"] is None]}
with open(f"{DATA_DIR}/matched_candidates.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"wrote matched_candidates.json")
