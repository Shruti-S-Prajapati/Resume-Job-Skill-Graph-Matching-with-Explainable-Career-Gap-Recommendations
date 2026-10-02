import pandas as pd

from src.normalization.skill_extractor import build_skill_lookup, extract_skills


def make_taxonomy():
    return pd.DataFrame({
        "skill": ["python", "scikit-learn", "r"],
        "category": ["programming", "library", "programming"],
        "aliases": ["py", "sklearn", ""],
    })


def test_build_skill_lookup_maps_canonical_and_aliases():
    lookup = build_skill_lookup(make_taxonomy())

    assert lookup["python"] == "python"
    assert lookup["py"] == "python"
    assert lookup["sklearn"] == "scikit-learn"
    assert lookup["scikit-learn"] == "scikit-learn"


def test_extract_skills_finds_canonical_and_alias_mentions():
    lookup = build_skill_lookup(make_taxonomy())
    text = "Experienced in Python and sklearn based pipelines."

    found = extract_skills(text, lookup)

    assert "python" in found
    assert "scikit-learn" in found


def test_extract_skills_respects_word_boundaries():
    """Short skill names like 'r' should not match inside unrelated words."""
    lookup = build_skill_lookup(make_taxonomy())
    text = "Worked on arithmetic and bar charts, no coding language mentioned here."

    found = extract_skills(text, lookup)

    assert "r" not in found


def test_extract_skills_empty_text_returns_empty_set():
    lookup = build_skill_lookup(make_taxonomy())
    assert extract_skills("", lookup) == set()