from src.parsing.resume_parser import parse_resume
from src.parsing.jd_parser import parse_jd
from src.normalization.skill_extractor import load_taxonomy, build_skill_lookup, extract_skills


def find_gap(resume_path: str, jd_path: str) -> dict:
    """
    Resume aur JD dono se skills nikalta hai, compare karta hai,
    aur match/missing/extra skills return karta hai.
    """
    taxonomy = load_taxonomy()
    lookup = build_skill_lookup(taxonomy)

    resume_text = parse_resume(resume_path)
    jd_text = parse_jd(jd_path)

    resume_skills = extract_skills(resume_text, lookup)
    jd_skills = extract_skills(jd_text, lookup)

    matched = resume_skills & jd_skills          # dono mein common
    missing = jd_skills - resume_skills           # JD mein hai, resume mein nahi (GAP)
    extra = resume_skills - jd_skills              # resume mein hai, JD mein nahi

    match_percentage = (len(matched) / len(jd_skills) * 100) if jd_skills else 0

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_percentage": round(match_percentage, 2),
    }


if __name__ == "__main__":
    result = find_gap(
        resume_path="data/raw/sample_resume.docx",
        jd_path="data/raw/sample_jd.txt",
    )

    print(f"Match percentage: {result['match_percentage']}%\n")
    print(f"Matched skills ({len(result['matched'])}): {result['matched']}\n")
    print(f"Missing skills / GAP ({len(result['missing'])}): {result['missing']}\n")
    print(f"Extra skills ({len(result['extra'])}): {result['extra']}")