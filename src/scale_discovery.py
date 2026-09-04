"""
Scale up from the 26-firm pilot to a real ~140-firm panel: CA-HQ treated
firms + matched non-CA control firms, each verified to have a DEF14A in
all three snapshot windows (pre 2017-2018, post 2020-2021, post-injunction
2023-2024). Real EDGAR data throughout -- no invented CIKs or filings.
"""
import sys, json, time, requests
sys.path.insert(0, "/Users/shaurya/CascadeProjects/sb826-board-interlock/src")
from edgar_utils import HEADERS, get_submissions, cik_to_10digit

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"
BROWSE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"

WINDOWS = {
    "pre": {"2017", "2018"},
    "post": {"2020", "2021"},
    "post2": {"2023", "2024"},
}


def browse_ciks(state, start, count=100):
    params = {"action": "getcompany", "State": state, "type": "DEF 14A",
              "dateb": "", "owner": "include", "count": count, "start": start, "output": "atom"}
    r = requests.get(BROWSE_URL, params=params, headers=HEADERS, timeout=30)
    time.sleep(0.15)
    if r.status_code != 200:
        return [], r.status_code
    import re
    ciks = re.findall(r"<cik>(\d+)</cik>", r.text)
    return ciks, 200


def collect_ciks(state, target_n, max_pages=8):
    seen = []
    start = 0
    for _ in range(max_pages):
        ciks, status = browse_ciks(state, start, 100)
        if status != 200 or not ciks:
            break
        seen.extend(ciks)
        start += 100
        if len(set(seen)) >= target_n:
            break
    # de-dup preserve order
    out = []
    s = set()
    for c in seen:
        if c not in s:
            s.add(c)
            out.append(c)
    return out


def check_firm(cik):
    cik10 = cik_to_10digit(cik)
    sub, status = get_submissions(cik10)
    if status != 200 or sub is None:
        return None
    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accns = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])

    window_hits = {}
    for wname, years in WINDOWS.items():
        matches = [(dates[i], accns[i], docs[i]) for i in range(len(forms))
                   if forms[i] == "DEF 14A" and dates[i][:4] in years]
        matches.sort(key=lambda x: x[0])
        window_hits[wname] = matches[-1] if matches else None

    if not all(window_hits.values()):
        return None  # need all three snapshots

    addr = sub.get("addresses", {}).get("business", {})
    return {
        "cik": cik10,
        "name": sub.get("name"),
        "sic": sub.get("sic"),
        "sicDescription": sub.get("sicDescription"),
        "current_state": addr.get("stateOrCountry"),
        "pre": {"date": window_hits["pre"][0], "accn": window_hits["pre"][1], "doc": window_hits["pre"][2]},
        "post": {"date": window_hits["post"][0], "accn": window_hits["post"][1], "doc": window_hits["post"][2]},
        "post2": {"date": window_hits["post2"][0], "accn": window_hits["post2"][1], "doc": window_hits["post2"][2]},
    }


def main():
    print("Collecting CA CIK pool...")
    ca_ciks = collect_ciks("CA", target_n=400, max_pages=6)
    print(f"CA pool: {len(ca_ciks)} CIKs")

    control_states = ["NY", "TX", "IL", "MA", "NJ", "WA", "OH", "PA", "GA", "FL"]
    control_ciks = []
    for st in control_states:
        c = collect_ciks(st, target_n=60, max_pages=1)
        control_ciks.extend(c)
        print(f"  {st} pool: {len(c)}")
    # de-dup
    s = set()
    control_ciks_dedup = []
    for c in control_ciks:
        if c not in s:
            s.add(c)
            control_ciks_dedup.append(c)
    print(f"Control pool total: {len(control_ciks_dedup)} CIKs")

    print("\nVerifying CA firms have all 3 snapshots (this takes a while, one call per CIK)...")
    ca_verified = []
    for i, cik in enumerate(ca_ciks):
        r = check_firm(cik)
        if r:
            r["current_state"] = r["current_state"]
            ca_verified.append(r)
        if i % 25 == 0:
            print(f"  ...{i}/{len(ca_ciks)} checked, {len(ca_verified)} verified so far")
        if len(ca_verified) >= 90:
            break

    print(f"CA verified (all 3 snapshots present): {len(ca_verified)}")

    print("\nVerifying control firms...")
    control_verified = []
    for i, cik in enumerate(control_ciks_dedup):
        r = check_firm(cik)
        if r:
            control_verified.append(r)
        if i % 25 == 0:
            print(f"  ...{i}/{len(control_ciks_dedup)} checked, {len(control_verified)} verified so far")
        if len(control_verified) >= 90:
            break

    print(f"Control verified (all 3 snapshots present): {len(control_verified)}")

    out = {"treated": ca_verified, "control": control_verified}
    with open(f"{DATA_DIR}/scaled_candidates.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote scaled_candidates.json: {len(ca_verified)} treated, {len(control_verified)} control")


if __name__ == "__main__":
    main()
