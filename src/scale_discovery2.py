"""
Fixed discovery approach. The first attempt (browse-edgar State=CA/other,
type=DEF14A) returned 0/400 verified because that endpoint surfaces ANY
filer that ever listed a CA/etc address -- overwhelmingly small, inactive,
or short-lived companies that don't span a continuous 2017-2024 filing
history. Real, honest finding, logged in PROJECT_LOG.md.

Fix: iterate the SEC's exchange-listed ticker universe (company_tickers_
exchange.json -- NYSE/Nasdaq only, excludes OTC/shell-heavy noise), check
each firm's CURRENT business-address state (fast first-pass filter) and
whether it has a DEF14A in all three snapshot windows.
"""
import sys, json, time
sys.path.insert(0, "/Users/shaurya/CascadeProjects/sb826-board-interlock/src")
from edgar_utils import get_json, get_submissions, cik_to_10digit

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"
EXCHANGE_URL = "https://www.sec.gov/files/company_tickers_exchange.json"

WINDOWS = {
    "pre": {"2017", "2018"},
    "post": {"2020", "2021"},
    "post2": {"2023", "2024"},
}

CONTROL_STATES = {"NY", "TX", "IL", "MA", "NJ", "WA", "OH", "PA", "GA", "FL", "CT", "MN", "MI", "VA", "CO"}


def check_firm(cik10):
    sub, status = get_submissions(cik10)
    if status != 200 or sub is None:
        return None, None
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

    addr = sub.get("addresses", {}).get("business", {})
    state = addr.get("stateOrCountry")

    if not all(window_hits.values()):
        return state, None

    result = {
        "cik": cik10, "name": sub.get("name"), "sic": sub.get("sic"),
        "sicDescription": sub.get("sicDescription"), "current_state": state,
        "pre": {"date": window_hits["pre"][0], "accn": window_hits["pre"][1], "doc": window_hits["pre"][2]},
        "post": {"date": window_hits["post"][0], "accn": window_hits["post"][1], "doc": window_hits["post"][2]},
        "post2": {"date": window_hits["post2"][0], "accn": window_hits["post2"][1], "doc": window_hits["post2"][2]},
    }
    return state, result


CHECKPOINT_PATH = f"{DATA_DIR}/scale_discovery2_checkpoint.json"


def save_checkpoint(treated, control, checked_ciks, n_checked, n_ca, n_ctrl):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump({"treated": treated, "control": control,
                    "checked_ciks": list(checked_ciks),
                    "n_checked": n_checked, "n_ca_state_seen": n_ca,
                    "n_control_state_seen": n_ctrl}, f)


def main():
    exch, status = get_json(EXCHANGE_URL)
    if status != 200:
        print("FAILED to fetch exchange ticker map:", status)
        return
    fields = exch["fields"]
    rows = exch["data"]
    print(f"total exchange-listed entries: {len(rows)}")

    treated, control, checked_ciks = [], [], set()
    n_checked = n_ca_state_seen = n_control_state_seen = 0

    try:
        with open(CHECKPOINT_PATH) as f:
            ck = json.load(f)
        treated, control = ck["treated"], ck["control"]
        checked_ciks = set(ck["checked_ciks"])
        n_checked, n_ca_state_seen, n_control_state_seen = ck["n_checked"], ck["n_ca_state_seen"], ck["n_control_state_seen"]
        print(f"RESUMED from checkpoint: n_checked={n_checked}, treated={len(treated)}, control={len(control)}")
    except FileNotFoundError:
        print("no checkpoint found, starting fresh")

    n_errors = 0
    for row in rows:
        rec = dict(zip(fields, row))
        exchange = rec.get("exchange")
        if exchange not in ("Nasdaq", "NYSE"):
            continue
        cik10 = cik_to_10digit(rec["cik"])
        if cik10 in checked_ciks:
            continue
        state, result = check_firm(cik10)
        checked_ciks.add(cik10)
        n_checked += 1
        if state is None:
            n_errors += 1
        elif state == "CA":
            n_ca_state_seen += 1
            if result:
                treated.append(result)
        elif state in CONTROL_STATES:
            n_control_state_seen += 1
            if result:
                control.append(result)

        if n_checked % 50 == 0:
            save_checkpoint(treated, control, checked_ciks, n_checked, n_ca_state_seen, n_control_state_seen)
            print(f"  checked {n_checked}, CA-state-seen={n_ca_state_seen} "
                  f"(verified={len(treated)}), control-state-seen={n_control_state_seen} "
                  f"(verified={len(control)}), errors={n_errors}")

        if len(treated) >= 100 and len(control) >= 100:
            break
        if n_checked >= 4000:
            print("hit attempt cap (4000), stopping")
            break

    save_checkpoint(treated, control, checked_ciks, n_checked, n_ca_state_seen, n_control_state_seen)
    out = {"treated": treated, "control": control,
           "meta": {"n_checked": n_checked, "n_ca_state_seen": n_ca_state_seen,
                     "n_control_state_seen": n_control_state_seen, "n_errors": n_errors}}
    with open(f"{DATA_DIR}/scaled_candidates.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nFINAL: treated={len(treated)}, control={len(control)}, "
          f"checked={n_checked}, CA-seen={n_ca_state_seen}, control-state-seen={n_control_state_seen}, errors={n_errors}")


if __name__ == "__main__":
    main()
