import pickle

from src.parsing.resume_parser import parse_resume
from src.parsing.jd_parser import parse_jd
from src.normalization.skill_extractor import load_taxonomy, build_skill_lookup, extract_skills
from src.similarity.tfidf_similarity import compute_tfidf_similarity
from src.graph.gap_explainer import explain_gaps


def compare_all_approaches(resume_path: str, jd_path: str, graph_path: str = "data/processed/skill_graph.gpickle") -> dict:
    taxonomy = load_taxonomy()
    lookup = build_skill_lookup(taxonomy)

    resume_text = parse_resume(resume_path)
    jd_text = parse_jd(jd_path)

    resume_skills = extract_skills(resume_text, lookup)
    jd_skills = extract_skills(jd_text, lookup)

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    skill_overlap_pct = round((len(matched) / len(jd_skills) * 100), 2) if jd_skills else 0
    tfidf_pct = compute_tfidf_similarity(resume_text, jd_text)

    with open(graph_path, "rb") as f:
        graph = pickle.load(f)
    gap_explanations = explain_gaps(graph, resume_skills, missing)

    # Graph-aware score: missing skills ko unki distance se "penalize" karke ek score banate hain
    # Agar distance chhoti hai (paas hai), to us gap ka weight kam; door hai to zyada
    reachable = [v["distance"] for v in gap_explanations.values() if v["distance"] is not None]
    avg_gap_distance = round(sum(reachable) / len(reachable), 2) if reachable else None

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "skill_overlap_score": skill_overlap_pct,
        "tfidf_score": tfidf_pct,
        "avg_gap_distance": avg_gap_distance,
        "gap_explanations": gap_explanations,
    }


if __name__ == "__main__":
    result = compare_all_approaches(
        resume_path="data/raw/resumes/resume_01.pdf",
        jd_path="data/raw/jds/jd_01.txt",
    )

    print(f"Skill-overlap score: {result['skill_overlap_score']}%")
    print(f"TF-IDF score: {result['tfidf_score']}%")
    print(f"Avg graph-distance of gaps: {result['avg_gap_distance']}")
    print(f"\nMissing skills with explanation:")
    for skill, info in result["gap_explanations"].items():
        print(f"  {skill}: distance={info['distance']}, nearest_known={info['nearest_known_skill']}")