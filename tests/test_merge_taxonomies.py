import pandas as pd

from src.normalization.merge_taxonomies import clean_skill_name, merge_taxonomies


def test_clean_skill_name_removes_parenthetical_qualifier():
    assert clean_skill_name("python (computer programming)") == "python"


def test_clean_skill_name_leaves_plain_names_unchanged():
    assert clean_skill_name("docker") == "docker"


def test_clean_skill_name_strips_extra_whitespace():
    assert clean_skill_name("  sql  ") == "sql"


def test_merge_taxonomies_excludes_listed_skills(tmp_path):
    manual_path = tmp_path / "manual.csv"
    esco_path = tmp_path / "esco.csv"
    exclude_path = tmp_path / "exclude.txt"
    output_path = tmp_path / "merged.csv"

    pd.DataFrame({
        "skill": ["python", "business intelligence"],
        "category": ["programming", "esco"],
        "aliases": ["", ""],
    }).to_csv(manual_path, index=False)

    pd.DataFrame({
        "skill": ["docker", "computer science"],
        "category": ["esco", "esco"],
        "aliases": ["", ""],
    }).to_csv(esco_path, index=False)

    exclude_path.write_text("business intelligence\ncomputer science\n")

    merge_taxonomies(str(manual_path), str(esco_path), str(output_path), exclude_path=str(exclude_path))

    result = pd.read_csv(output_path)
    skills = set(result["skill"])

    assert "python" in skills
    assert "docker" in skills
    assert "business intelligence" not in skills
    assert "computer science" not in skills


def test_merge_taxonomies_deduplicates_and_merges_aliases(tmp_path):
    manual_path = tmp_path / "manual.csv"
    esco_path = tmp_path / "esco.csv"
    output_path = tmp_path / "merged.csv"

    pd.DataFrame({
        "skill": ["scikit-learn"],
        "category": ["library"],
        "aliases": ["sklearn"],
    }).to_csv(manual_path, index=False)

    pd.DataFrame({
        "skill": ["scikit-learn"],
        "category": ["esco"],
        "aliases": ["scikit learn"],
    }).to_csv(esco_path, index=False)

    merge_taxonomies(str(manual_path), str(esco_path), str(output_path))

    result = pd.read_csv(output_path)
    assert len(result) == 1  # deduplicated, not two rows
    aliases = result.iloc[0]["aliases"]
    assert "sklearn" in aliases
    assert "scikit learn" in aliases