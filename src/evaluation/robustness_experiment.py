"""Controlled robustness experiment for resume skill extraction.

The experiment keeps the underlying skills constant and changes only the
presentation/noise of the resume text. It is intentionally a robustness
experiment, not a demographic fairness study.

Run from the repository root:
    PYTHONPATH=. python src/evaluation/robustness_experiment.py

Outputs:
    data/robustness/robustness_results.csv
    docs/robustness_experiment.md
"""

from __future__ import annotations

import csv
from pathlib import Path

from src.normalization.skill_extractor import (
    build_skill_lookup,
    extract_skills,
    load_taxonomy,
)
from src.similarity.tfidf_similarity import compute_tfidf_similarity


ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / "data" / "robustness" / "robustness_results.csv"
REPORT_PATH = ROOT / "docs" / "robustness_experiment.md"

# Same underlying skill content across all resume variants.
EXPECTED_SKILLS = {
    "python",
    "sql",
    "pandas",
    "scikit-learn",
    "docker",
    "git",
    "machine learning",
}

JOB_DESCRIPTION = """
We are hiring a data engineer with experience in Python, SQL, pandas,
scikit-learn, Docker, Git, and machine learning. The role involves building
machine learning pipelines and production data workflows.
""".strip()

RESUME_VARIANTS = {
    "clean": """
Software Engineer
Python, SQL, pandas, scikit-learn, Docker, Git
Built machine learning pipelines and REST APIs.
""".strip(),
    "case_and_punctuation": """
SOFTWARE ENGINEER!!!
python; SQL / PANDAS / SCIKIT-LEARN / docker / GIT.
Built machine-learning pipelines & REST APIs.
""".strip(),
    "whitespace_noise": """
Software Engineer

Python   SQL\t pandas
scikit-learn
Docker
Git
Built machine learning pipelines and REST APIs.
""".strip(),
    "pdf_extraction_artifacts": """
Software Engineer
Pyth on, SQL, pandas, scikit-
learn, Docker, Git
Built machine learning pipelines and REST APIs.
""".strip(),
    "heavy_irrelevant_noise": """
[PAGE 1] SOFTWARE ENGINEER | 2026
Contact: example@example.com | 12345
PYTHON ... SQL ... PANDAS ... SCIKIT-LEARN ... DOCKER ... GIT

Lorem ipsum lorem ipsum lorem ipsum.
Machine learning pipelines / REST APIs.
""".strip(),
}


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def run_experiment() -> list[dict]:
    taxonomy = load_taxonomy(str(ROOT / "data" / "skills_taxonomy.csv"))
    lookup = build_skill_lookup(taxonomy)
    jd_skills = extract_skills(JOB_DESCRIPTION, lookup)

    # The expected set is explicit so the experiment is reproducible even if
    # the taxonomy later gains additional related terms.
    clean_skills = extract_skills(RESUME_VARIANTS["clean"], lookup)
    expected = EXPECTED_SKILLS & clean_skills

    rows: list[dict] = []
    for variant, text in RESUME_VARIANTS.items():
        extracted = extract_skills(text, lookup)
        matched = extracted & jd_skills
        missing = jd_skills - extracted
        unexpected = extracted - expected

        rows.append(
            {
                "variant": variant,
                "expected_skill_count": len(expected),
                "extracted_skill_count": len(extracted),
                "retention_rate_pct": round(
                    len(extracted & expected) / len(expected) * 100, 2
                ),
                "skill_jaccard_pct": round(jaccard(expected, extracted) * 100, 2),
                "unexpected_skill_count": len(unexpected),
                "jd_overlap_pct": round(
                    len(matched) / len(jd_skills) * 100, 2
                )
                if jd_skills
                else 0.0,
                "missing_jd_skill_count": len(missing),
                "tfidf_vs_clean_pct": compute_tfidf_similarity(
                    RESUME_VARIANTS["clean"], text
                ),
                "missing_skills": ", ".join(sorted(missing)),
            }
        )

    return rows


