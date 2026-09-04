"""
Stage 4 kill-test, step 1: verify a candidate list of CA-HQ public companies
via real SEC EDGAR data (not memory), and check which ones have a DEF 14A
filed in both a pre-window (2017-2018) and a post-window (2020-2021).
"""
import sys, json, time
sys.path.insert(0, "/Users/shaurya/CascadeProjects/sb826-board-interlock/src")
from edgar_utils import get_json, get_submissions, cik_to_10digit

# candidate CA-HQ large public companies (to be VERIFIED via EDGAR, not assumed)
CANDIDATES = [
    "AAPL", "GOOGL", "META", "CRM", "ORCL", "INTC", "CSCO", "CVX", "WFC", "V",
    "GPS", "CLX", "PCG", "ADBE", "INTU", "EBAY", "GILD", "AMAT", "AVGO", "QCOM",
    "NVDA", "NFLX", "DIS", "SCHW", "MCK", "YELP", "UBER", "SQ", "PYPL", "WDC",
    "JNPR", "AMGN", "EIX", "SRE", "MAT", "ATVI", "SNAP", "ROST", "WSM", "FRC",
    "BEN", "MOH", "HPQ", "HPE", "CBRE",
    "EA", "ADSK", "CDNS", "SNPS", "A", "KLAC", "LRCX", "MRVL", "ILMN", "RMD",
    "RHI", "JACK", "PSA", "O", "PLD", "ESS", "DECK", "SKX", "HLF", "RH",
    "KRC", "EW", "CHGG", "TSLA",
]

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"

def main():
    tmap, status = get_json(TICKER_MAP_URL)
    if status != 200:
        print("FAILED to fetch ticker map:", status)
        return
    ticker_to_cik = {}
    for _, row in tmap.items():
        ticker_to_cik[row["ticker"].upper()] = row["cik_str"]

    results = []
    for tkr in CANDIDATES:
        cik = ticker_to_cik.get(tkr)
        if cik is None:
            results.append({"ticker": tkr, "status": "NOT_FOUND_IN_TICKER_MAP"})
            continue
        cik10 = cik_to_10digit(cik)
        sub, status = get_submissions(cik10)
        if status != 200 or sub is None:
            results.append({"ticker": tkr, "cik": cik10, "status": f"SUBMISSIONS_FETCH_FAILED_{status}"})
            continue
        addr = sub.get("addresses", {}).get("business", {})
        state = addr.get("stateOrCountry")
        name = sub.get("name")

        recent = sub.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accns = recent.get("accessionNumber", [])
        docs = recent.get("primaryDocument", [])

        def10a = [(dates[i], accns[i], docs[i]) for i in range(len(forms)) if forms[i] == "DEF 14A"]
        # NOTE: 'recent' only covers the most recent ~1000 filings; older DEF14As
        # may live in the submission's "files" array (additional JSON pages).
        # Flagging this explicitly rather than silently assuming recent-only coverage is complete.
        older_files = sub.get("filings", {}).get("files", [])

        has_pre = any(d.startswith(("2017", "2018")) for d, _, _ in def10a)
        has_post = any(d.startswith(("2020", "2021")) for d, _, _ in def10a)

        results.append({
            "ticker": tkr, "cik": cik10, "name": name, "state": state,
            "status": "OK", "n_def14a_recent": len(def10a),
            "has_pre_2017_2018_in_recent": has_pre,
            "has_post_2020_2021_in_recent": has_post,
            "older_filing_pages": len(older_files),
            "def14a_dates_recent": [d for d, _, _ in def10a],
        })

    out_path = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/candidate_verification.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print("wrote", out_path)
    for r in results:
        print(r.get("ticker"), "|", r.get("state"), "|", r.get("status"), "|",
              "pre" if r.get("has_pre_2017_2018_in_recent") else "-",
              "post" if r.get("has_post_2020_2021_in_recent") else "-",
              "| older_pages:", r.get("older_filing_pages"))

if __name__ == "__main__":
    main()
