import pickle
import networkx as nx
from itertools import combinations


def build_cooccurrence_graph(skill_sets: list) -> nx.Graph:
    """
    Har document (resume/JD) ke skills ka set leta hai.
    Jo do skills same document mein saath aayi, unke beech edge banata hai.
    Edge weight = kitni baar wo pair saath aaya (across documents).
    """
    graph = nx.Graph()

    for skills in skill_sets:
        skills_list = sorted(skills)  # order consistent rakhne ke liye

        # har skill ko node ke taur pe add karo
        graph.add_nodes_from(skills_list)

        # har pair of skills (jo saath aayi) ke beech edge/weight update karo
        for skill_a, skill_b in combinations(skills_list, 2):
            if graph.has_edge(skill_a, skill_b):
                graph[skill_a][skill_b]["weight"] += 1
            else:
                graph.add_edge(skill_a, skill_b, weight=1)

    return graph


if __name__ == "__main__":
    with open("data/processed/skill_sets.pkl", "rb") as f:
        skill_sets = pickle.load(f)

    graph = build_cooccurrence_graph(skill_sets)

    print(f"Total nodes (unique skills): {graph.number_of_nodes()}")
    print(f"Total edges (relationships): {graph.number_of_edges()}")

    # Top 10 sabse zyada connected skills (degree centrality)
    degree_dict = dict(graph.degree())
    top_skills = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nTop 10 most connected skills:")
    for skill, degree in top_skills:
        print(f"  {skill}: {degree} connections")

    # Graph save karo taaki baar baar rebuild na karna pade
    with open("data/processed/skill_graph.gpickle", "wb") as f:
        pickle.dump(graph, f)
    print("\nSaved to: data/processed/skill_graph.gpickle")