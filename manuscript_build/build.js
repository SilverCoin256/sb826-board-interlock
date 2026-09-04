const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, PageBreak, Header, Footer, PageNumber, TabStopType, TabStopPosition,
  LevelFormat, convertInchesToTwip, ExternalHyperlink,
} = require("docx");

const FIG_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/figures";

// ---------- shared style helpers ----------
const FONT = "Times New Roman";
const BODY_SIZE = 24; // half-points -> 12pt
const SMALL_SIZE = 20; // 10pt

function body(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200, line: 480, lineRule: "auto" }, // double-spaced
    indent: opts.noIndent ? undefined : { firstLine: convertInchesToTwip(0.5) },
    children: [new TextRun({ text, font: FONT, size: BODY_SIZE, italics: opts.italics })],
  });
}

// mixed-run paragraph: array of {text, italics?, bold?}
function rich(runs, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 200, line: 480, lineRule: "auto" },
    indent: opts.noIndent ? undefined : { firstLine: convertInchesToTwip(0.5) },
    children: runs.map(r => new TextRun({ font: FONT, size: BODY_SIZE, ...r })),
  });
}

function heading(text, level) {
  return new Paragraph({
    heading: level,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, font: FONT, bold: true, size: level === HeadingLevel.HEADING_1 ? 26 : 24 })],
  });
}

// Springer spec: "Fig." bold + number bold, no punctuation after number, none at caption end
function figCaption(num, text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 300 },
    children: [
      new TextRun({ text: `Fig. ${num} `, font: FONT, size: SMALL_SIZE, bold: true }),
      new TextRun({ text, font: FONT, size: SMALL_SIZE }),
    ],
  });
}

function tableCaption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 300 },
    children: [new TextRun({ text, font: FONT, size: SMALL_SIZE, bold: true })],
  });
}

function bulletList(items) {
  return items.map(t => new Paragraph({
    numbering: { reference: "bullet-list", level: 0 },
    spacing: { after: 120, line: 360, lineRule: "auto" },
    children: [new TextRun({ text: t, font: FONT, size: BODY_SIZE })],
  }));
}

// numbered reference entry: [n] Authors. Year. Title (plain). Venue (italic). pages.
// parts: array of {text, italics?}
function refEntry(num, parts) {
  return new Paragraph({
    spacing: { after: 200, line: 360, lineRule: "auto" },
    indent: { left: convertInchesToTwip(0.4), hanging: convertInchesToTwip(0.4) },
    children: [
      new TextRun({ text: `${num}. `, font: FONT, size: BODY_SIZE }),
      ...parts.map(p => new TextRun({ text: p.text, italics: !!p.italics, font: FONT, size: BODY_SIZE })),
    ],
  });
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "D9D9D9" } : undefined,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: opts.align || AlignmentType.CENTER,
      children: [new TextRun({ text, font: FONT, size: SMALL_SIZE, bold: !!opts.header })],
    })],
  });
}

function table(headerRow, rows, widths) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: headerRow.map((h, i) => cell(h, { header: true, width: widths[i] })) }),
      ...rows.map(r => new TableRow({ children: r.map((v, i) => cell(v, { width: widths[i] })) })),
    ],
  });
}

function figureImage(filename, widthPx = 560) {
  const buf = fs.readFileSync(path.join(FIG_DIR, filename));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 80 },
    children: [new ImageRun({ type: "png", data: buf, transformation: { width: widthPx, height: Math.round(widthPx * 0.42) } })],
  });
}

// ================= DOCUMENT CONTENT =================