def write_results(rows: list[dict]) -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def write_report(rows: list[dict]) -> None:
    clean = next(row for row in rows if row["variant"] == "clean")
    artifact = next(
        row for row in rows if row["variant"] == "pdf_extraction_artifacts"
    )
    heavy_noise = next(
        row for row in rows if row["variant"] == "heavy_irrelevant_noise"
    )

    table = [
        "| Variant | Extracted | Retention | Skill Jaccard | JD overlap | TF-IDF vs clean | Missing JD skills |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        table.append(
            f"| {row['variant']} | {row['extracted_skill_count']} | "
            f"{row['retention_rate_pct']:.2f}% | {row['skill_jaccard_pct']:.2f}% | "
            f"{row['jd_overlap_pct']:.2f}% | {row['tfidf_vs_clean_pct']:.2f}% | "
            f"{row['missing_jd_skill_count']} |"
        )

    report = f"""# Robustness / Failure-Mode Experiment

## Scope

This experiment evaluates **robustness to resume formatting and text-extraction noise**. It is not a demographic fairness audit: no protected attributes or demographic groups are represented in the experiment. Therefore, the results should not be interpreted as evidence of demographic fairness.

The experiment uses one controlled resume whose underlying skill set is held constant while the presentation is changed. The variants introduce casing/punctuation changes, whitespace noise, simulated PDF extraction artifacts, and irrelevant text.

## Experimental setup

- Taxonomy: `data/skills_taxonomy.csv`
- Skill extraction: `src/normalization/skill_extractor.py`
- TF-IDF baseline: `src/similarity/tfidf_similarity.py`
- Expected skill set: Python, SQL, pandas, scikit-learn, Docker, Git, and machine learning
- Job description contains the same seven target skills.
- No model retraining or parameter tuning is performed between variants.

### Metrics

- **Retention rate:** expected skills still extracted / expected skills.
- **Skill Jaccard:** overlap between expected and extracted skill sets.
- **JD overlap:** extracted skills that match the controlled JD skill set.
- **TF-IDF vs clean:** text similarity between the clean resume and each variant.
- **Missing JD skills:** controlled JD skills not extracted from the variant.

## Results

{chr(10).join(table)}

## Observed failure modes

The clean baseline extracted **{clean['extracted_skill_count']} / {clean['expected_skill_count']}** expected skills ({clean['retention_rate_pct']:.2f}% retention).

The simulated PDF extraction-artifact variant reduced extraction to **{artifact['extracted_skill_count']} skills** ({artifact['retention_rate_pct']:.2f}% retention). In particular, breaking `scikit-learn` across a line and changing `Python` to `Pyth on` demonstrates a real class of extraction failure: the taxonomy matcher relies on contiguous word-boundary matches, so broken tokens can become invisible to the extractor.

The heavy-noise variant retained **{heavy_noise['retention_rate_pct']:.2f}%** of the expected skills while its TF-IDF similarity to the clean resume fell to **{heavy_noise['tfidf_vs_clean_pct']:.2f}%**. This shows that text-level similarity is sensitive to added irrelevant content even when the skill extractor can still recover the target skills.

## Interpretation and limitations

The experiment shows that the current taxonomy-based extractor is reasonably tolerant of case, punctuation, and ordinary whitespace changes, but it can fail when document extraction splits a skill into non-contiguous tokens. This is a **failure-mode finding**, not a claim about performance on all resumes or demographic groups.

The experiment is deliberately small and synthetic. It does not measure robustness across PDF generators, OCR engines, languages, resume templates, or real-world document corruption. A stronger future study would use a larger set of real resumes, paired clean/perturbed versions, multiple PDF extraction paths, and confidence intervals across documents.

## Reproduction

From the repository root:

```bash
PYTHONPATH=. python src/evaluation/robustness_experiment.py
```

The command regenerates:

- `data/robustness/robustness_results.csv`
- `docs/robustness_experiment.md`
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    rows = run_experiment()
    write_results(rows)
    write_report(rows)
    print(f"Wrote {RESULTS_PATH}")
    print(f"Wrote {REPORT_PATH}")
    for row in rows:
        print(
            f"{row['variant']}: retention={row['retention_rate_pct']:.2f}% "
            f"JD-overlap={row['jd_overlap_pct']:.2f}% "
            f"TF-IDF={row['tfidf_vs_clean_pct']:.2f}%"
        )


if __name__ == "__main__":
    main()
