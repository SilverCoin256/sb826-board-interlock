"""
Stage 9: publication-quality figures. Each communicates one specific
finding, per the KPI list -- not decorative.
"""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import re

DATA_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data"
FIG_DIR = "/Users/shaurya/CascadeProjects/sb826-board-interlock/figures"
import os
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({"font.size": 11, "figure.dpi": 150, "savefig.dpi": 150})


def norm(name):
    n = name.lower()
    n = re.sub(r"^(dr\.|mr\.|ms\.|mrs\.)\s*", "", n)
    n = re.sub(r"[^a-z ]", "", n)
    return re.sub(r"\s+", " ", n).strip()


def fig1_network_diagram():
    with open(f"{DATA_DIR}/clean_directors.json") as f:
        data = json.load(f)
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    for ax, group in zip(axes, ["treated", "control"]):
        period_dict = data[group]["post"]
        B = nx.Graph()
        for firm, directors in period_dict.items():
            B.add_node(("firm", firm), bipartite=0)
            for d in directors:
                dn = ("director", norm(d))
                B.add_node(dn, bipartite=1)
                B.add_edge(("firm", firm), dn)
        firm_nodes = [n for n, d in B.nodes(data=True) if d["bipartite"] == 0]
        proj = nx.bipartite.weighted_projected_graph(B, firm_nodes) if len(firm_nodes) > 1 else nx.Graph()
        pos = nx.spring_layout(proj if proj.number_of_nodes() else B, seed=1)
        nx.draw_networkx_nodes(proj, pos, ax=ax, node_size=60, node_color="#2b6cb0" if group == "treated" else "#718096")
        nx.draw_networkx_edges(proj, pos, ax=ax, alpha=0.4)
        ax.set_title(f"{group.capitalize()} firms, post-mandate (board-interlock ties)")
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig1_network_diagram.png")
    plt.close()
    print("wrote fig1_network_diagram.png")


def fig2_metric_trends():
    df = pd.read_csv(f"{DATA_DIR}/network_metrics_long.csv")
    order = ["pre", "post", "post2"]
    df["snapshot"] = pd.Categorical(df["snapshot"], categories=order, ordered=True)
    df = df.sort_values("snapshot")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, metric in zip(axes, ["density", "degree_centralization"]):
        for group, style in [("treated", "-o"), ("control", "--s")]:
            sub = df[df.group == group]
            ax.plot(sub["snapshot"], sub[metric], style, label=group)
        ax.set_title(metric)
        ax.axvline(0.5, color="gray", linestyle=":", alpha=0.6)
        ax.legend()
    plt.suptitle("Network-topology metrics, treated vs. matched control, across snapshots")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig2_metric_trends.png")
    plt.close()
    print("wrote fig2_metric_trends.png")


def fig3_concentration():
    with open(f"{DATA_DIR}/concentration_index.json") as f:
        conc = json.load(f)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(["Gini of new-appointee\nboard-seat counts"], [conc["gini_of_appointment_counts"]], color="#c05621")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Gini coefficient (0=broad-based, 1=fully concentrated)")
    ax.set_title(f"Tokenism/concentration index\n(n={conc['n_unique_new_appointees']} unique new appointees, "
                 f"{conc['n_total_new_appointments']} appointments)")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig3_concentration_index.png")
    plt.close()
    print("wrote fig3_concentration_index.png")


def fig4_turnover():
    df = pd.read_csv(f"{DATA_DIR}/turnover_long.csv")
    agg = df.groupby(["group", "from"])[["kept", "departed", "added"]].mean().reset_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(agg))
    ax.bar(x, agg["kept"], label="kept", color="#2f855a")
    ax.bar(x, agg["departed"], bottom=agg["kept"], label="departed", color="#c53030")
    ax.bar(x, agg["added"], bottom=agg["kept"] + agg["departed"], label="added", color="#2b6cb0")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{r.group}\n{r['from']}->next" for _, r in agg.iterrows()], fontsize=9)
    ax.set_ylabel("avg directors per firm")
    ax.set_title("Board turnover/expansion, treated vs. control")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/fig4_turnover.png")
    plt.close()
    print("wrote fig4_turnover.png")


if __name__ == "__main__":
    fig1_network_diagram()
    fig2_metric_trends()
    fig3_concentration()
    fig4_turnover()
