"""
Stage 4 kill-test, step 2: for the confirmed CA-HQ, pre+post candidates,
pick one pre (2017-2018) and one post (2020-2021) DEF 14A each, fetch the
real filing document from EDGAR, and save raw HTML for parsing.
"""
import sys, json, time, os
sys.path.insert(0, "/Users/shaurya/CascadeProjects/sb826-board-interlock/src")
from edgar_utils import get_submissions, cik_to_10digit, HEADERS
import requests

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"
RAW_DIR = os.path.join(DATA_DIR, "raw_def14a")
os.makedirs(RAW_DIR, exist_ok=True)

# confirmed current-CA, pre+post available (excludes HLF [ambiguous foreign
# incorporation state code 'E9'] and any relocated-HQ company, per honest
# flag in PROJECT_LOG — those need per-filing address verification, deferred)
CONFIRMED = [
    "AAPL", "V", "CLX", "PCG", "GILD", "AMAT", "EIX", "MAT", "ROST", "WSM",
    "HPQ", "MOH", "ADSK", "SNPS", "A", "KLAC", "LRCX", "RMD", "RHI", "JACK",
    "O", "ESS", "DECK", "RH", "KRC", "CHGG",
]

with open(os.path.join(DATA_DIR, "candidate_verification.json")) as f:
    verified = {r["ticker"]: r for r in json.load(f)}


def pick_filing(cik10, window_years):
    sub, status = get_submissions(cik10)
    if status != 200:
        return None
    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accns = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])
    matches = [
        (dates[i], accns[i], docs[i])
        for i in range(len(forms))
        if forms[i] == "DEF 14A" and dates[i][:4] in window_years
    ]
    if not matches:
        return None
    matches.sort(key=lambda x: x[0])  # ascending; take latest in window
    return matches[-1]


def fetch_and_save(ticker, cik10, accn, doc, tag):
    accn_nodash = accn.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{accn_nodash}/{doc}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    time.sleep(0.15)
    out_path = os.path.join(RAW_DIR, f"{ticker}_{tag}.html")
    status = r.status_code
    if status == 200:
        with open(out_path, "wb") as f:
            f.write(r.content)
    return {"ticker": ticker, "tag": tag, "url": url, "status": status,
            "bytes": len(r.content) if status == 200 else 0, "saved": out_path if status == 200 else None}


def main():
    manifest = []
    for tkr in CONFIRMED:
        v = verified.get(tkr)
        if not v:
            manifest.append({"ticker": tkr, "error": "not in verification file"})
            continue
        cik10 = v["cik"]
        pre = pick_filing(cik10, {"2017", "2018"})
        post = pick_filing(cik10, {"2020", "2021"})
        entry = {"ticker": tkr, "cik": cik10, "name": v.get("name")}
        if pre:
            entry["pre"] = fetch_and_save(tkr, cik10, pre[1], pre[2], "pre")
            entry["pre"]["filing_date"] = pre[0]
        else:
            entry["pre"] = None
        if post:
            entry["post"] = fetch_and_save(tkr, cik10, post[1], post[2], "post")
            entry["post"]["filing_date"] = post[0]
        else:
            entry["post"] = None
        manifest.append(entry)
        print(tkr, "pre:", entry["pre"]["status"] if entry["pre"] else "MISSING",
              entry["pre"]["bytes"] if entry["pre"] else "-",
              "| post:", entry["post"]["status"] if entry["post"] else "MISSING",
              entry["post"]["bytes"] if entry["post"] else "-")

    with open(os.path.join(DATA_DIR, "fetch_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("wrote manifest")


if __name__ == "__main__":
    main()
