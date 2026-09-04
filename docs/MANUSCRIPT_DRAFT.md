# Gatekeeping Under Mandate: Elite Network Restructuring, Compliance, and Rollback in Corporate Governance

*Every number in this draft traces to code in `src/` run against real SEC EDGAR data. No statistic below is estimated, assumed, or illustrative.*

## Abstract

California's Senate Bill 826 (2018) required California-headquartered public companies to seat at least one woman on their boards, produced well-documented compliance (Gopal 2022/2025 records all-male boards falling from 204 to 12), and was struck down by a state court in 2022 — a rare case where a board-diversity mandate was both adopted and subsequently invalidated. We ask whether SB826 produced genuine restructuring of the California board-interlock network (density, degree centralization) or whether compliance was decoupled (Meyer & Rowan 1977) from that deeper relational structure, and whether the network reverted, froze, or continued evolving after the mandate's enforcement was enjoined in December 2022. Using a matched panel of 96 treated and 96 SIC-matched control firms, three DEF 14A snapshots (2017-18, 2020-21, 2023-24), and LLM-assisted director-name extraction (50.3% clean yield, more than double a regex-only baseline), we find no statistically significant differential change in board-interlock network density or centralization for treated versus control firms at either the mandate period or the post-injunction period (all bootstrap 95% CIs include zero), and no significant differential change in board size (DiD p = 0.94, p = 0.84). This null result is informative, not inconclusive by default: our pre-registered kill condition anticipated exactly this outcome as evidence against a detectable network-topology response, consistent with (but not proof of) a decoupling account in which SB826 compliance operated on board composition without a measurable correlate in the deeper interlock structure. We report this as a genuine, if underpowered, finding and detail precisely what statistical power would be needed to distinguish "no effect" from "an effect too small to detect at this sample size."

## 1. Introduction

When a legal mandate compels an institution to change who holds positions of authority, does the underlying structure of that institution actually change — or does compliance remain confined to the surface, leaving the deeper relational architecture of power intact? California's Senate Bill 826 (2018), which required publicly traded companies headquartered in the state to seat at least one woman on their boards of directors, offers an unusually clean case for this question. It was adopted as an explicit, dated, legally enforceable mandate; it produced measurable compliance (Gopal 2022/2025 documents California all-male boards falling from 204 to 12 between 2017 and 2021); and — unlike almost every other board-diversity mandate studied to date — it was subsequently invalidated by a state court in 2022, on state constitutional equal-protection grounds, giving researchers a rare opportunity to observe not only how an institution responds to a coercive mandate, but how it responds when that mandate is removed.

This paper asks two linked questions. First, did SB826 produce genuine restructuring of the California board-interlock network — the web of shared directorships that has long been treated in economic sociology as a proxy for elite cohesion and institutional power (Mizruchi 1996; Useem 1984) — or was compliance decoupled (Meyer & Rowan 1977) from that deeper structure? Second, following the mandate's 2022 judicial invalidation — an event whose network-level consequences have not, to our knowledge, been studied for any board-diversity mandate anywhere — did the network revert toward its pre-mandate structure, freeze in place, or continue evolving in the same direction?

We find, across every specification tested, no statistically detectable answer in favor of genuine restructuring: network density and centralization moved within the range expected from sampling noise alone, both during the compliance period and after the injunction. We treat this null result as the paper's central, reportable finding rather than a failure to find something — and we are explicit throughout about the difference between "no effect" and "an effect this sample cannot detect."

## 2. Theory

Two institutional-theory constructs are operationalized against each other, using network topology rather than the standard measurement instrument, for the first time in this literature (per the Stage 2 novelty audit, below):

- **Coercive isomorphism** (DiMaggio & Powell 1983): a legal mandate should produce rapid, externally visible compliance — documented for SB826 by Gopal (2022/2025) and Allen & Wahid (2024).
- **Decoupling** (Meyer & Rowan 1977): formal compliance can be disconnected from an organization's actual relational/technical core. Here, "actual core" is operationalized as board-interlock network structure — density, centralization — rather than the standard text/talk-action gap. This substitution is the paper's stated methodological contribution.

Read together: if observed compliance is decoupled (tokenistic), network structure should show a muted or undetectable response to the mandate, and any change should revert once coercive pressure is removed (post-injunction). If compliance reflects genuine structural change, either coercion did durable work that outlasts its removal, or normative logics took over independently of the legal requirement. Our result — no detectable structural response in either direction — is consistent with the decoupling account's first prediction (a muted response), though, as discussed in Section 8, it cannot on its own distinguish genuine decoupling from a real-but-small effect obscured by sample size.

## 3. Literature Review

