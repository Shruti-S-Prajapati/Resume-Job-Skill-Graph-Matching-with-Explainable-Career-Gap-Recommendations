# Resume–Job Skill Graph Matching with Explainable Career-Gap Recommendations

A resume–job-description matching system that combines **taxonomy-based skill extraction, skill overlap, TF-IDF similarity, an IDF-weighted skill co-occurrence graph, explainable skill-gap distances, and ranked learning recommendations**.

The project is designed to answer two related questions:

1. **How well does a resume match a target job description?**
2. **Which missing skills should be considered first, and how are those gaps related to skills the candidate already has?**

> **Important scope note:** the robustness experiment in this repository evaluates sensitivity to formatting and text-extraction noise. It is **not a demographic fairness audit** because it does not contain protected-attribute groups or demographic labels.

## Features

- PDF/DOCX resume text extraction
- TXT/PDF/DOCX job-description extraction
- 1,300+ skill taxonomy combining manual skills and ESCO-derived skills
- Alias-aware, case-insensitive taxonomy matching
- Word-boundary matching to reduce false positives from short skills
- Skill-overlap matching with matched/missing/extra skills
- TF-IDF cosine similarity as a text-level baseline
- NetworkX skill co-occurrence graph with IDF-weighted edges
- Graph-based explanations for missing skills
- Priority ranking of missing skills using JD frequency and graph distance
- Evaluation workflow with annotation template and Precision/Recall/F1
- Streamlit dashboard
- FastAPI `/match` endpoint
- SQLite audit logging for manual skill corrections
- Automated pytest suite and GitHub Actions CI
- Controlled robustness/failure-mode experiment

## Architecture

```text
                  ┌──────────────────────┐
                  │ Resume (PDF/DOCX)    │
                  └──────────┬───────────┘
                             │
                             ▼
                    Resume Text Parser
                             │
                             │
                  ┌──────────▼───────────┐
                  │                      │
                  │  Skill Taxonomy      │
                  │  Manual + ESCO       │
                  │                      │
                  └──────────┬───────────┘
                             │
                             ▼
                    Skill Extraction
                             │
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
 Skill Overlap          TF-IDF Baseline      Skill Graph
        │                    │                    │
        │                    │                    ▼
        │                    │              Gap Explanation
        │                    │                    │
        └────────────────────┴────────────┬───────┘
                                         ▼
                                  Gap Ranking
                                         │
                                         ▼
                             Dashboard / API Results
```

## Repository structure

```text
.
├── app/
│   └── dashboard.py
├── data/
│   ├── annotation_template.csv
│   ├── exclude_skills.txt
│   ├── skills_taxonomy.csv
│   ├── skills_taxonomy_esco.csv
│   ├── skills_taxonomy_manual.csv
│   └── robustness/
│       └── robustness_results.csv
├── docs/
│   └── robustness_experiment.md
├── src/
│   ├── api/
│   ├── evaluation/
│   ├── graph/
│   ├── normalization/
│   ├── parsing/
│   ├── ranking/
│   └── similarity/
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Installation

Python 3.10+ is recommended. The GitHub Actions workflow currently tests the project on Python 3.12.

```bash
git clone <your-repository-url>
cd Resume-Job-Skill-Graph-Matching-with-Explainable-Career-Gap-Recommendations

