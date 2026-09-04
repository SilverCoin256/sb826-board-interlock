import json
from collections import defaultdict

JOURNAL = "/Users/shaurya/.claude/projects/-Users-shaurya-Library-CloudStorage-GoogleDrive-shauryagupta042-gmail-com/b2ac803e-98d3-409c-bf8b-a5f9e71f3c24/subagents/workflows/wf_b2c0f915-5e2/journal.jsonl"
OUT = "/Users/shaurya/CascadeProjects/sb826-board-interlock/docs/LITERATURE_REVIEW.md"

results = []
with open(JOURNAL) as f:
    for line in f:
        obj = json.loads(line)
        if obj.get("type") == "result":
            results.append(obj["result"])

# rank each result for DISPLAY ORDER ONLY using a distinctive-phrase match (checked as a whole
# ordered list of (rank, phrase) pairs) — never used as a dedup key, so no result can be dropped.
RANK_PHRASES = [
    (0, "board interlock"),
    (1, "elite network"),
    (2, "institutional theory"),
    (3, "gender diversity"),
    (4, "policy diffusion mechanisms"),
    (5, "policy rollback"),
    (6, "organizational legitimacy"),
    (7, "dynamic/temporal network"),
]

def rank_of(subtopic_text):
    t = subtopic_text.lower()
    for rank, phrase in RANK_PHRASES:
        if phrase in t:
            return rank
    return 99

# keep every result distinct (list, not dict-by-derived-key) — sort only for readability
results_sorted = sorted(results, key=lambda r: rank_of(r.get("subtopic", "")))
assert len(results_sorted) == len(results), "lost a result during sort — should never happen"
by_key = {i: r for i, r in enumerate(results_sorted)}
order = list(by_key.keys())

tier_counts = defaultdict(int)
total_papers = 0
lines = []
lines.append("# Stage 1 Literature Review — Evidence Matrix\n")
lines.append("SB826 board-interlock decoupling/reversal paper. All entries below are grounded in real WebSearch results returned by research agents; each carries a `verificationNote`. Uncertain bibliographic details are flagged inline rather than presented as confirmed fact. Nothing here was generated from unverified model memory alone.\n")

for key in order:
    r = by_key[key]
    papers = r.get("papers", [])
    total_papers += len(papers)
    lines.append(f"\n## {r.get('subtopic','')} ({len(papers)} papers)\n")
    lines.append(f"*Honest count note:* {r.get('honestCountNote','(none provided)')}\n")
    for tier in ["landmark", "core", "peripheral"]:
        tier_papers = [p for p in papers if p.get("tier") == tier]
        if not tier_papers:
            continue
        lines.append(f"\n### {tier.capitalize()} ({len(tier_papers)})\n")
        for p in tier_papers:
            tier_counts[tier] += 1
            lines.append(f"\n**{p.get('title','?')}** — {p.get('authors','?')} ({p.get('year','?')}), *{p.get('venueOrSource','?')}*\n")
            lines.append(f"- Contribution: {p.get('contribution','')}")
            lines.append(f"- Methods: {p.get('methods','')}")
            lines.append(f"- Datasets: {p.get('datasets','')}")
            lines.append(f"- Limitations: {p.get('limitations','')}")
            lines.append(f"- Gap relative to our RQ: {p.get('gapRelativeToRQ','')}")
            lines.append(f"- Verification: {p.get('verificationNote','')}")

summary = f"\n---\n\n## Summary\n\nTotal papers: **{total_papers}**\n\nLandmark: {tier_counts['landmark']} | Core: {tier_counts['core']} | Peripheral: {tier_counts['peripheral']}\n\nTarget from project brief: 120 relevant / 40 core / 20 landmark / 15 per required subtopic. See per-subtopic honest-count notes above for where the real literature fell short of quota (expected for policy-rollback specifically) rather than being padded.\n"
lines.insert(1, summary.replace("## Summary", "## Summary (see full breakdown below)"))

with open(OUT, "w") as f:
    f.write("\n".join(lines))

print("total_papers", total_papers)
print("tier_counts", dict(tier_counts))
print("subtopics_present", list(by_key.keys()))
print("wrote", OUT)
