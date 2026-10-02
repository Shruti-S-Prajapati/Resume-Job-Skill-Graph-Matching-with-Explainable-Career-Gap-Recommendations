from src.ranking.gap_ranker import (
    compute_jd_term_frequency,
    rank_gaps_from_result,
)


def test_compute_jd_term_frequency_is_case_insensitive():
    jd_text = "Python PYTHON python"

    assert compute_jd_term_frequency(jd_text, "python") == 3


def test_higher_jd_frequency_increases_priority_when_distance_is_equal():
    jd_text = "python python sql"
    missing = {"python", "sql"}

    gap_explanations = {
        "python": {
            "distance": 1.0,
            "nearest_known_skill": "pandas",
        },
        "sql": {
            "distance": 1.0,
            "nearest_known_skill": "pandas",
        },
    }

    ranked = rank_gaps_from_result(
        jd_text,
        missing,
        gap_explanations,
    )

    assert ranked[0]["skill"] == "python"
    assert ranked[0]["jd_frequency"] == 2
    assert ranked[1]["jd_frequency"] == 1


def test_shorter_graph_distance_increases_priority_when_frequency_is_equal():
    jd_text = "python sql"
    missing = {"python", "sql"}

    gap_explanations = {
        "python": {
            "distance": 1.0,
            "nearest_known_skill": "pandas",
        },
        "sql": {
            "distance": 3.0,
            "nearest_known_skill": "pandas",
        },
    }

    ranked = rank_gaps_from_result(
        jd_text,
        missing,
        gap_explanations,
    )

    assert ranked[0]["skill"] == "python"
    assert ranked[0]["graph_distance"] == 1.0
    assert ranked[1]["graph_distance"] == 3.0


def test_unreachable_gap_uses_default_distance_penalty():
    jd_text = "python"
    missing = {"python"}

    gap_explanations = {
        "python": {
            "distance": None,
            "nearest_known_skill": None,
        },
    }

    ranked = rank_gaps_from_result(
        jd_text,
        missing,
        gap_explanations,
    )

    assert ranked[0]["skill"] == "python"
    assert ranked[0]["jd_frequency"] == 1
    assert ranked[0]["graph_distance"] is None
    assert ranked[0]["nearest_known_skill"] is None


def test_missing_explanation_uses_default_values():
    ranked = rank_gaps_from_result(
        "python",
        {"python"},
        {},
    )

    assert ranked[0]["skill"] == "python"
    assert ranked[0]["graph_distance"] is None
    assert ranked[0]["nearest_known_skill"] is None