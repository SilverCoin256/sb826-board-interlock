"""
Fetch real DEF14A documents (3 snapshots x N firms) for the scaled panel,
and extract each filing's OWN reported business-address state directly
from the document text (cover page) -- fixes the kill-test's Finding 1
(current EDGAR address != historical address) properly, per-filing,
rather than relying on the company's current profile.
"""
import json, os, time, re, requests, sys
sys.path.insert(0, "/Users/shaurya/CascadeProjects/sb826-board-interlock/src")
from edgar_utils import HEADERS

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"
RAW_DIR = os.path.join(DATA_DIR, "raw_scaled")
os.makedirs(RAW_DIR, exist_ok=True)

US_STATE_ABBR = set("""AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT
NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC""".split())


def fetch_doc(cik10, accn, doc, max_retries=4):
    accn_nodash = accn.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{accn_nodash}/{doc}"
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            time.sleep(0.12)
            return r
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout):
            time.sleep(2 ** attempt)
    class _Dummy:
        status_code = -1
        content = b""
    return _Dummy()


def guess_state_from_text(html_bytes):
    """Look for a 2-letter US state code near the top of the document (cover
    page address block) rather than trusting the company's CURRENT EDGAR
    profile. Heuristic, imperfect -- reports None if not confidently found,
    rather than guessing."""
    try:
        text = html_bytes[:20000].decode("utf-8", errors="ignore")
    except Exception:
        return None
    # common pattern: "City, ST 94025" or "City, ST  94025-1234"
    m = re.findall(r",\s*([A-Z]{2})\s+\d{5}(?:-\d{4})?", text)
    for code in m:
        if code in US_STATE_ABBR:
            return code
    return None


MANIFEST_PATH = os.path.join(DATA_DIR, "scaled_fetch_manifest.json")


def main():
    with open(os.path.join(DATA_DIR, "matched_candidates.json")) as f:
        cand = json.load(f)

    manifest = []
    done_keys = set()
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            manifest = json.load(f)
        done_keys = {(m["group"], m["cik"]) for m in manifest}
        print(f"RESUMING: {len(manifest)} firms already in manifest")

    n_since_save = 0
    for group in ["treated", "control"]:
        for firm in cand[group]:
            cik10 = firm["cik"]
            if (group, cik10) in done_keys:
                continue
            entry = {"group": group, "cik": cik10, "name": firm["name"], "sic": firm.get("sic")}
            for tag in ["pre", "post", "post2"]:
                info = firm[tag]
                fname = f"{group}_{cik10}_{tag}.html"
                fpath = os.path.join(RAW_DIR, fname)
                if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
                    with open(fpath, "rb") as fh:
                        content = fh.read()
                    status, detected_state = 200, guess_state_from_text(content)
                    entry[tag] = {"status": status, "bytes": len(content), "file": fname,
                                   "filing_date": info["date"], "detected_state_from_filing_text": detected_state}
                    continue
                r = fetch_doc(cik10, info["accn"], info["doc"])
                status = r.status_code
                detected_state = None
                if status == 200:
                    with open(fpath, "wb") as out:
                        out.write(r.content)
                    detected_state = guess_state_from_text(r.content)
                entry[tag] = {"status": status, "bytes": len(r.content) if status == 200 else 0,
                               "file": fname if status == 200 else None,
                               "filing_date": info["date"],
                               "detected_state_from_filing_text": detected_state}
            manifest.append(entry)
            n_since_save += 1
            print(f"{group:8s} {entry['name'][:35]:35s} "
                  f"pre={entry['pre']['status']}/{entry['pre']['detected_state_from_filing_text']} "
                  f"post={entry['post']['status']}/{entry['post']['detected_state_from_filing_text']} "
                  f"post2={entry['post2']['status']}/{entry['post2']['detected_state_from_filing_text']}")
            if n_since_save >= 10:
                with open(MANIFEST_PATH, "w") as f:
                    json.dump(manifest, f, indent=2)
                n_since_save = 0

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nwrote scaled_fetch_manifest.json, {len(manifest)} firms x 3 snapshots")


if __name__ == "__main__":
    main()
