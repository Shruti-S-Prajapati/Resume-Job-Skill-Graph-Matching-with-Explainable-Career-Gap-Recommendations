import networkx as nx

from src.graph.gap_explainer import explain_gaps


def make_simple_graph():
    graph = nx.Graph()
    # python -- pandas -- scikit-learn (chain), weight = strength of connection
    graph.add_edge("python", "pandas", weight=5)
    graph.add_edge("pandas", "scikit-learn", weight=5)
    # "docker" is an isolated node, no path from python/pandas to it
    graph.add_node("docker")
    return graph


def test_reachable_skill_gets_a_distance():
    graph = make_simple_graph()
    result = explain_gaps(graph, resume_skills={"python"}, missing_skills={"scikit-learn"})

    assert result["scikit-learn"]["distance"] is not None
    assert result["scikit-learn"]["nearest_known_skill"] == "python"


def test_unreachable_skill_gets_none_distance():
    graph = make_simple_graph()
    result = explain_gaps(graph, resume_skills={"python"}, missing_skills={"docker"})

    assert result["docker"]["distance"] is None
    assert result["docker"]["nearest_known_skill"] is None


def test_skill_not_in_graph_gets_none_distance():
    graph = make_simple_graph()
    result = explain_gaps(graph, resume_skills={"python"}, missing_skills={"some-unknown-skill"})

    assert result["some-unknown-skill"]["distance"] is None


def test_nearer_skill_is_picked_over_farther_one():
    graph = make_simple_graph()
    # resume has both "python" (2 hops away) and "pandas" (1 hop away) from scikit-learn
    result = explain_gaps(graph, resume_skills={"python", "pandas"}, missing_skills={"scikit-learn"})

    assert result["scikit-learn"]["nearest_known_skill"] == "pandas"