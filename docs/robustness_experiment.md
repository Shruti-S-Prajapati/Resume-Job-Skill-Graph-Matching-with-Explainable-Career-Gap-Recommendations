# Robustness / Failure-Mode Experiment

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

| Variant | Extracted | Retention | Skill Jaccard | JD overlap | TF-IDF vs clean | Missing JD skills |
|---|---:|---:|---:|---:|---:|---:|
| clean | 7 | 100.00% | 100.00% | 100.00% | 100.00% | 0 |
| case_and_punctuation | 6 | 85.71% | 85.71% | 85.71% | 100.00% | 1 |
| whitespace_noise | 7 | 100.00% | 100.00% | 100.00% | 100.00% | 0 |
| pdf_extraction_artifacts | 5 | 71.43% | 71.43% | 71.43% | 87.64% | 2 |
| heavy_irrelevant_noise | 7 | 100.00% | 100.00% | 100.00% | 42.69% | 0 |

## Observed failure modes

The clean baseline extracted **7 / 7** expected skills (100.00% retention).

The simulated PDF extraction-artifact variant reduced extraction to **5 skills** (71.43% retention). In particular, breaking `scikit-learn` across a line and changing `Python` to `Pyth on` demonstrates a real class of extraction failure: the taxonomy matcher relies on contiguous word-boundary matches, so broken tokens can become invisible to the extractor.

The heavy-noise variant retained **100.00%** of the expected skills while its TF-IDF similarity to the clean resume fell to **42.69%**. This shows that text-level similarity is sensitive to added irrelevant content even when the skill extractor can still recover the target skills.

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
