# Stage 3 — Research Design

## Verified legal timeline (Stage 3 fact-check, real WebSearch, sources logged in PROJECT_LOG.md)

This replaces earlier session-level approximations with verified dates:

- **SB 826** (2018 women-on-boards mandate): struck down May 13, 2022, LA County Superior Court (Judge Duffy-Lewis), *Crest v. Padilla*, Case No. 19STCV27561, on state equal-protection grounds.
- **AB 979** (2020 underrepresented-minorities mandate): struck down separately, April 1, 2022, different judge, same court — "*Crest v. Padilla II*."
- **Injunction dynamics are not a single clean date.** The trial-court injunction barred state enforcement immediately, but the Court of Appeal temporarily lifted part of it (state data-collection/reporting only) in mid-2022, then reinstated the full injunction in December 2022 after denying the state's stay request. Net legal effect throughout: the state cannot enforce either mandate. The state's appeal is ongoing and unresolved as of the most recent source I could confirm (July 2026); I could not independently verify a source describing current appellate briefing status beyond a blocked snippet, so I am treating the appeal as **open/unresolved, not decided**, rather than guessing an outcome.
- **Nasdaq board-diversity rule:** SEC-approved 2021; 5th Circuit panel upheld it (~Oct 2023); reheard en banc; **vacated 9-8 on Dec 11, 2024** (arbitrary/capricious under the APA); neither Nasdaq nor SEC sought certiorari — final, rule dead as of ~March 2025.

**Design consequence:** there is no single "reversal date." I'm treating **December 2022** (Court of Appeal's reinstatement of the full injunction, after the mid-2022 partial-lift episode resolved) as the point after which enforcement pressure was unambiguously and continuously absent — and flagging May–Dec 2022 explicitly as a legally ambiguous transition window to be excluded from the core specification and used only as a robustness-check boundary. This is a judgment call, documented as one, not a hidden assumption.

## Hypotheses (stated before any data is touched, per your kill-condition requirement)

**H1 (Decoupling/tokenism).** SB 826 compliance (elimination of all-male boards) was decoupled from genuine network restructuring: density/centralization/cohesion metrics for CA-HQ boards show muted change relative to the scale of compliance-count change, and/or new appointments are concentrated in a small, repeatedly-recycled pool of "credentialed" directors rather than broad-based entry.

**H1-alt (Genuine restructuring).** Network-topology metrics shift substantively alongside compliance, and new entrants are broadly distributed (low concentration) — inconsistent with tokenism.

**H2 (Post-injunction trajectory — three mutually exclusive, ex-ante predictions).** After December 2022, CA-HQ treated-firm network structure either (a) **reverts** toward its pre-2018 trend, (b) **freezes** at its 2022 level, or (c) **continues** evolving in the same direction as during 2018-2022. Institutional theory gives each a distinct causal story: (a) is consistent with change having been purely coercive/legitimacy-driven; (c) is consistent with normative internalization outlasting the mandate; (b) is the ambiguous middle case and needs the tokenism/concentration measure from H1 to interpret.

**Pre-registered kill condition:** if the CA-HQ vs. matched-control DiD on density/centralization shows no detectable divergence at all during 2018-2022 (i.e., compliance happened with literally zero network-topology signature, not even a muted one), H1 and H1-alt are both moot and the paper pivots to a pure "compliance without any structural correlate" null finding — still publishable as an honest null result, but a materially different paper. This should be checked on the cheap hand-coded pilot (below) before the full build.

## Conceptual framework

