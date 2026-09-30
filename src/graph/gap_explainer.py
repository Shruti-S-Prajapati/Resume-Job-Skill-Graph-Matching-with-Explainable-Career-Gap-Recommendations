import pickle
import networkx as nx


def explain_gaps(graph: nx.Graph, resume_skills: set, missing_skills: set) -> dict:
    """Har missing skill ke liye: nearest resume skill se kitni door hai (graph distance)."""
    explanations = {}
    for skill in missing_skills:
        if skill not in graph:
            explanations[skill] = {"distance": None, "nearest_known_skill": None}
            continue

        best_distance = None
        nearest_skill = None
        for known_skill in resume_skills:
            if known_skill not in graph:
                continue
            try:
                dist = nx.shortest_path_length(graph, source=known_skill, target=skill)
                if best_distance is None or dist < best_distance:
                    best_distance = dist
                    nearest_skill = known_skill
            except nx.NetworkXNoPath:
                continue

        explanations[skill] = {"distance": best_distance, "nearest_known_skill": nearest_skill}
    return explanations


if __name__ == "__main__":
    with open("data/processed/skill_graph.gpickle", "rb") as f:
        graph = pickle.load(f)
    # test: gap_finder.py ka result yahan plug karna hoga