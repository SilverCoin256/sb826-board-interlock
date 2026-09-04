"""
Stage 5+6: build bipartite director-board graphs per group (treated/control)
per snapshot (pre/post/post2), compute network metrics, and emit a tidy
long-format table ready for Stage 7 statistical modeling.

Expects data/clean_directors.json in the shape:
{
  "treated": {"pre": {firm: [directors]}, "post": {...}, "post2": {...}},
  "control": {"pre": {...}, "post": {...}, "post2": {...}}
}
"""
import json, re
import networkx as nx
import pandas as pd

IN_PATH = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/clean_directors.json"
OUT_METRICS = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/network_metrics_long.csv"
OUT_TURNOVER = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/turnover_long.csv"
OUT_CONCENTRATION = "/Users/shaurya/CascadeProjects/sb826-board-interlock/data/concentration_index.json"


def norm(name):
    n = name.lower()
    n = re.sub(r"^(dr\.|mr\.|ms\.|mrs\.)\s*", "", n)
    n = re.sub(r"[^a-z ]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def build_bipartite(period_dict):
    B = nx.Graph()
    for firm, directors in period_dict.items():
        fnode = ("firm", firm)
        B.add_node(fnode, bipartite=0)
        for d in directors:
            dnode = ("director", norm(d))
            B.add_node(dnode, bipartite=1, display=d)
            B.add_edge(fnode, dnode)
    return B


def board_projection(B):
    firm_nodes = [n for n, d in B.nodes(data=True) if d["bipartite"] == 0]
    if len(firm_nodes) < 2:
        return nx.Graph()
    return nx.bipartite.weighted_projected_graph(B, firm_nodes)


def metrics_for(period_dict):
    B = build_bipartite(period_dict)
    proj = board_projection(B)
    n_firms = len(period_dict)
    n_directors = len({norm(d) for ds in period_dict.values() for d in ds})
    n_edges = proj.number_of_edges()
    possible = n_firms * (n_firms - 1) / 2
    density = n_edges / possible if possible else float("nan")

    if n_edges > 0:
        deg_cent = nx.degree_centrality(proj)
        degrees = list(deg_cent.values())
        max_deg = max(degrees)
        centralization = sum(max_deg - d for d in degrees) / (len(degrees) - 1) if len(degrees) > 1 else float("nan")
        largest_cc = len(max(nx.connected_components(proj), key=len))
        try:
            avg_clustering = nx.average_clustering(proj, weight=None)
        except Exception:
            avg_clustering = float("nan")
    else:
        centralization = 0.0
        largest_cc = 1 if n_firms else 0
        avg_clustering = 0.0

    return {
        "n_firms": n_firms, "n_directors_unique": n_directors,
        "n_interlock_edges": n_edges, "density": density,
        "degree_centralization": centralization,
        "largest_component_firms": largest_cc,
        "avg_clustering": avg_clustering,
    }


def turnover_rows(group, pre_dict, post_dict, pre_tag, post_tag):
    rows = []
    shared = sorted(set(pre_dict) & set(post_dict))
    for firm in shared:
        pre_set = {norm(d) for d in pre_dict[firm]}
        post_set = {norm(d) for d in post_dict[firm]}
        rows.append({
            "group": group, "firm": firm, "from": pre_tag, "to": post_tag,
            "pre_n": len(pre_set), "post_n": len(post_set),
            "kept": len(pre_set & post_set),
            "departed": len(pre_set - post_set),
            "added": len(post_set - pre_set),
        })
    return rows


def gini(values):
    if not values:
        return float("nan")
    v = sorted(values)
    n = len(v)
    cum = sum((i + 1) * x for i, x in enumerate(v))
    total = sum(v)
    if total == 0:
        return float("nan")
    return (2 * cum) / (n * total) - (n + 1) / n


def main():
    with open(IN_PATH) as f:
        data = json.load(f)

    metric_rows = []
    for group in ["treated", "control"]:
        for snap in ["pre", "post", "post2"]:
            m = metrics_for(data[group][snap])
            m["group"] = group
            m["snapshot"] = snap
            metric_rows.append(m)
    metrics_df = pd.DataFrame(metric_rows)
    metrics_df.to_csv(OUT_METRICS, index=False)
    print(metrics_df.to_string(index=False))

    turnover = []
    for group in ["treated", "control"]:
        turnover += turnover_rows(group, data[group]["pre"], data[group]["post"], "pre", "post")
        turnover += turnover_rows(group, data[group]["post"], data[group]["post2"], "post", "post2")
    turnover_df = pd.DataFrame(turnover)
    turnover_df.to_csv(OUT_TURNOVER, index=False)
    print(f"\nwrote {len(turnover_df)} turnover rows")

    # concentration/Gini index of NEW appointments treated pre->post (tokenism test)
    treated_pre = data["treated"]["pre"]
    treated_post = data["treated"]["post"]
    new_appointee_board_counts = {}
    for firm in set(treated_pre) & set(treated_post):
        pre_set = {norm(d) for d in treated_pre[firm]}
        post_set = {norm(d) for d in treated_post[firm]}
        newly_added = post_set - pre_set
        for d in newly_added:
            new_appointee_board_counts[d] = new_appointee_board_counts.get(d, 0) + 1
    conc = {
        "n_unique_new_appointees": len(new_appointee_board_counts),
        "n_total_new_appointments": sum(new_appointee_board_counts.values()),
        "gini_of_appointment_counts": gini(list(new_appointee_board_counts.values())),
        "max_boards_by_single_appointee": max(new_appointee_board_counts.values()) if new_appointee_board_counts else 0,
        "note": "High Gini / high max = tokenism-consistent (small recycled pool). Low Gini = broad-based entry (H1-alt consistent). NOTE: only detects recycling WITHIN this sample -- an appointee could sit on many more boards outside the sample and appear as 1 here.",
    }
    with open(OUT_CONCENTRATION, "w") as f:
        json.dump(conc, f, indent=2)
    print("\nConcentration/tokenism index:", json.dumps(conc, indent=2))


if __name__ == "__main__":
    main()