Two institutional-theory constructs, operationalized against each other for the first time via network topology (per Stage 2's novelty audit):

- **Coercive isomorphism** (DiMaggio & Powell 1983): a legal mandate should produce rapid, externally-visible compliance.
- **Decoupling** (Meyer & Rowan 1977): formal compliance can be decoupled from the organization's actual relational/technical core. Here, "actual core" = board-interlock network structure, not headcount compliance — this substitution (topology instead of the standard text/rating talk-action gap) is the paper's stated methodological contribution.

Reading H1 and H2 together: decoupled (tokenistic) compliance implies change was legitimacy-performance only, predicting reversion once legal pressure is removed (H2a). Genuine structural change implies either coercion did real work that outlasts removal of the coercive source (unlikely under classic institutional theory, but testable) or that normative logics took over (H2c). This gives the empirical revert/freeze/continue finding real theoretical stakes rather than being a bare description.

## Unit of analysis, population, time window

- **Primary unit:** the whole board-interlock network (California-HQ, SB826-covered public firms) per year, described by graph-level metrics (density, centralization, largest-component size, k-core/community structure, gender assortativity).
- **Secondary unit:** the individual newly-appointed female director, 2018-2022, for the concentration/tokenism index.
- **Population:** California-headquartered, SB826-covered public companies (following the same population definition used by Allen & Wahid 2024 and Klick 2025, which keeps our sample construction comparable to established work rather than inventing an unvetted population).
- **Comparison group:** matched non-CA-HQ public firms (similar size/industry, no SB826 exposure) — a real control group, not a before/after-only design. Rejected the Norway-style no-control design specifically because the U.S. setting gives us an actual untreated comparison population SB826 literature has already validated as a matching strategy.
- **Time window:** 2015-2026 annual panel. 2015-2018 = pre-treatment baseline (trend check), 2018-Dec 2022 = compliance/mandate period, Dec 2022-2026 = post-injunction/unenforced period. May-Dec 2022 excluded from the core specification (ambiguous transition), included only as a robustness boundary.

## Identification strategy

**Primary:** two-event difference-in-differences / event-study design — CA-HQ (treated) vs. matched non-CA-HQ (control), around (1) the 2018 SB826 mandate and (2) the December 2022 injunction-reinstatement point — on network-topology outcomes.

**Secondary (heterogeneous treatment intensity):** using Gopal's (2022/2025) finding that SB826 cut CA all-male boards from 204 to 12, firms can be ranked by compliance-pressure intensity (e.g., were they all-male pre-2018, and how many new directors did they add). This tests whether firms under the greatest compliance pressure show the *least* structural change (strongest tokenism signal) or the *most* (strongest genuine-restructuring signal) — a within-treatment-group test that doesn't depend solely on the CA-vs-control contrast.

**Why not simpler alternatives:**
- A single before/after split at "2022" (no control group) was rejected — it can't separate a national trend (e.g., general post-2020 board-diversity momentum, ESG wave) from an SB826-specific effect. The matched-control design is what lets us attribute an effect to the mandate specifically, not the zeitgeist — this was flagged as a first-order confound risk for this exact design in the earlier session's scan and is addressed head-on here, not left as an unaddressed limitation.
- Treating the 2022 invalidation as a single sharp date was rejected once the actual injunction history (partial lift, then reinstatement) was verified — using an unverified sharp date would have been a factual error baked into the identification strategy.

## Variable definitions (operational)

| Construct | Operational definition |
|---|---|
| Network density | Proportion of realized ties in the director-board bipartite graph's board-projection, per year |
| Centralization | Freeman degree/betweenness centralization of the board-projection network, per year |
| Elite cohesion | Size of largest connected component + k-core structure, per year |
| Genuine restructuring (H1-alt support) | Statistically significant DiD effect on density/centralization AND low concentration index (below) |
| Isomorphic tokenism (H1 support) | Compliance-count change (all-male-board elimination) without corresponding density/centralization DiD effect, OR high concentration index |
| Concentration/tokenism index | Gini or HHI of the distribution of 2018-2022 new female-director appointments across unique individuals (high = small recycled pool; low = broad-based entry) |
| Reversion / freeze / continuation (H2) | Post-Dec-2022 trend in treated-firm network metrics relative to control: reversion toward pre-2018 trend line / flat at 2022 level / continued same-direction trend, tested via segmented regression on the panel |

## What Stage 3 does NOT resolve (deferred to Stage 4, and flagged as real risk, not hidden)

- Director name disambiguation across DEF 14A filings (no structured director-ID field in EDGAR) — the single largest engineering risk, previously flagged, unresolved by design work alone.
- Exact matched-control firm selection criteria (propensity-score vs. exact industry/size match) — to be finalized once real EDGAR data coverage is confirmed, not decided in the abstract.
- The cheap kill-test (hand-coded density/centralization for ~30 CA boards pre/post 2019) has not yet been run — this is the first concrete action of Stage 4, before any full-scale build.

## Reviewer #2 pass on Stage 3

**Objection 1 — is the Dec-2022 cutoff defensible or arbitrary?** Defensible as a documented judgment call given the real injunction history, but a reviewer will ask for the May-Dec-2022 sensitivity check to be shown, not just mentioned. Noted as a required robustness table for Stage 8, not optional.

**Objection 2 — does the heterogeneous-treatment-intensity design double-count with the DiD?** No — DiD identifies the average treatment effect (CA vs. control); the intensity design is a within-CA-sample test using Gopal's compliance data as a continuous moderator. Should be presented as complementary, and the paper must be explicit they answer different questions (average effect vs. dose-response) so a reviewer doesn't read it as a redundant robustness check.

**Objection 3 — matched-control construction is asserted, not yet specified precisely.** Correct, and left open on purpose: committing to exact-match vs. propensity-score matching before seeing real EDGAR coverage would be premature specification, not rigor. This gets finalized in Stage 4 once we know what the real data supports, and the choice will be documented and justified there, not silently decided now.

Stage 3 passes review with these three items carried forward as explicit, tracked obligations (not silently dropped) — logged in `PROJECT_LOG.md`.