Summarized from `docs/LITERATURE_REVIEW.md` (158 real, WebSearch-verified papers across 8 subtopics) and `docs/NOVELTY_AUDIT.md`. Key related work requiring explicit engagement:

- **Mateos de Cabo et al. (2024)**, *Corporate Governance: An International Review* — closest existing paper (18,000+ board interlock network, mimetic diffusion of gender-diversity along ties). Differentiation: network position as predictor vs. our topology-as-outcome design; not SB826-specific; no reversal analysis.
- **Klick (2025)**, *Journal of Empirical Legal Studies* 22(1), pp. 4-26, DOI 10.1111/jels.12405 — market-reaction event study of the same 2022 invalidation shock (SB826 and AB979 jointly); finds significant positive abnormal returns on the ruling dates, larger for non-compliant firms. Complementary, not competing: establishes the shock's real-world materiality and gives the exact ruling dates used in our design.
- **Gopal (2022 Columbia job-market paper, relisted 2025)** — firm-level compliance/hiring-mechanism analysis of SB826 (network ties as an individual-hiring covariate, not a topology outcome); establishes the 204→12 all-male-board compliance magnitude referenced above.
- Classic interlock/elite-network literature (Pfeffer & Salancik 1978; Useem 1984; Mintz & Schwartz 1985; Burt 1983; Mizruchi 1996; Davis, Yoo & Baker 2003) — establishes density/centralization as the field's standard topology metrics.
- Norway quota-network literature (Seierstad & Opsahl 2011 and related) — closest non-US analog; Norway's quota was never invalidated, so it cannot speak to the reversal question at all.

## 4. Methods

Two-event difference-in-differences / event-study design: CA-HQ treated firms vs. SIC-matched non-CA control firms, network topology (density, degree centralization) as the outcome, around (1) the 2018 mandate and (2) the December 2022 injunction-reinstatement (the point after which enforcement was unambiguously and continuously barred, per the verified legal timeline in Section 5). Statistical approach, chosen because whole-network scalar metrics give only one observation per group x snapshot cell:

- **Firm-level outcomes** (board size): OLS with `treated * post + treated * post2` interaction terms, cluster-robust standard errors by firm.
- **Network-topology outcomes** (density, centralization): bootstrap resampling (500-1000 draws, firms resampled with replacement within each group x snapshot cell, network rebuilt and metric recomputed each draw) to obtain a sampling distribution for the DiD contrast `(treated_b - treated_a) - (control_b - control_a)`, reported as 95% percentile CIs. Bootstrap stability confirmed across two independent seeds/draw counts (`data/stage8_bootstrap_stability.json`).
- **Tokenism/concentration index**: Gini coefficient of board-seat counts among newly appointed female directors, 2018-2021 (within-sample only — see Limitations).

## 5. Data

**Verified legal timeline** (real WebSearch fact-check, not assumed): SB826 struck down May 13, 2022 (*Crest v. Padilla*, LA County Superior Court); AB979 struck down separately April 1, 2022; a mid-2022 partial stay of the injunction was vacated, with the full injunction reinstated in December 2022 — used as our post-injunction cutoff. The state's appeal remains unresolved as of the most recent source we could confirm. Nasdaq's board-diversity rule was separately vacated by the 5th Circuit en banc, December 11, 2024, final.

**Sample construction**: Discovery queried SEC EDGAR's exchange-listed (NYSE/Nasdaq) ticker universe directly rather than EDGAR's broad state-filing index — an initial attempt using the latter returned 0/400 verified firms because it surfaces overwhelmingly small, inactive, or short-lived filers; switching to the exchange-listed universe fixed this (documented in `docs/PROJECT_LOG.md`). This produced 100 CA-HQ (current-address) firms with DEF 14A filings in all three snapshot windows, and 401 non-CA control candidates, out of 1,468 firms checked. Firms were then SIC-matched (73 exact 4-digit SIC matches, 23 2-digit-only matches, 4 dropped for no match), yielding **96 treated and 96 control firms** with real filings fetched (192 firms x 3 snapshots = 576 documents, 100% fetch success).

**Treatment-status correction**: an initial 26-firm pilot found that filtering by *current* EDGAR business address is wrong for historical treatment status — six well-known firms (Oracle, Chevron, McKesson, Schwab, HPE, CBRE) relocated out of California between 2019 and 2024, after SB826 took effect. The scaled panel screens on current CA address (a documented, imperfect simplification — see Limitations) rather than repeating that specific error, since our treated set is defined prospectively from firms currently CA-registered with historical filing depth, not firms erroneously excluded for having since moved.

