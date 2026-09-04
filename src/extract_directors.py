"""
Stage 4 kill-test, step 3: extract director-name candidates from each fetched
DEF 14A. This is a heuristic, imperfect extractor by design — real DEF14As
have no standardized machine-readable director-list format. Approach:
locate a probable "director nominees" section via multiple header markers,
then pull title-case 2-4 word name-candidates out of that window.

Every extraction is written with its source window so it can be spot-checked
against the raw text — per Stage 3 design, entity-resolution accuracy is
reported as a first-class result, not hidden.
"""
import re, os, json, glob

RAW_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/raw_def14a"
OUT_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"

from bs4 import BeautifulSoup

SECTION_MARKERS = [
    "Board of Directors and Committees",
    "Our Director Nominees",
    "Nominees for Director",
    "NOMINEES FOR ELECTION",
    "Election of Directors",
    "ELECTION OF DIRECTORS",
    "Director Nominees",
]

STOPWORD_LINES = {
    "board of directors", "election of directors", "table of contents",
    "annual meeting", "proxy statement", "other public", "public company",
    "audit and finance", "nominating and", "corporate governance",
    "compensation committee", "other information", "general information",
    "notice of annual", "record date", "proxy access", "shareholder proposal",
}

NAME_RE = re.compile(r"^[A-Z][a-zA-Z\.\-']+(?:\s+[A-Z][a-zA-Z\.\-']+){1,3}$")


def find_section_window(text, window_chars=6000):
    for marker in SECTION_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            return text[idx: idx + window_chars], marker, idx
    return None, None, None


def candidate_names(window_text):
    lines = [l.strip() for l in window_text.split("\n")]
    candidates = []
    for l in lines:
        if not l or len(l) > 40 or len(l) < 4:
            continue
        low = l.lower()
        if low in STOPWORD_LINES:
            continue
        if any(sw in low for sw in ["committee", "proposal", "meeting", "election", "director since",
                                      "public company", "corporate", "annual report", "chairman of",
                                      "governance", "audit", "compensation", "nominating"]):
            continue
        if NAME_RE.match(l):
            candidates.append(l)
    # de-dup, preserve order
    seen = set()
    out = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def main():
    results = {}
    for path in sorted(glob.glob(os.path.join(RAW_DIR, "*.html"))):
        base = os.path.basename(path).replace(".html", "")
        with open(path, "rb") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        text = soup.get_text("\n")
        window, marker, idx = find_section_window(text)
        if window is None:
            results[base] = {"marker": None, "candidates": [], "n": 0, "note": "NO SECTION MARKER FOUND"}
            continue
        cands = candidate_names(window)
        results[base] = {"marker": marker, "char_offset": idx, "candidates": cands, "n": len(cands)}

    out_path = os.path.join(OUT_DIR, "director_candidates_raw.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    for k, v in results.items():
        print(f"{k:20s} marker={v.get('marker')!s:35s} n={v['n']:3d} sample={v['candidates'][:5]}")
    print("\nwrote", out_path)


if __name__ == "__main__":
    main()
