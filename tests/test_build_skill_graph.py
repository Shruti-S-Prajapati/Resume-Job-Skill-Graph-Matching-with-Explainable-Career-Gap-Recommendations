from src.graph.build_skill_graph import compute_idf, build_cooccurrence_graph


def make_skill_sets():
    # "python" appears in every document (common/hub skill)
    # "pytorch" and "mlops" appear together, rarely (specific/rare pair)
    return [
        {"python", "sql"},
        {"python", "pandas"},
        {"python", "pytorch", "mlops"},
        {"python", "pytorch", "mlops"},
    ]


def test_idf_is_lower_for_common_skills():
    idf = compute_idf(make_skill_sets())
    # python appears in all 4 docs, mlops only in 2 -> python's IDF should be lower
    assert idf["python"] < idf["mlops"]


def test_graph_builds_nodes_and_edges():
    graph = build_cooccurrence_graph(make_skill_sets(), min_weight=1)
    assert "python" in graph.nodes
    assert "pytorch" in graph.nodes
    assert graph.has_edge("pytorch", "mlops")


def test_min_weight_filters_rare_pairs():
    skill_sets = [{"a", "b"}, {"a", "c"}]  # each pair occurs only once
    graph = build_cooccurrence_graph(skill_sets, min_weight=2)
    # no pair occurs >= 2 times, so graph should have no edges
    assert graph.number_of_edges() == 0


def test_edge_weight_is_idf_scaled_not_raw_count():
    graph = build_cooccurrence_graph(make_skill_sets(), min_weight=1)
    edge_data = graph.get_edge_data("pytorch", "mlops")
    # raw co-occurrence count was 2, but weight should be IDF-scaled (not exactly 2)
    assert edge_data["raw_count"] == 2
    assert edge_data["weight"] != edge_data["raw_count"]