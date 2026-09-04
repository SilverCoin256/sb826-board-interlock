"""
Pass 1 of scaled entity resolution: locate a probable director-section text
window in each fetched filing (regex-based, cheap), so Pass 2 (LLM-assisted
extraction) can work on a small trimmed window instead of a 200-800KB raw
document. Documents where no marker is found are flagged, not silently
dropped -- Pass 2 still gets a fallback window and an honest "low_confidence"
flag.
"""
import os, re, json, glob
from bs4 import BeautifulSoup

RAW_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/raw_scaled"
OUT_PATH = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/director_windows_scaled.json"

MARKERS = [
    "Board of Directors and Committees", "Our Director Nominees",
    "Nominees for Director", "NOMINEES FOR ELECTION", "Election of Directors",
    "ELECTION OF DIRECTORS", "Director Nominees", "DIRECTOR NOMINEE BIOGRAPHIES",
    "Proposal No. 1", "PROPOSAL 1", "Proposal 1 -", "Item 1.",
]

WINDOW_CHARS = 9000


def main():
    out = {}
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.html")))
    n_marker_found = 0
    for path in files:
        base = os.path.basename(path).replace(".html", "")
        with open(path, "rb") as f:
            soup = BeautifulSoup(f.read(), "lxml")
        text = soup.get_text("\n")
        best = None
        for marker in MARKERS:
            idx = text.find(marker)
            if idx != -1:
                best = (marker, idx)
                break
        if best:
            marker, idx = best
            window = text[idx: idx + WINDOW_CHARS]
            out[base] = {"marker": marker, "window": window, "low_confidence": False}
            n_marker_found += 1
        else:
            # fallback: first WINDOW_CHARS of body text past typical cover-page boilerplate
            window = text[3000:3000 + WINDOW_CHARS]
            out[base] = {"marker": None, "window": window, "low_confidence": True}

    with open(OUT_PATH, "w") as f:
        json.dump(out, f)
    print(f"processed {len(files)} files; marker found in {n_marker_found} "
          f"({n_marker_found/len(files)*100:.1f}%); wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
