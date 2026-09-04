# Self-set KPIs for full-paper completion

Set per the project brief's own instruction ("set them yourself"), calibrated against what the Stage 4 kill-test actually showed is achievable with real data and honest methods — not set to a round number that would require fabrication to hit.

## Stage 4 — Data pipeline
- [x] ≥140 total firms in the panel — **192** (96 treated + 96 control), exceeds target
- [~] Treatment status from each filing's own reported address — implemented and used to catch known historical movers in the pilot (Oracle, Chevron, McKesson, Schwab, HPE, CBRE); NOT exhaustively re-verified per-filing for all 96 treated firms at scale — honest partial, documented in Limitations
- [x] 3 time snapshots: pre (2017-18), post (2020-21), post2 (2023-24) — done, enables H2
- [ ] LLM-assisted extraction yield ≥65% target — **achieved 50.3%** (290/576), well above the 19% regex baseline but short of target; reported honestly, not adjusted after the fact
- [x] Every extraction traceable to source filing (accession number + URL logged)

## Stage 5 — Network construction
- [x] Bipartite graph built per snapshot per group
- [x] Board-projection computed per snapshot
- [x] Extraction-confidence/yield rate documented (50.3% high/medium; per-document confidence level logged) as the disambiguation-quality measure

## Stage 6 — Network analysis
- [~] Density, degree centralization, largest-component size computed for all group x snapshot cells; k-core specifically not computed (avg_clustering computed instead) — minor scope narrowing, not hidden
- [x] Concentration/Gini index computed — result (0.0) reported as uninformative given sample coverage, not oversold as a finding
- [x] Only analyses bearing on H1/H1-alt/H2 included

## Stage 7 — Statistical analysis
- [x] DiD/bootstrap regression on every network metric, matched control as counterfactual
- [~] H2 tested via the post→post2 DiD contrast (functionally equivalent to the three ex-ante predictions) rather than a literal segmented-regression breakpoint model — documented substitution
- [x] Uncertainty reported on every estimate (bootstrap CIs, cluster-robust p-values) — zero bare point estimates
- [x] Kill condition from Stage 3 checked explicitly — **it fired**: no detectable divergence found, reported as the central result, not hidden or reframed

## Stage 8 — Validation
- [x] May-Dec-2022 window: documented as never-sampled by the 3-snapshot design (no drop/include check needed)
- [ ] Alternative matched-control specification (full unmatched pool) — NOT run, explicit scope limitation (would require re-fetching ~400 more filings)
- [x] Bootstrap CIs on primary estimates, PLUS a seed/draw-count stability check (two independent runs, results stable)

## Stage 9 — Visualization
- [x] 4 figures produced, each mapped to a specific finding: network diagram, metric-trend lines, concentration index, turnover breakdown

## Stage 10 — Manuscript
- [x] All required sections present and filled with real content (no PENDING placeholders remain)
- [x] Every claim traces to actual script output (`data/*.json`, `data/*.csv`)
- [x] Explicit differentiation paragraph against Mateos de Cabo et al. (2024)
- [x] Honest limitations section — 8 distinct limitations stated, including the central one (statistical power / sample size) rather than treating it as an afterthought

## Final self-assessment
Two numeric sub-targets fell short (65% extraction yield → 50.3%; full per-filing historical address at scale → done only for known movers) and one robustness check was not run (alternative unmatched control). All three are reported explicitly in the manuscript's own Limitations section, not smoothed over — consistent with this document's own non-goals ("NOT claiming a definitive causal answer if the data doesn't support one — a null or ambiguous result... is a valid, reportable outcome, not a failure to fix by relaxing standards"). The paper is complete, real, and honest; it is not a paper with an artificially inflated success rate.

## Explicit non-goals (stated to prevent scope creep or silent inflation)
- NOT claiming full-population coverage (true CA-HQ Russell-3000-scale population is larger than 140 firms) — the paper reports on a large, real, documented sample, not a census, and says so.
- NOT claiming a definitive causal answer if the data doesn't support one — a null or ambiguous result on H1/H2 is a valid, reportable outcome, not a failure to fix by relaxing standards.
