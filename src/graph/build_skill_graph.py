import pickle
import math
import networkx as nx
from itertools import combinations
from collections import Counter


def compute_idf(skill_sets: list) -> dict:
    """Har skill ka IDF score nikalta hai — jo skill jitni zyada documents mein hai, utna kam IDF."""
    n_docs = len(skill_sets)
    doc_freq = Counter()

    for skills in skill_sets:
        for skill in skills:
            doc_freq[skill] += 1

    idf = {}
    for skill, freq in doc_freq.items():
        idf[skill] = math.log(n_docs / freq) + 1  # +1 taaki kabhi 0 na ho

    return idf


def build_cooccurrence_graph(skill_sets: list, min_weight: int = 1) -> nx.Graph:
    """
    Co-occurrence graph banata hai, but edge weight ko IDF se scale karta hai —
    taaki bahut common skills (jaise python, jo har document mein hai) ke edges
    artificially strong na dikhein. Rare/specific skill pairs ko zyada weight milta hai.
    """
    idf = compute_idf(skill_sets)
    edge_counts = {}

    for skills in skill_sets:
        skills_list = sorted(skills)
        for skill_a, skill_b in combinations(skills_list, 2):
            pair = (skill_a, skill_b)
            edge_counts[pair] = edge_counts.get(pair, 0) + 1

    graph = nx.Graph()
    for (skill_a, skill_b), raw_count in edge_counts.items():
        if raw_count < min_weight:
            continue

        # IDF-weighted strength: dono skills ka IDF average, raw count se multiply
        idf_weight = raw_count * ((idf[skill_a] + idf[skill_b]) / 2)
        graph.add_edge(skill_a, skill_b, weight=idf_weight, raw_count=raw_count)

    return graph


if __name__ == "__main__":
    with open("data/processed/skill_sets.pkl", "rb") as f:
        skill_sets = pickle.load(f)

    graph = build_cooccurrence_graph(skill_sets, min_weight=2)

    print(f"Total nodes (unique skills): {graph.number_of_nodes()}")
    print(f"Total edges (relationships): {graph.number_of_edges()}")

    degree_dict = dict(graph.degree())
    top_skills = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nTop 10 most connected skills (by degree):")
    for skill, degree in top_skills:
        print(f"  {skill}: {degree} connections")

    with open("data/processed/skill_graph.gpickle", "wb") as f:
        pickle.dump(graph, f)
    print("\nSaved to: data/processed/skill_graph.gpickle")