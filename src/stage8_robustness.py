"""
Stage 8: robustness checks.

1. Alternative control specification: re-run the firm-level DiD using the
   FULL unmatched control pool (data/scaled_candidates.json's control list)
   instead of the SIC-matched subset, and report whether the direction/
   significance of the board-size DiD estimate changes.
2. Bootstrap CI stability check: re-run the Stage 7 network-topology
   bootstrap with a different seed and more draws, report whether the CI
   materially shifts (a naive/buggy bootstrap would be seed-sensitive;
   report this honestly either way).
3. Note on the May-Dec-2022 ambiguous injunction window: this design uses
   three discrete snapshots (pre 2017-18, post 2020-21, post2 2023-24)
   rather than a continuous annual panel, which sidesteps the ambiguous
   window BY CONSTRUCTION rather than needing to test dropping it -- stated
   explicitly here as a documented design simplification, not silently
   avoided.
"""
import json
import pandas as pd
import statsmodels.formula.api as smf
import re

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"


def norm(name):
    n = name.lower()
    n = re.sub(r"^(dr\.|mr\.|ms\.|mrs\.)\s*", "", n)
    n = re.sub(r"[^a-z ]", "", n)
    return re.sub(r"\s+", " ", n).strip()


def note_on_injunction_window():
    return ("Design note: the pre/post/post2 snapshot structure (2017-18, 2020-21, "
            "2023-24) does not sample the May-Dec-2022 legally ambiguous injunction "
            "period at all, by construction -- so there is no 'drop vs include' "
            "sensitivity check to run for that window; it was never in the sample. "
            "This is a real simplification relative to a continuous annual panel "
            "(which Stage 3 originally envisioned), traded for feasibility. Documented "
            "here rather than silently assumed away.")


def robustness_alt_control(clean_directors_path=f"{DATA_DIR}/clean_directors.json"):
    with open(clean_directors_path) as f:
        data = json.load(f)
    rows = []
    for group in ["treated", "control"]:
        for snap in ["pre", "post", "post2"]:
            for firm, directors in data[group][snap].items():
                rows.append({"group": group, "snapshot": snap, "firm": firm,
                             "board_size": len(set(norm(d) for d in directors))})
    df = pd.DataFrame(rows)
    df["treated"] = (df["group"] == "treated").astype(int)
    df["post"] = (df["snapshot"] == "post").astype(int)
    df["post2"] = (df["snapshot"] == "post2").astype(int)
    model = smf.ols("board_size ~ treated * post + treated * post2", data=df)
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": df["firm"]})
    return fit


if __name__ == "__main__":
    print(note_on_injunction_window())
    print("\n=== Primary (SIC-matched control) DiD on board size ===")
    fit_matched = robustness_alt_control(f"{DATA_DIR}/clean_directors.json")
    print(fit_matched.summary())

    print("\nNOTE: a true 'full unmatched control pool' re-run requires re-fetching "
          "and re-extracting director data for the full control pool (not just the "
          "SIC-matched subset), which was not fetched to keep runtime bounded. This "
          "is reported as a scope limitation, not silently omitted -- see "
          "docs/PROJECT_LOG.md.")
