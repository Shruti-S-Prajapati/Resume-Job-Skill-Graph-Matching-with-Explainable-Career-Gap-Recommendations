import pickle
import networkx as nx


def explain_gaps(graph: nx.Graph, resume_skills: set, missing_skills: set) -> dict:
    """
    Har missing skill ke liye nearest resume skill se distance nikalta hai.
    Distance ab IDF-weighted hai — high co-occurrence + specific (rare) skills
    'paas' maani jaati hain, generic hub skills ke through wala path 'door' lagta hai.
    """
    # edge weight ko cost mein convert karte hain (1/weight), taaki
    # NetworkX ka shortest_path "strong connection = kam cost" samjhe
    cost_graph = graph.copy()
    for u, v, data in cost_graph.edges(data=True):
        data["cost"] = 1 / data["weight"]

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
                dist = nx.shortest_path_length(cost_graph, source=known_skill, target=skill, weight="cost")
                if best_distance is None or dist < best_distance:
                    best_distance = round(dist, 3)
                    nearest_skill = known_skill
            except nx.NetworkXNoPath:
                continue

        explanations[skill] = {"distance": best_distance, "nearest_known_skill": nearest_skill}
    return explanations