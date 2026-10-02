import pickle

import networkx as nx

import src.similarity.compare_approaches as compare_module


def make_graph():
    graph = nx.Graph()

    graph.add_edge(
        "python",
        "pandas",
        weight=2.0,
    )

    graph.add_edge(
        "pandas",
        "scikit-learn",
        weight=2.0,
    )

    return graph


def test_compare_all_approaches_combines_overlap_tfidf_and_graph(
    tmp_path,
    monkeypatch,
):
    graph_path = tmp_path / "graph.gpickle"

    with graph_path.open("wb") as f:
        pickle.dump(make_graph(), f)

    monkeypatch.setattr(
        compare_module,
        "load_taxonomy",
        lambda: object(),
    )

    monkeypatch.setattr(
        compare_module,
        "build_skill_lookup",
        lambda taxonomy: {"python": "python"},
    )

    monkeypatch.setattr(
        compare_module,
        "parse_resume",
        lambda path: "Python resume",
    )

    monkeypatch.setattr(
        compare_module,
        "parse_jd",
        lambda path: "Python pandas scikit-learn",
    )

    monkeypatch.setattr(
        compare_module,
        "extract_skills",
        lambda text, lookup: (
            {"python"}
            if text == "Python resume"
            else {"python", "pandas", "scikit-learn"}
        ),
    )

    monkeypatch.setattr(
        compare_module,
        "compute_tfidf_similarity",
        lambda resume, jd: 75.5,
    )

    result = compare_module.compare_all_approaches(
        "resume.pdf",
        "jd.txt",
        graph_path=str(graph_path),
    )

    assert result["matched"] == {"python"}
    assert result["missing"] == {"pandas", "scikit-learn"}
    assert result["extra"] == set()

    assert result["skill_overlap_score"] == 33.33
    assert result["tfidf_score"] == 75.5

    assert result["jd_text"] == "Python pandas scikit-learn"

    assert result["avg_gap_distance"] is not None

    assert set(result["gap_explanations"]) == {
        "pandas",
        "scikit-learn",
    }


def test_compare_all_approaches_handles_jd_with_no_detected_skills(
    tmp_path,
    monkeypatch,
):
    graph_path = tmp_path / "graph.gpickle"

    with graph_path.open("wb") as f:
        pickle.dump(nx.Graph(), f)

    monkeypatch.setattr(
        compare_module,
        "load_taxonomy",
        lambda: object(),
    )

    monkeypatch.setattr(
        compare_module,
        "build_skill_lookup",
        lambda taxonomy: {},
    )

    monkeypatch.setattr(
        compare_module,
        "parse_resume",
        lambda path: "resume",
    )

    monkeypatch.setattr(
        compare_module,
        "parse_jd",
        lambda path: "jd",
    )

    monkeypatch.setattr(
        compare_module,
        "extract_skills",
        lambda text, lookup: set(),
    )

    monkeypatch.setattr(
        compare_module,
        "compute_tfidf_similarity",
        lambda resume, jd: 0.0,
    )

    result = compare_module.compare_all_approaches(
        "resume.pdf",
        "jd.txt",
        graph_path=str(graph_path),
    )

    assert result["matched"] == set()
    assert result["missing"] == set()
    assert result["extra"] == set()

    assert result["skill_overlap_score"] == 0
    assert result["tfidf_score"] == 0.0

    assert result["avg_gap_distance"] is None
    assert result["gap_explanations"] == {}


def test_compare_all_approaches_raises_for_missing_graph(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        compare_module,
        "load_taxonomy",
        lambda: object(),
    )

    monkeypatch.setattr(
        compare_module,
        "build_skill_lookup",
        lambda taxonomy: {},
    )

    monkeypatch.setattr(
        compare_module,
        "parse_resume",
        lambda path: "resume",
    )

    monkeypatch.setattr(
        compare_module,
        "parse_jd",
        lambda path: "jd",
    )

    monkeypatch.setattr(
        compare_module,
        "extract_skills",
        lambda text, lookup: set(),
    )

    monkeypatch.setattr(
        compare_module,
        "compute_tfidf_similarity",
        lambda resume, jd: 0.0,
    )

    missing_graph = tmp_path / "missing.gpickle"

    try:
        compare_module.compare_all_approaches(
            "resume.pdf",
            "jd.txt",
            graph_path=str(missing_graph),
        )

        assert False, "Expected FileNotFoundError"

    except FileNotFoundError:
        pass