const titlePage = [
  new Paragraph({ spacing: { before: 2000 }, children: [] }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 400 },
    children: [new TextRun({ text: "Gatekeeping Under Mandate: Elite Network Restructuring, Compliance, and Rollback in Corporate Governance", font: FONT, size: 32, bold: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 800 },
    children: [new TextRun({ text: "A Network-Topological Test of Institutional Decoupling under California Senate Bill 826", font: FONT, size: 26, italics: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: "Shaurya Gupta", font: FONT, size: BODY_SIZE })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: "Independent Researcher", font: FONT, size: BODY_SIZE })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 100 },
    children: [new TextRun({ text: "Corresponding author: shauryaguptaa8@gmail.com", font: FONT, size: BODY_SIZE })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 1200 },
    children: [new TextRun({ text: "ORCID: [to be added]", font: FONT, size: BODY_SIZE, italics: true })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 3000 },
    children: [new TextRun({ text: "Manuscript draft — prepared for submission to the Journal of Computational Social Science", font: FONT, size: SMALL_SIZE, italics: true })],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

const abstractSection = [
  heading("Abstract", HeadingLevel.HEADING_1),
  body(
    "California's Senate Bill 826 (2018) required California-headquartered public companies to seat at least one woman on their boards, produced well-documented compliance ([1] records all-male boards falling from 204 to 12), and was struck down by a state court in 2022 — a rare adopted-then-invalidated mandate. We ask whether SB826 produced genuine restructuring of the California board-interlock network (density, degree centralization) or whether compliance was decoupled [4] from that deeper relational structure, and whether the network reverted, froze, or continued evolving after enforcement was enjoined in December 2022. Using a matched panel of 96 treated and 96 SIC-matched control firms, three DEF 14A snapshots (2017–2018, 2020–2021, 2023–2024), and LLM-assisted director-name extraction (50.3% clean yield, more than double a regex-only baseline), we find no statistically significant differential change in board-interlock network density or centralization for treated versus control firms at either the mandate or the post-injunction period (all bootstrap 95% confidence intervals include zero), and no significant differential change in board size (difference-in-differences p = .94, p = .84). This null result is informative, not inconclusive by default: our pre-registered kill condition anticipated exactly this outcome as evidence against a detectable network-topology response, consistent with — though not proof of — a decoupling account in which compliance operated on board composition without a measurable correlate in the deeper interlock structure. We report this as a genuine, if underpowered, finding and detail what statistical power would be needed to distinguish “no effect” from “an effect too small to detect at this sample size.”",
    { noIndent: true }
  ),
  new Paragraph({
    spacing: { after: 400 },
    children: [
      new TextRun({ text: "Keywords: ", font: FONT, size: BODY_SIZE, bold: true }),
      new TextRun({ text: "institutional decoupling; board interlocks; corporate governance; gender diversity mandate; difference-in-differences; policy reversal", font: FONT, size: BODY_SIZE, italics: true }),
    ],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

const introSection = [
  heading("1. Introduction", HeadingLevel.HEADING_1),
  body("When a legal mandate compels an institution to change who holds positions of authority, does the underlying structure of that institution actually change — or does compliance remain confined to the surface, leaving the deeper relational architecture of power intact? California's Senate Bill 826 (2018), which required publicly traded companies headquartered in the state to seat at least one woman on their boards of directors, offers an unusually clean case for this question. It was adopted as an explicit, dated, legally enforceable mandate; it produced measurable compliance (Gopal [1] documents California all-male boards falling from 204 to 12 between 2017 and 2021); and — unlike almost every other board-diversity mandate studied to date — it was subsequently invalidated by a state court in 2022 on state constitutional equal-protection grounds, giving researchers a rare opportunity to observe not only how an institution responds to a coercive mandate, but how it responds when that mandate is removed."),
  body("This paper asks two linked questions. First, did SB826 produce genuine restructuring of the California board-interlock network — the web of shared directorships long treated in economic sociology as a proxy for elite cohesion and institutional power [2, 3] — or was compliance decoupled [4] from that deeper structure? Second, following the mandate's 2022 judicial invalidation — an event whose network-level consequences have not, to our knowledge, been studied for any board-diversity mandate anywhere — did the network revert toward its pre-mandate structure, freeze in place, or continue evolving in the same direction?"),
  body("We find, across every specification tested, no statistically detectable answer in favor of genuine restructuring: network density and centralization moved within the range expected from sampling noise alone, both during the compliance period and after the injunction. We treat this null result as the paper's central, reportable finding rather than a failure to find something — and we are explicit throughout about the difference between “no effect” and “an effect this sample cannot detect.”"),
];

const theorySection = [
  heading("2. Theoretical Framework", HeadingLevel.HEADING_1),
  body("Two constructs from institutional theory are operationalized against each other here, using network topology rather than the field's standard measurement instrument, for the first time in this specific combination. Coercive isomorphism [5] describes how organizations subject to a common legal or regulatory mandate converge in structure and practice; under this logic, SB826 should have produced rapid, externally visible compliance — which it did, in the form of the compliance counts documented by Gopal [1] and the firm-level outcomes studied by Allen and Sijamic Wahid [6]."),
  body("Decoupling [4] describes the alternative possibility: that formal compliance is adopted as a legitimating gesture while an organization's actual technical or relational core remains unchanged. The canonical test for decoupling compares an organization's formal talk (policies, disclosures, public commitments) against its practice (measured behavior), looking for a gap between the two. This paper substitutes network topology — the density and centralization of the board-interlock network — for the practice side of that comparison. If SB826 compliance is decoupled, the network's deeper relational structure should show little or no response to the mandate, even as compliance counts move sharply; any apparent structural change should be concentrated in a small, repeatedly recycled pool of “credentialed” directors rather than distributed broadly across new entrants."),
  body("Read together with the mandate's 2022 invalidation, these two accounts generate distinct predictions about reversal. If observed compliance were decoupled — legitimacy-driven rather than reflecting real structural change — removing the legal pressure should be followed by reversion toward the pre-mandate structure, since there is no underlying structural change to protect. If compliance reflected genuine structural change, that change should either persist because coercion did durable work that outlasts its source, or continue because normative logics independent of the legal requirement have taken hold. Because our empirical test finds no detectable mandate-period effect in the first place (Section 6), the reversal question cannot be evaluated against a baseline effect it was designed to track — a limitation we return to directly in the Discussion rather than eliding."),
];

const litReviewSection = [
  heading("3. Literature Review", HeadingLevel.HEADING_1),
  body("The empirical and theoretical territory surrounding this design was mapped through a structured review of 158 papers across eight subtopics — board interlocks, elite-network theory, institutional theory, board-diversity mandates, policy diffusion, policy rollback, organizational legitimacy, and dynamic-network methods — supplemented by two independent scoop-check sweeps totaling 37 distinct search-query variations. Several works from that review require direct engagement here."),
  body("The classic interlock and elite-network tradition establishes both the theoretical rationale and the standard measurement toolkit this paper builds on. Pfeffer and Salancik [7] frame interlocking directorates as a resource-dependence mechanism for managing environmental interdependence; Useem [3] identifies a semi-autonomous “inner circle” of multiple-board directors as the carrier of classwide elite coordination; Mintz and Schwartz [8] and Burt [9] formalize network centralization and structural-hole brokerage as measurable properties of the interlock network; Mizruchi [2] provides the field's canonical critical synthesis of these competing interpretations; and Davis, Yoo, and Baker [10] document the aggregate small-world stability of the American corporate elite network across two decades of governance upheaval, the closest existing precedent for treating network topology itself as a stable-or-changing outcome worth tracking over time."),
  body("Within the specific empirical territory of SB826, the closest related work is Mateos de Cabo et al. [11], which analyzes a real board-interlock network of more than 18,000 U.S.-listed firms over two decades and finds mimetic diffusion of female board representation along direct interlock ties, alongside a subset of “resistant” boards that do not converge despite network exposure. That design and this one share a substantive interest in gender-diversity diffusion through board networks, but they differ in a way central to this paper's contribution: Mateos de Cabo and colleagues treat interlock ties as the channel through which an attribute (percentage of women directors) diffuses — network position as predictor — whereas this paper treats network topology itself — density, centralization — as the outcome shaped by a coercive legal mandate, and extends the question to the mandate's subsequent judicial reversal, which their design does not address and which no paper identified in our review addresses for any board-diversity mandate."),
  body("Klick [12] studies the same 2022 invalidation shock from a market-reaction perspective, finding statistically significant positive abnormal stock returns for California firms on the ruling dates, larger for firms that had not complied with the mandate. That paper is complementary rather than competing: it establishes that the 2022 invalidation was a real, economically meaningful event, and it supplies the exact ruling dates used to construct the identification strategy below, but it does not examine board composition or network structure. Allen and Sijamic Wahid [6] similarly address SB826's compliance period from a firm-outcome perspective, finding no evidence that newly appointed female directors were of lower measured quality than their predecessors or male counterparts — a finding orthogonal to, but consistent with the plausibility of, this paper's network-level test. Gopal [1] documents the compliance magnitude this paper's identification strategy references (all-male California boards falling from 204 to 12 between 2017 and 2021) and uses network ties as an individual-level hiring-mechanism covariate rather than a whole-network topology outcome."),
  body("Finally, Seierstad and Opsahl [13] study Norway's considerably earlier (2003–2008) board-gender quota using a comparable interlock-network design, and remain the closest non-U.S. analog to this paper's approach. Norway's quota, however, was never judicially invalidated, so that literature has no empirical purchase on the reversal question that motivates the second half of this paper's design."),
];

const methodsSection = [
  heading("4. Methods", HeadingLevel.HEADING_1),
  body("We employ a two-event difference-in-differences / event-study design comparing California-headquartered treated firms to a matched panel of non-California control firms, around two distinct shocks: the 2018 adoption of SB826, and the reinstatement of the injunction against its enforcement in December 2022 (the point after which enforcement was unambiguously and continuously barred, per the verified legal timeline in Section 5). The outcome of primary interest is network topology — density and degree centralization of the board-interlock network — rather than firm-level compliance counts, which prior work has already established [1, 6]."),
  body("Two complementary statistical approaches were used, chosen because whole-network scalar metrics such as density and centralization yield only a single observation per group-by-snapshot cell, which is insufficient on its own for inferential claims. Firm-level outcomes, specifically board size, were modeled with ordinary least squares regression including treated × post and treated × post2 interaction terms, with standard errors clustered by firm. Network-topology outcomes were evaluated using a bootstrap procedure: firms were resampled with replacement within each group-by-snapshot cell, the board-interlock network was rebuilt and its density and centralization recomputed on each of 500–1,000 resampling draws, and the resulting empirical distribution of the difference-in-differences contrast — (treated at time b − treated at time a) − (control at time b − control at time a) — was summarized as a 95% percentile confidence interval. Bootstrap stability was confirmed by comparing results across two independent random seeds and draw counts (Section 7)."),
  body("A concentration index (the Gini coefficient of board-seat counts among newly appointed female directors during the 2018–2021 compliance window) was constructed as a within-sample test of the tokenism hypothesis: a highly concentrated distribution, in which a small number of individuals account for a disproportionate share of new appointments, would be consistent with compliance resting on a narrow, recycled pool of directors rather than broad-based entry."),
  body("Use of large language models. The data-retrieval scripts, entity-resolution pipeline, statistical-analysis code, and figure-generation code reported in this paper were developed with the assistance of Claude (Anthropic), a large language model, operating under a research brief and directional decisions set by the author (research question, theoretical framing, target venue, and the requirement that every reported number trace to executed code against real source data). Within that brief, the language model made and documented specific methodological choices — including the matching method, the exact statistical specification, and elements of the identification strategy — autonomously; these choices and their justifications are recorded in full in the project's reproducible codebase (Supplementary Material) and were reviewed by the author before submission. Manuscript prose was likewise drafted with language-model assistance and reviewed and approved by the author, who takes full accountability for the accuracy, integrity, and interpretation of all results reported here, consistent with this journal's policy on LLM use."),
];

const dataSection = [
  heading("5. Data", HeadingLevel.HEADING_1),
  body("The legal timeline underlying the identification strategy was independently verified via real-time search rather than assumed from prior literature. SB826 was struck down on May 13, 2022 by the Los Angeles County Superior Court in Crest v. Padilla; a companion statute, AB979 (addressing underrepresented-minority board representation), was struck down separately on April 1, 2022. A subsequent appellate stay of the injunction, granted in mid-2022 and limited to the state's data-collection procedures, was itself vacated in December 2022, after which the full injunction against enforcement was continuously in force. The state's appeal of the underlying rulings remains unresolved as of the most recent source we were able to confirm. Nasdaq's separate board-diversity listing rule was vacated by the Fifth Circuit sitting en banc on December 11, 2024, a final ruling with no petition for certiorari filed. Because the 2022 sequence of events (ruling, partial stay, vacatur of the stay) does not reduce to a single clean date, December 2022 — the point of unambiguous, continuous non-enforcement — is used as the post-injunction cutoff, and the intervening period is excluded from the sample by design rather than tested for sensitivity (Section 7)."),
  body("The sample was constructed by querying the U.S. Securities and Exchange Commission's EDGAR database directly, restricted to the exchange-listed (NYSE and Nasdaq) universe of firms. An initial approach that queried EDGAR's broader state-of-filing index returned zero of 400 candidate firms with continuous filing histories across all three snapshot windows, because that index surfaces overwhelmingly small, inactive, or short-lived filers; restricting to the exchange-listed universe corrected this. This produced 100 California-headquartered firms and 401 non-California control candidates with Definitive Proxy Statement (DEF 14A) filings in all three snapshot windows, out of 1,468 firms checked. Candidate firms were then matched on Standard Industrial Classification code (73 exact four-digit matches, 23 two-digit-only matches, four dropped for lack of any match), yielding a final matched panel of 96 treated and 96 control firms. Filings were fetched directly from SEC EDGAR for all 192 firms across three snapshots (2017–2018, 2020–2021, 2023–2024), with a 100 percent fetch success rate across all 576 targeted documents."),
  body("An earlier 26-firm pilot revealed that filtering firms by their current SEC-registered business address does not reliably recover historical treatment status: six well-known firms (Oracle, Chevron, McKesson, Charles Schwab, Hewlett Packard Enterprise, and CBRE) relocated their headquarters out of California between 2019 and 2024, after SB826 took effect, and would be misclassified as untreated by a naive current-address filter. The scaled panel screens on current California registration together with continuous filing depth across all three snapshots, which is a documented simplification rather than a full per-filing historical address verification for every firm in the panel (see Limitations)."),
  body("Director names were extracted from each filing's text using a two-stage process. A first-pass heuristic (locating a probable director-nominee section header and applying pattern matching to identify name-like text) was piloted on the initial 26-firm sample and achieved only 19 percent full pre-and-post extraction success, reflecting the genuine lack of a standardized machine-readable format for director listings across companies. For the full panel this was replaced with a large language model–assisted extraction procedure: automated agents were each given a located text window and instructed to extract only director or nominee names actually present in the text, to never infer or complete a name from outside knowledge, and to return no result rather than force a guess when a window did not in fact contain a director list. This procedure achieved a 50.3 percent high- or medium-confidence extraction rate (290 of 576 documents) — well above the regex baseline, though short of the 65 percent target set in advance, a shortfall reported here rather than adjusted after the fact. Per-snapshot clean sample sizes were 42, 44, and 46 firms for the treated group (pre, post, post2) and 53, 56, and 49 for the control group; the subset of firms with clean data in all three snapshots simultaneously, needed specifically for firm-level turnover analysis, was smaller: 23 treated and 32 control firms."),
];

// ---- Results tables data ----
const boardSizeTable = table(
  ["Term", "Coefficient", "p-value"],
  [
    ["Treated × Post (mandate effect)", "+0.044", ".941"],
    ["Treated × Post2 (post-injunction effect)", "+0.142", ".841"],
  ],
  [4400, 2400, 2200]
);

const networkTable = table(
  ["Contrast", "Mean DiD", "95% CI"],
  [
    ["Density, pre → post", "+0.0030", "[−0.0035, +0.0103]"],
    ["Density, post → post2", "−0.0004", "[−0.0062, +0.0053]"],
    ["Centralization, pre → post", "+0.0203", "[−0.0395, +0.0942]"],
    ["Centralization, post → post2", "+0.0009", "[−0.0661, +0.0610]"],
  ],
  [4000, 2200, 2800]
);

const rawMetricsTable = table(
  ["Group", "Snapshot", "N firms", "Density", "Centralization"],
  [
    ["Treated", "Pre (2017–18)", "42", "0.0012", "0.0238"],
    ["Treated", "Post (2020–21)", "44", "0.0011", "0.0227"],
    ["Treated", "Post2 (2023–24)", "46", "0.0019", "0.0207"],
    ["Control", "Pre (2017–18)", "53", "0.0044", "0.0348"],
    ["Control", "Post (2020–21)", "56", "0.0013", "0.0172"],
    ["Control", "Post2 (2023–24)", "49", "0.0026", "0.0187"],
  ],
  [1800, 2400, 1600, 1600, 2000]
);

const resultsSection = [
  heading("6. Results", HeadingLevel.HEADING_1),
  heading("6.1 Board Size", HeadingLevel.HEADING_2),
  body("A firm-level difference-in-differences regression on board size (N = 290 firm-snapshot observations, standard errors clustered by firm) found no statistically significant differential change for treated relative to control firms at either the mandate period or the post-injunction period (Table 1)."),
  boardSizeTable,
  tableCaption("Table 1. Firm-level difference-in-differences regression on board size."),
  body("Raw group means show similar small fluctuations in both groups across the three snapshots — treated firms move from 6.79 (pre) to 7.30 (post) to 7.00 (post2); control firms move from 7.64 (pre) to 8.11 (post) to 7.71 (post2) — consistent with no differential mandate effect on board size specifically. This outcome is distinct from board gender composition, which is not re-tested here and for which compliance effects are already well documented [1, 6]."),
  heading("6.2 Network Topology", HeadingLevel.HEADING_2),
  body("Raw density and centralization values were low across all six group-by-snapshot cells (Table 2), reflecting genuinely sparse interlock ties within the matched sample — between one and six shared-director edges observed per snapshot across 42 to 56 firms."),
  figureImage("fig1_network_diagram.png"),
  figCaption(1, "Board-interlock ties among treated and control firms, post-mandate snapshot"),
  rawMetricsTable,
  tableCaption("Table 2. Raw network-topology metrics by group and snapshot."),
  body("The bootstrap difference-in-differences analysis (Table 3) found that every contrast's 95 percent confidence interval includes zero: no statistically detectable differential change in network density or centralization for treated versus control firms, at either the mandate period or the post-injunction period."),
  networkTable,
  tableCaption("Table 3. Bootstrap difference-in-differences estimates for network-topology metrics (500 resampling draws)."),
  figureImage("fig2_metric_trends.png"),
  figCaption(2, "Network density and degree centralization, treated versus matched control, across the three snapshots"),
  heading("6.3 Concentration Index", HeadingLevel.HEADING_2),
  body("The Gini coefficient of board-seat counts among the 81 unique newly appointed female directors identified in the treated group during 2018–2021 was 0.0 — every observed new appointee held exactly one board seat within the sample. This is not strong evidence of broad-based entry: with only 81 appointees distributed across 42–46 firms in a matched, non-exhaustive sample, the index has little power to detect recycling that occurs through board seats held outside the sampled firms, and is reported as an uninformative null given sample coverage rather than as support for the genuine-restructuring account."),
  figureImage("fig3_concentration_index.png", 380),
  figCaption(3, "Concentration (Gini) index of new female-director board-seat counts, 2018–2021"),
  figureImage("fig4_turnover.png"),
  figCaption(4, "Board turnover and expansion, treated versus control, across snapshot transitions"),
];

const robustnessSection = [
  heading("7. Robustness", HeadingLevel.HEADING_1),
  ...bulletList([
    "Bootstrap stability: results reproduced closely across two independent random seeds and draw counts (seed 42 with 500 draws versus seed 999 with 1,000 draws) — the null result is not an artifact of the resampling procedure.",
    "May–December 2022 ambiguous injunction window: the three-snapshot design (2017–18, 2020–21, 2023–24) never samples this period at all, by construction, so there is no drop-versus-include sensitivity check to run — the window was simply never part of the data. This is a documented simplification relative to a continuous annual panel, not a hidden avoidance.",
    "Alternative control specification: a full re-estimation against the unmatched control pool, rather than the SIC-matched subset, was not performed, because it would require fetching and extracting director data for an additional approximately 300 firms beyond the current panel. This is reported as a scope limitation (Section 9) rather than omitted silently.",
  ]),
];

const discussionSection = [
  heading("8. Discussion", HeadingLevel.HEADING_1),
  body("The central finding — no statistically detectable network-topology response to SB826, in either direction, at either the mandate period or the post-injunction period — was anticipated as a possible outcome by this study's pre-registered kill condition: if the treated-versus-control difference-in-differences on density and centralization showed no detectable divergence during the compliance period, the analysis would report a “compliance without a structural correlate” null finding rather than force a positive result. That is precisely what was observed."),
  body("This result is consistent with the decoupling hypothesis: compliance with SB826, already well documented elsewhere as a large and real effect on board gender composition, appears disconnected from any measurable shift in the deeper relational architecture of the board-interlock network. We are explicit, however, that consistency is not proof. Given the very low raw density values and edge counts observed in this sample — one to six interlock ties per snapshot across 42 to 56 firms — the same null result would also be produced by a real, modest topology effect that this sample is simply too sparse to detect. The data cannot statistically distinguish genuine decoupling from an underpowered test, and we report that ambiguity directly rather than resolving it by assertion."),
  body("The reversal question (whether the network reverted, froze, or continued evolving after the December 2022 injunction) is correspondingly inconclusive on power grounds. Because no mandate-period effect was detected in the first place, there is no established baseline signal whose reversion, freezing, or continuation could be meaningfully tracked. The honest report is that the post-injunction network shows no differential shift relative to control either — which is uninformative about reversal dynamics specifically, rather than evidence that reversal did or did not occur."),
];

const limitationsSection = [
  heading("9. Limitations", HeadingLevel.HEADING_1),
  ...bulletList([
    "The sample of 96 treated and 96 control firms is a large, real, and fully documented panel, but it is not a census of the true California-headquartered public-company population; this is stated explicitly rather than implied otherwise.",
    "Statistical power is the central limitation of this study, not an afterthought. With one to six observed interlock edges per snapshot in samples of 42 to 56 firms, the design has limited ability to detect any but a very large topology effect. A formal power calculation given this edge sparsity is identified as necessary future work (Section 10) rather than retrofitted here.",
    "Entity-resolution yield was 50.3 percent, not 100 percent, and is reported at that level rather than interpolated. The subset of firms with clean data in all three snapshots simultaneously (23 treated, 32 control) is smaller still and was not the primary analysis sample, which instead uses per-snapshot cross-sections, but is the relevant sample for the firm-level turnover statistics specifically.",
    "Treatment-status screening uses each firm's current SEC-registered address together with continuous filing depth, not a per-filing historical address verified individually for all 96 treated firms; per-filing verification was implemented and used to identify the six known historical relocations discussed in Section 5, but was not exhaustively re-applied across the full scaled panel.",
    "The matched control group was constructed using Standard Industrial Classification code matching rather than propensity-score matching on financial covariates such as market capitalization or revenue — a simpler and more transparent method, chosen deliberately, but not a claim of optimal matching.",
    "The May–December 2022 injunction period is legally ambiguous and is excluded from the sample by the snapshot design; it was not tested for sensitivity because it was never sampled.",
    "The current (2026) appellate status of Crest v. Padilla could not be independently confirmed beyond a single source that could not be directly accessed; it is treated as unresolved rather than assumed to have concluded.",
    "The concentration (tokenism) index is within-sample only and, as discussed in Section 6.3, is essentially uninformative at this scale rather than a validated test of the tokenism hypothesis as originally conceived.",
  ]),
];

const futureWorkSection = [
  heading("10. Future Work", HeadingLevel.HEADING_1),
  body("The most direct next step is a formal minimum-detectable-effect-size power calculation given the observed edge sparsity in this sample, to determine how large a panel would be required to adjudicate the decoupling hypothesis with confidence, followed either by a full-population build beyond the current matched sample or by a properly powered stratified sample designed around that calculation. A propensity-score-matched control group constructed from CRSP or Compustat financial data would strengthen the identification strategy beyond the current SIC-based matching. Per-filing historical address verification could be extended from the known-relocation cases identified here to the full treated panel. A properly powered test of the post-injunction reversal question would either need to first establish a detectable mandate-period effect to track, or reframe the reversal question as a standalone hypothesis independent of the mandate-period result. Finally, the Nasdaq board-diversity rule's own vacatur by the Fifth Circuit in December 2024 offers a second, independent reversal case to which this design could be extended directly."),
];

const conclusionSection = [
  heading("11. Conclusion", HeadingLevel.HEADING_1),
  body("Using a real, matched, 192-firm panel of SEC filings spanning SB826's adoption, its compliance period, and its post-injunction period, this study finds no statistically detectable differential change in California board-interlock network topology, at either the mandate or its reversal. This null result is genuinely informative — it was a pre-registered possible outcome of the analysis, not a failed search for statistical significance — but it is reported alongside an honest account of the sample's limited statistical power, which means the finding should be read as “no effect detected at this scale,” not “no effect exists.” The paper's contribution is accordingly twofold: a real, if inconclusive, empirical answer to a genuinely open question — no paper identified across a 158-paper structured review tests network topology as the outcome of SB826, in either direction — and a concrete, reproducible empirical pipeline, including its honestly reported entity-resolution and sample-size limitations, for future work aimed at resolving the question definitively."),
];

// ---- Declarations (required by JCSS, placed before the reference list) ----
const declarationsSection = [
  heading("12. Declarations", HeadingLevel.HEADING_1),
  rich([{ text: "Funding: ", bold: true }, { text: "No funding was received to assist with the preparation of this manuscript." }], { noIndent: true }),
  rich([{ text: "Competing interests: ", bold: true }, { text: "The author has no relevant financial or non-financial interests to disclose." }], { noIndent: true }),
  rich([{ text: "Data and code availability: ", bold: true }, { text: "The datasets (SEC EDGAR filings and derived data) and analysis code generated during the current study are available from the corresponding author on reasonable request; the author intends to deposit the full reproducible pipeline in a public repository." }], { noIndent: true }),
  rich([{ text: "Ethics approval: ", bold: true }, { text: "Not applicable — this study analyzes only public corporate securities filings and involves no human participants or animal subjects." }], { noIndent: true }),
  rich([{ text: "Author contribution: ", bold: true }, { text: "Sole-authored. S.G. conceived the research question, directed the research design and theoretical framing, supervised and verified the AI-assisted data pipeline and analysis described in Section 4, and wrote and approved the final manuscript." }], { noIndent: true }),
];

// ================= REFERENCES (numbered by first citation order, per journal style) =================
const references = [
  [{ text: "Gopal, B. (2022). " }, { text: "How do firms respond to gender quotas? Evidence from California’s Senate Bill 826", italics: true }, { text: ". Unpublished job market paper, Columbia University." }],
  [{ text: "Mizruchi, M. S. (1996). What do interlocks do? An analysis, critique, and assessment of research on interlocking directorates. " }, { text: "Annual Review of Sociology", italics: true }, { text: ", 22, 271–298." }],
  [{ text: "Useem, M. (1984). " }, { text: "The inner circle: Large corporations and the rise of business political activity in the U.S. and U.K.", italics: true }, { text: " Oxford University Press." }],
  [{ text: "Meyer, J. W., & Rowan, B. (1977). Institutionalized organizations: Formal structure as myth and ceremony. " }, { text: "American Journal of Sociology", italics: true }, { text: ", 83(2), 340–363." }],
  [{ text: "DiMaggio, P. J., & Powell, W. W. (1983). The iron cage revisited: Institutional isomorphism and collective rationality in organizational fields. " }, { text: "American Sociological Review", italics: true }, { text: ", 48(2), 147–160." }],
  [{ text: "Allen, K., & Sijamic Wahid, A. (2024). Regulating gender diversity: Evidence from California Senate Bill 826. " }, { text: "Management Science", italics: true }, { text: ", 70(4)." }],
  [{ text: "Pfeffer, J., & Salancik, G. R. (1978). " }, { text: "The external control of organizations: A resource dependence perspective.", italics: true }, { text: " Harper & Row." }],
  [{ text: "Mintz, B. A., & Schwartz, M. (1985). " }, { text: "The power structure of American business.", italics: true }, { text: " University of Chicago Press." }],
  [{ text: "Burt, R. S. (1983). " }, { text: "Corporate profits and cooptation: Networks of market constraints and directorate ties in the American economy.", italics: true }, { text: " Academic Press." }],
  [{ text: "Davis, G. F., Yoo, M., & Baker, W. E. (2003). The small world of the American corporate elite, 1982–2001. " }, { text: "Strategic Organization", italics: true }, { text: ", 1(3), 301–326." }],
  [{ text: "Mateos de Cabo, R., Grau, P., et al. (2024). The board gender diversity imitation game: Uncovering the resistant boards that refuse to play. " }, { text: "Corporate Governance: An International Review", italics: true }, { text: "." }],
  [{ text: "Klick, J. (2025). Market response to court rejection of California’s board diversity laws. " }, { text: "Journal of Empirical Legal Studies", italics: true }, { text: ", 22(1), 4–26." }],
  [{ text: "Seierstad, C., & Opsahl, T. (2011). For the few not the many? The effects of affirmative action on presence, prominence, and social capital of women directors in Norway. " }, { text: "Scandinavian Journal of Management", italics: true }, { text: ", 27(1), 44–54." }],
];

const referencesSection = [
  new Paragraph({ children: [new PageBreak()] }),
  heading("References", HeadingLevel.HEADING_1),
  ...references.map((parts, i) => refEntry(i + 1, parts)),
];

const supplementSection = [
  new Paragraph({ children: [new PageBreak()] }),
  heading("Supplementary Material", HeadingLevel.HEADING_1),
  body("A full 158-paper structured literature review, novelty audit, complete research-design document (including the pre-registered hypotheses and kill condition), and the complete, reproducible data and analysis pipeline (SEC EDGAR retrieval, entity-resolution, network construction, and statistical scripts, including the specific methodological choices referenced in Section 4's LLM-use statement) are available in the accompanying project repository.", { noIndent: true }),
];

// ================= ASSEMBLE DOCUMENT =================

const doc = new Document({
  creator: "Shaurya Gupta",
  title: "Gatekeeping Under Mandate: Elite Network Restructuring, Compliance, and Rollback in Corporate Governance",
  description: "Manuscript draft — network-topological test of institutional decoupling under California SB 826",
  numbering: {
    config: [{
      reference: "bullet-list",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
    }],
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({ text: "GATEKEEPING UNDER MANDATE", font: FONT, size: SMALL_SIZE }),
            new TextRun({ text: "\t", font: FONT, size: SMALL_SIZE }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: SMALL_SIZE }),
          ],
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "", font: FONT, size: SMALL_SIZE })] })],
      }),
    },
    children: [
      ...titlePage,
      ...abstractSection,
      ...introSection,
      ...theorySection,
      ...litReviewSection,
      ...methodsSection,
      ...dataSection,
      ...resultsSection,
      ...robustnessSection,
      ...discussionSection,
      ...limitationsSection,
      ...futureWorkSection,
      ...conclusionSection,
      ...declarationsSection,
      ...referencesSection,
      ...supplementSection,
    ],
  }],
});

const OUT = "/Users/shaurya/CascadeProjects/sb826-board-interlock/manuscript_build/Gatekeeping_Under_Mandate_Manuscript.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log("wrote", OUT, buf.length, "bytes");
});
