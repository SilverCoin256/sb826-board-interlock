"""
Stage 4 kill-test, step 4: build the actual bipartite director-board graph
from the hand-verified pilot data and report real, honest statistics.

IMPORTANT CAVEAT computed and stated up front, not buried: density/
centralization are population-scale network properties. A 5-8 firm
convenience sample cannot produce a meaningful density/centralization
estimate for the true CA-HQ board-interlock population -- there just
aren't enough nodes for cross-firm ties to be likely by chance. This
script reports what CAN be honestly learned at this scale (board-level
turnover, whether ANY shared-director tie exists in this small sample)
and states plainly what it cannot tell us.
"""
import json, re
import networkx as nx

with open("/Users/shaurya/CascadeProjects/sb826-board-interlock/data/hand_verified_directors.json") as f:
    data = json.load(f)


def norm(name):
    n = name.lower()
    n = re.sub(r"^(dr\.|mr\.|ms\.|mrs\.)\s*", "", n)
    n = re.sub(r"[^a-z ]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def build_bipartite(period_dict):
    B = nx.Graph()
    for firm, directors in period_dict.items():
        B.add_node(("firm", firm), bipartite=0)
        for d in directors:
            key = ("director", norm(d))
            B.add_node(key, bipartite=1, display=d)
            B.add_edge(("firm", firm), key)
    return B


def board_projection(B):
    firm_nodes = [n for n, d in B.nodes(data=True) if d["bipartite"] == 0]
    return nx.bipartite.weighted_projected_graph(B, firm_nodes)


def report(period_name, period_dict):
    print(f"\n=== {period_name} ===")
    B = build_bipartite(period_dict)
    n_firms = len(period_dict)
    n_directors = len({norm(d) for ds in period_dict.values() for d in ds})
    print(f"firms: {n_firms}, unique directors (normalized): {n_directors}, "
          f"total director-firm ties: {sum(len(v) for v in period_dict.values())}")

    proj = board_projection(B)
    print(f"board-projection edges (firm pairs sharing >=1 director): {proj.number_of_edges()}")
    for u, v, w in proj.edges(data=True):
        print(f"  INTERLOCK FOUND: {u[1]} -- {v[1]} (shared directors: {w['weight']})")
    if proj.number_of_edges() == 0:
        print("  No shared directors found among these firms in this sample.")

    possible_pairs = n_firms * (n_firms - 1) / 2
    density = proj.number_of_edges() / possible_pairs if possible_pairs else float("nan")
    print(f"within-sample board-projection density: {density:.4f} "
          f"({proj.number_of_edges()}/{int(possible_pairs)} possible firm-pairs)")
    print("CAVEAT: this density is NOT an estimate of true population interlock "
          "density -- it only tells us whether these specific few firms happen "
          "to share directors with EACH OTHER, which is unlikely by chance at "
          "this sample size regardless of the true population-level density.")
    return {"n_firms": n_firms, "n_directors": n_directors, "n_interlock_edges": proj.number_of_edges(),
            "within_sample_density": density}


def turnover(pre_dict, post_dict):
    print("\n=== Board turnover, pre -> post (firms present in both) ===")
    shared_firms = sorted(set(pre_dict) & set(post_dict))
    out = {}
    for firm in shared_firms:
        pre_set = {norm(d) for d in pre_dict[firm]}
        post_set = {norm(d) for d in post_dict[firm]}
        departed = pre_set - post_set
        added = post_set - pre_set
        kept = pre_set & post_set
        print(f"{firm}: pre_n={len(pre_set)} post_n={len(post_set)} "
              f"kept={len(kept)} departed={len(departed)} added={len(added)}")
        out[firm] = {"pre_n": len(pre_set), "post_n": len(post_set),
                     "kept": len(kept), "departed": len(departed), "added": len(added)}
    return out


if __name__ == "__main__":
    pre_stats = report("PRE (2017-2018)", data["pre"])
    post_stats = report("POST (2020-2021)", data["post"])
    turn = turnover(data["pre"], data["post"])

    out = {"pre": pre_stats, "post": post_stats, "turnover": turn}
    with open("/Users/shaurya/CascadeProjects/sb826-board-interlock/data/pilot_network_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote pilot_network_results.json")
