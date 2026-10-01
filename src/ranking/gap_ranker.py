import pickle
import math
from collections import Counter

from src.parsing.resume_parser import parse_resume
from src.parsing.jd_parser import parse_jd
from src.normalization.skill_extractor import load_taxonomy, build_skill_lookup, extract_skills
from src.graph.gap_explainer import explain_gaps


def compute_jd_term_frequency(jd_text: str, skill: str) -> int:
    """JD text mein skill kitni baar mention hui — zyada baar = zyada important."""
    return jd_text.lower().count(skill.lower())


def rank_gaps(resume_path: str, jd_path: str, graph_path: str = "data/processed/skill_graph.gpickle") -> list:
    """
    Missing skills ko priority score ke hisaab se rank karta hai.
    Score jitna zyada, utni pehle seekhni chahiye us skill ko.

    Formula: score = jd_frequency_weight - distance_penalty
      - JD mein zyada baar mention -> zyada important -> score badhta hai
      - Graph mein zyada door -> seekhna mushkil/bada gap -> score ghatta hai
        (taaki "easy wins" pehle recommend ho, jo resume skills se paas hain)
    """
    taxonomy = load_taxonomy()
    lookup = build_skill_lookup(taxonomy)

    resume_text = parse_resume(resume_path)
    jd_text = parse_jd(jd_path)

    resume_skills = extract_skills(resume_text, lookup)
    jd_skills = extract_skills(jd_text, lookup)
    missing = jd_skills - resume_skills

    with open(graph_path, "rb") as f:
        graph = pickle.load(f)

    gap_explanations = explain_gaps(graph, resume_skills, missing)

    ranked = []
    for skill in missing:
        jd_freq = compute_jd_term_frequency(jd_text, skill)
        distance = gap_explanations[skill]["distance"]
        nearest = gap_explanations[skill]["nearest_known_skill"]

        # agar graph mein path hi nahi mila (unreachable), to badi penalty do
        distance_penalty = distance if distance is not None else 5.0

        # jd_freq ko log-scale karte hain taaki ek bahut zyada mention wali skill
        # baaki sabko pura dominate na kare
        score = math.log(jd_freq + 1) * 2 - distance_penalty

        ranked.append({
            "skill": skill,
            "jd_frequency": jd_freq,
            "graph_distance": distance,
            "nearest_known_skill": nearest,
            "priority_score": round(score, 3),
        })

    ranked.sort(key=lambda x: x["priority_score"], reverse=True)
    return ranked


if __name__ == "__main__":
    results = rank_gaps(
        resume_path="data/raw/resumes/resume_01.pdf",
        jd_path="data/raw/jds/jd_01.txt",
    )

    print(f"{'Rank':<5}{'Skill':<30}{'JD Freq':<10}{'Distance':<12}{'Nearest Known':<20}{'Score'}")
    for i, item in enumerate(results, start=1):
        dist_str = str(item["graph_distance"]) if item["graph_distance"] is not None else "unreachable"
        print(f"{i:<5}{item['skill']:<30}{item['jd_frequency']:<10}{dist_str:<12}{item['nearest_known_skill'] or '-':<20}{item['priority_score']}")