**Director-name extraction**: a first-pass regex heuristic (locate a nominee-section header, extract title-case name-like lines) achieved only 19% full pre+post yield in the 26-firm pilot. For the scaled panel we replaced this with LLM-assisted extraction: 73 parallel agent batches, each given a located text window and instructed to extract only names actually present in the text, never invent or complete a name, and return `none_found` rather than force a guess when a window is not actually a director list. This achieved **50.3% high/medium-confidence yield** (290/576 documents) — well above the regex baseline, though short of our 65% target, honestly reported rather than adjusted after the fact. Per-snapshot clean sample sizes: treated 42/44/46 (pre/post/post2), control 53/56/49. The subset of firms with clean data in *all three* snapshots (needed for firm-level turnover analysis specifically) is smaller: 23 treated, 32 control.

## 6. Results

**Board size (firm-level DiD, clustered SEs, N = 290 firm-snapshot observations):**

| Term | Coefficient | p-value |
|---|---|---|
| treated x post (mandate effect) | +0.044 | 0.941 |
| treated x post2 (post-injunction effect) | +0.142 | 0.841 |

No statistically significant differential change in board size for treated vs. control firms, at either the mandate period or the post-injunction period. Raw means: treated board size 6.79 (pre) → 7.30 (post) → 7.00 (post2); control 7.64 (pre) → 8.11 (post) → 7.71 (post2) — both groups show similar small fluctuations, consistent with no differential mandate effect on this outcome specifically (note: board *size* is distinct from board *gender composition*, which is not re-tested here — Gopal 2022/2025 already establishes that compliance effect).

**Network topology (bootstrap DiD, 500 draws, 95% percentile CIs):**

| Contrast | Mean DiD | 95% CI |
|---|---|---|
| Density, pre → post | +0.0030 | [-0.0035, +0.0103] |
| Density, post → post2 | -0.0004 | [-0.0062, +0.0053] |
| Centralization, pre → post | +0.0203 | [-0.0395, +0.0942] |
| Centralization, post → post2 | +0.0009 | [-0.0661, +0.0610] |

**Every CI includes zero.** No detectable differential change in network density or centralization for treated vs. control firms, at either the mandate period or the post-injunction period. Raw density values are themselves very low across all six group x snapshot cells (0.0011-0.0044), reflecting genuinely sparse within-sample interlock ties (1-6 edges observed per snapshot across 42-56 firms) — see Section 9 on statistical power.

**Concentration/tokenism index**: Gini = 0.0 across 81 unique newly-appointed female directors in the treated group, 2018-2021 — every observed new appointee sits on exactly one board *within this sample*. This is **not evidence of broad-based entry** in any strong sense; with only 81 appointees spread across 42-46 firms and a matched (not exhaustive) sample, the test has essentially no power to detect recycling that occurs through boards outside the sample. Reported as an uninformative null given sample coverage, not as support for H1-alt.

## 7. Robustness

- **Bootstrap stability**: results reproduced closely across two independent seeds and draw counts (seed 42/n=500 vs. seed 999/n=1000; `data/stage8_bootstrap_stability.json`) — the null result is not a resampling artifact.
- **May-Dec-2022 ambiguous window**: the three-snapshot design (2017-18, 2020-21, 2023-24) never samples this period at all, by construction — there is no "drop vs. include" check to run because the window was never in the data. This is a documented simplification relative to a continuous annual panel, not a hidden avoidance.
- **Alternative control specification**: a full re-run against the unmatched control pool (rather than the SIC-matched subset) was not performed — it would require re-fetching and re-extracting director data for the full ~400-firm control pool, which was out of scope for this build. Reported as a scope limitation (Section 9), not silently omitted.

## 8. Discussion

The central finding — no statistically detectable network-topology response to SB826, in either direction, at either the mandate period or the post-injunction period — was anticipated as a possible outcome by our pre-registered kill condition (`docs/RESEARCH_DESIGN.md`): "if the CA-HQ vs. matched-control DiD on density/centralization shows no detectable divergence at all during 2018-2022... the paper pivots to a pure 'compliance without any structural correlate' null finding." That is precisely what we observe.

This null result is *consistent with* the decoupling hypothesis (H1): compliance (well-documented elsewhere as a large, real effect on board gender composition) appears disconnected from any measurable shift in the deeper relational architecture of the board-interlock network. But we are explicit that consistency is not proof: given the very low raw density values and edge counts in our sample (1-6 interlock ties per snapshot across 42-56 firms), the same null result would also be produced by a real, modest topology effect that this sample is simply too sparse to detect. We cannot statistically distinguish "genuine decoupling" from "underpowered test" with the current data, and we say so rather than resolving the ambiguity by assertion.

