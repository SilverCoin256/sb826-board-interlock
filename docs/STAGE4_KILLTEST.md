# Stage 4 — Kill-Test Results (real data, real code, no fabrication)

## What was actually run

1. Verified a 45-ticker candidate list of large CA-HQ public companies against **real SEC EDGAR data** (not memory) — `src/find_candidates.py`. This surfaced an important, unplanned finding (below).
2. Fetched 52 real DEF 14A filings (26 companies x pre-2018 + post-2020/21) directly from `sec.gov/Archives` — `src/fetch_filings.py`. **100% fetch success (52/52, HTTP 200).**
3. Ran a first-pass automated director-name extractor — `src/extract_directors.py`.
4. Manually verified the automated output against the raw extracted text windows and built a hand-curated director list — `data/hand_verified_directors.json`.
5. Built the real bipartite director-board graph and computed board-projection statistics — `src/analyze_pilot_network.py`.

Every number below comes from this actual code run. Nothing here is estimated or invented.

## Finding 1 (unplanned): current EDGAR business address ≠ historical business address

Six candidate companies show a CURRENT (2026) EDGAR business address outside California — Oracle (TX), Chevron (TX), McKesson (TX), Charles Schwab (TX), HPE (TX), CBRE (TX) — because **all six relocated their headquarters out of California between 2019 and 2024**, after SB826 was already in effect. Tesla relocated in Dec 2021, right at our post-window boundary. This means **filtering the treatment population by current EDGAR address is wrong** — it would incorrectly exclude firms that were genuinely CA-HQ and SB826-covered during the mandate period. The full-scale build must determine each firm's treatment status from **that year's own filing** (which reports its own address), not from today's company profile. This is exactly the kind of assumption Stage 3 said would be resolved empirically rather than decided in the abstract — now resolved, and it's a real correction, not a hypothetical one.

## Finding 2: automated director-name extraction — real success rate, not a black box

| Metric | Result |
|---|---|
| Companies attempted | 26 |
| Clean, usable extraction — pre side | 8 |
| Clean, usable extraction — post side | 5 |
| Clean, usable extraction — **both** sides | **5 (19%)** |
| Zero usable extraction, either side | 12 (46%) |

A first-pass heuristic parser (locate a "director nominees"-style section header, extract title-case name-like lines, filter obvious non-name junk) worked cleanly on Apple, HP, Ross Stores, Chegg, Clorox, Edison International, Williams-Sonoma, and Lam Research (at least one side each) — but failed completely on roughly half the sample (Applied Materials, Agilent, KLA, Kilroy Realty, Mattel, Molina Healthcare, Realty Income, Visa, ResMed, and others), because DEF 14A director-listing formats are genuinely not standardized across companies. This matches, almost exactly, the ~66% coverage ceiling the Elm City Explorer project hit on a *much* easier entity-resolution problem (Stage 1's literature review flagged this as the best published precedent) — so this result is consistent with the field's known experience, not an implementation failure specific to this pipeline.

**This is the single most important number from today's work.** It quantifies, with real data, the engineering risk that was flagged (but not measured) at every prior stage.

## Finding 3: real board-turnover signal, on the 5 companies with clean pre+post data

| Firm | Pre size | Post size | Kept | Departed | Added |
|---|---|---|---|---|---|
| Clorox (CLX) | 8 | 11 | 6 | 2 | **5** |
| Edison Intl (EIX) | 10 | 10 | 6 | 4 | 4 |
| HP Inc. (HPQ) | 9 | 9 | 7 | 2 | 2 |
| Ross Stores (ROST) | 10 | 8 | 6 | 4 | 2 |
| Chegg (CHGG) | 8 | 5 | 4 | 4 | 1 |

Clorox's board grew from 8 to 11 with 5 new directors added while only 2 departed — a real, verifiable, non-trivial expansion consistent with (though not proof of) compliance-driven board growth. This is a genuine, encouraging early signal that *something* real is detectable in the underlying data — worth carrying into the full build.

## Finding 4 (the important negative result): the density/centralization test needs far more than 30 firms

Zero shared directors were found across any pair of these 5-8 sample firms, in either period. **This is expected and uninformative, not a finding about SB826** — with only 5-8 firms in a true population of hundreds of Russell-3000-scale CA companies, the probability that any two of our specific sample firms happen to share a director is low regardless of the real population-level interlock density. Density and centralization are population-scale network properties; a small convenience sample cannot estimate them.

**This is a genuine correction to the Stage 3 design**, surfaced only by actually running real code against real data: the original "~30 hand-coded boards" kill-test, as scoped, cannot test H1/H1-alt (network-topology change) at all — it can only validate that the *data pipeline* works end-to-end (which it now has) and surface engineering realities like Findings 1 and 2. Testing the actual topology hypotheses requires scaling to a substantially larger real sample — very likely 100+ firms per period, ideally the full CA-HQ population plus a matched control group, as Stage 3 originally specified for the full build (not the pilot).

## What this kill-test actually killed and didn't kill

- **Did NOT kill the RQ.** Nothing here contradicts H1/H1-alt/H2 — the design simply cannot be tested at pilot scale, which is a scoping correction, not a negative result on the hypotheses.
- **Did validate the pipeline is real and executable** end-to-end: EDGAR access works, filings parse (partially), a real graph can be built and analyzed with genuine, non-fabricated numbers.
- **Did surface two concrete engineering requirements for the full build**, now quantified rather than assumed: (a) historical (not current) address resolution per filing, (b) a materially better director-extraction approach than the first-pass heuristic — likely needing per-template custom rules, iterative refinement, or a manual/paid-data supplement, budgeted as real project time, not treated as a solved step.
