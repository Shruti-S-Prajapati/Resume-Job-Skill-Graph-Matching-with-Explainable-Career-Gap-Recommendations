from src.evaluation.robustness_experiment import run_experiment


def test_robustness_experiment_contains_controlled_variants():
    rows = run_experiment()
    variants = {row["variant"] for row in rows}

    assert variants == {
        "clean",
        "case_and_punctuation",
        "whitespace_noise",
        "pdf_extraction_artifacts",
        "heavy_irrelevant_noise",
    }


def test_robustness_experiment_exposes_pdf_artifact_failure_mode():
    rows = run_experiment()
    artifact = next(
        row for row in rows if row["variant"] == "pdf_extraction_artifacts"
    )
    clean = next(row for row in rows if row["variant"] == "clean")

    assert clean["retention_rate_pct"] == 100.0
    assert artifact["retention_rate_pct"] < clean["retention_rate_pct"]
    assert "python" in artifact["missing_skills"]
    assert "scikit-learn" in artifact["missing_skills"]