python -m venv .venv
```

Activate the environment:

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run the Streamlit dashboard

```bash
streamlit run app/dashboard.py
```

The dashboard accepts:

- Resume: PDF or DOCX
- Job description: TXT, PDF, or DOCX

It displays:

- Skill-overlap score
- TF-IDF baseline score
- Average graph distance of gaps
- Matched skills
- Ranked missing skills
- Nearest known skills used to explain gaps
- Extra resume skills
- Manual corrections saved to the SQLite audit log

## Run the FastAPI service

Start the API with:

```bash
uvicorn src.api.main:app --reload
```

The API exposes:

```text
GET  /
POST /match
```

The `/match` endpoint accepts paths to a resume and job-description file and returns the skill-overlap score, TF-IDF score, graph-gap information, matched skills, missing skills, and extra skills.

## Run tests

From the repository root:

```bash
PYTHONPATH=. pytest -q
```

The test suite covers:

- Resume parsing
- Skill extraction and aliases
- Taxonomy merging
- Skill graph construction
- Graph-based gap explanation
- Gap ranking
- TF-IDF similarity
- Combined comparison pipeline
- Robustness/failure-mode experiment

## Methodology

### 1. Skill taxonomy

`data/skills_taxonomy.csv` is the main skill vocabulary. The project also retains the manual and ESCO-derived source taxonomies and an exclusion list for noisy/generic terms.

### 2. Skill extraction

`src/normalization/skill_extractor.py` builds a canonical lookup from skill names and aliases. Matching is case-insensitive and uses word-boundary regular expressions.

For example:

```text
sklearn → scikit-learn
py      → python
```

### 3. Skill overlap

For resume skill set `R` and JD skill set `J`:

```text
matched = R ∩ J
missing = J − R
extra   = R − J
```

The skill-overlap score is:

```text
|matched| / |JD skills| × 100
```

### 4. TF-IDF baseline

The full resume and JD text are transformed with TF-IDF and compared using cosine similarity. This provides a text-level baseline that does not explicitly reason over the skill taxonomy.

### 5. Skill graph

Skills extracted from a batch of resumes and JDs are used to construct a NetworkX co-occurrence graph. Edge weights incorporate co-occurrence and IDF information so that relationships between more specific skills can contribute to gap explanations.

### 6. Explainable career gaps

For each missing skill, the system searches for a shortest path from a skill already present in the resume. Edge weights are converted into path costs, so stronger skill relationships correspond to lower path cost.

The explanation contains:

- graph distance
- nearest known resume skill

### 7. Gap ranking

Missing skills are ranked using JD frequency and graph distance:

```text
priority = 2 × log(JD frequency + 1) − graph distance
```

If a missing skill is unreachable in the graph, a default distance penalty is used.

## Evaluation

The project includes an annotation workflow under `src/evaluation/` and `data/annotation_template.csv`.

The evaluation script reports:

- Precision
- Recall
- F1
- Human agreement rate

The current project evaluation run reported **Precision = 0.76** and **F1 = 0.864**. These values depend on the annotated evaluation set and should be updated if the annotation set changes.

Run:

```bash
PYTHONPATH=. python src/evaluation/compute_metrics.py
```

## Robustness / failure-mode experiment

The repository contains a controlled experiment at:

```text
src/evaluation/robustness_experiment.py
```

It keeps the underlying skill content constant and changes the resume presentation through:

- clean text
- case/punctuation changes
- whitespace noise
- simulated PDF extraction artifacts
- heavy irrelevant text

Run it with:

```bash
PYTHONPATH=. python src/evaluation/robustness_experiment.py
```

Outputs:

```text
data/robustness/robustness_results.csv
docs/robustness_experiment.md
```

### Current controlled results

| Variant | Skill retention | Skill Jaccard | JD overlap | TF-IDF vs clean |
|---|---:|---:|---:|---:|
| Clean | 100.00% | 100.00% | 100.00% | 100.00% |
| Case/punctuation | 85.71% | 85.71% | 85.71% | 100.00% |
| Whitespace noise | 100.00% | 100.00% | 100.00% | 100.00% |
| PDF extraction artifacts | 71.43% | 71.43% | 71.43% | 87.64% |
| Heavy irrelevant noise | 100.00% | 100.00% | 100.00% | 42.69% |

The key observed failure mode is simulated document extraction that breaks tokens such as `scikit-learn` across a line or changes `Python` into a non-contiguous token. The current word-boundary matcher cannot recover such broken tokens.

This is a **robustness finding**, not evidence of demographic fairness. A demographic fairness study would require appropriate data representing relevant groups and a separate analysis of group-level performance differences.

See [`docs/robustness_experiment.md`](docs/robustness_experiment.md) for the formal experiment description, metrics, results, limitations, and reproduction command.

## Manual correction audit log

Manual corrections from the Streamlit dashboard are stored in:

```text
data/audit_logs.db
```

The implementation is in:

```text
src/evaluation/audit_logger.py
```

Each correction records a timestamp, resume/JD names, original matched skills, and corrected matched skills.

## Docker

Build the image:

```bash
docker build -t resume-skill-matcher .
```

Run the Streamlit application:

```bash
docker run --rm -p 8501:8501 resume-skill-matcher
```

Open the Streamlit interface at:

```text
http://localhost:8501
```

## Continuous integration

GitHub Actions is configured in:

```text
.github/workflows/ci.yml
```

On pushes and pull requests to `main`, CI:

1. installs the pinned dependencies,
2. downloads the spaCy model,
3. runs critical-error Flake8 checks,
4. runs `pip-audit`, and
5. executes the pytest suite.

## Limitations

- Taxonomy-based matching is dependent on vocabulary coverage and aliases.
- Broken OCR/PDF extraction can split skill names and reduce recall.
- TF-IDF measures textual similarity rather than semantic skill equivalence.
- Graph explanations depend on the coverage and quality of the co-occurrence graph.
- The graph distance is an explanatory signal, not a causal measure of learning difficulty.
- The evaluation annotation set is limited and should not be treated as a universal benchmark.
- The current robustness experiment is controlled and small; it is not a demographic fairness evaluation.

## Future work

Potential extensions include:

- OCR-aware normalization for broken PDF tokens
- semantic/embedding-based skill matching
- larger human-annotated evaluation sets
- calibration of gap-priority scores
- broader robustness testing across document formats and extraction engines
- demographic fairness evaluation with an appropriately designed dataset
- richer recommendation explanations and learning-resource links

## License

Add the project's intended license here before public release.