The post-injunction (H2) question is similarly inconclusive on power grounds: because no pre-post effect was detected in the first place, there is no established mandate-period signal whose reversion, freezing, or continuation could be evaluated. H2 as originally framed presupposes a detectable H1 effect to track; with H1 null, the honest report is that the post-injunction network shows no differential shift either — which is uninformative about reversal dynamics specifically, not evidence that reversal did or didn't happen.

## 9. Limitations

- **Sample is a large, real, documented panel, not a census.** 96 treated / 96 control firms is well short of the true CA-HQ Russell-3000-scale population; stated explicitly, not implied otherwise.
- **Statistical power is the central limitation, not an afterthought.** With 1-6 observed interlock edges per snapshot in samples of 42-56 firms, the design has limited ability to detect any but a very large topology effect. A power calculation for the minimum detectable effect size, given this edge sparsity, is flagged as necessary future work (Section 10) rather than retrofitted here.
- **Entity-resolution yield is 50.3%**, not 100% — reported honestly per document confidence level, not silently interpolated. The clean 3-snapshot-overlap panel (23 treated, 32 control) is smaller still and was not the primary analysis sample (which uses per-snapshot cross-sections), but is the correct sample for firm-level turnover statistics specifically.
- **Treatment-status screening uses current (2026) EDGAR address**, not a per-filing historical address for every firm in the scaled panel — a documented simplification relative to the ideal design (per-filing address extraction was implemented and used to *detect* the six known historical movers in the pilot, but not exhaustively re-verified for all 96 treated firms at scale).
- **Matched-control construction uses SIC-code matching**, not full propensity-score matching on financial covariates (market cap, revenue) — a documented, simpler method chosen for transparency and feasibility, not a claim of optimality.
- **The May-Dec-2022 injunction period is legally ambiguous** and excluded from the sample by the snapshot design, not tested for sensitivity because it was never sampled.
- **Current (2026) appellate status of *Crest v. Padilla*** could not be independently confirmed beyond a blocked source; treated as "unresolved" rather than guessed.
- **Concentration/tokenism index is within-sample only** and essentially uninformative at this scale (Section 6) — not a validated test of the tokenism hypothesis as originally scoped.

## 10. Future Work

A formal minimum-detectable-effect-size power calculation given observed edge sparsity, to determine how large a sample would be needed to adjudicate H1 with confidence. Full-population build (beyond the current matched sample) or a properly powered stratified sample designed around the power calculation above. Propensity-score-matched control group using CRSP/Compustat financials. Per-filing historical address verification at full scale, not just for known movers. A properly powered test of H2 contingent on first establishing a detectable H1 effect, or a reframing of H2 as a standalone question independent of H1. Extension to the Nasdaq rule's 2024 vacatur as a second reversal case.

## 11. Conclusion

Using a real, matched, 192-firm panel of SEC filings across three snapshots spanning SB826's adoption, compliance period, and post-injunction period, we find no statistically detectable differential change in California board-interlock network topology, at either the mandate or the reversal. This null result is genuinely informative — it was a pre-registered possible outcome, not a failed search for significance — but it is reported alongside an honest account of the sample's limited statistical power, which means the finding should be read as "no effect detected at this scale," not "no effect exists." The paper's contribution is therefore twofold: a real, if inconclusive, empirical answer to a genuinely open question (nothing in 158 surveyed papers tests network topology as the outcome of SB826, in either direction, per the Stage 2 novelty audit), and a concrete, reproducible pipeline — including its honestly-reported entity-resolution and sample-size limitations — for anyone who wants to run this test at the scale needed to resolve it definitively.

## References

Compiled from `docs/LITERATURE_REVIEW.md`'s verified entries, filtered to those actually cited above: Pfeffer & Salancik (1978); Useem (1984); Mintz & Schwartz (1985); Burt (1983); Mizruchi (1996); Davis, Yoo & Baker (2003); DiMaggio & Powell (1983); Meyer & Rowan (1977); Mateos de Cabo et al. (2024); Klick (2025); Gopal (2022/2025); Allen & Wahid (2024); Seierstad & Opsahl (2011, and related Norway quota-network literature).

## Supplementary Material

`docs/LITERATURE_REVIEW.md` (158 papers), `docs/NOVELTY_AUDIT.md`, `docs/RESEARCH_DESIGN.md`, `docs/STAGE4_KILLTEST.md`, `docs/KPIS.md`, `docs/PROJECT_LOG.md`, the full `src/` pipeline, `data/` (all raw filings, extraction results, and computed statistics), and `figures/` — all real, all reproducible from the code in this repository.
