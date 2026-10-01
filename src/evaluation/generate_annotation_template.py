import csv
from pathlib import Path

from src.parsing.resume_parser import parse_resume
from src.parsing.jd_parser import parse_jd
from src.normalization.skill_extractor import load_taxonomy, build_skill_lookup, extract_skills


def generate_template(resume_jd_pairs: list, output_path: str = "data/annotation_template.csv"):
    """
    Har resume-JD pair ke liye, system ne jo missing skills nikali unki list banata hai.
    Human annotator har row mein 'correct_gap' column mein 1/0 bharega
    (1 = ye genuinely gap hai, 0 = galat/noise hai).
    """
    taxonomy = load_taxonomy()
    lookup = build_skill_lookup(taxonomy)

    rows = []
    for pair_id, (resume_path, jd_path) in enumerate(resume_jd_pairs, start=1):
        resume_text = parse_resume(resume_path)
        jd_text = parse_jd(jd_path)

        resume_skills = extract_skills(resume_text, lookup)
        jd_skills = extract_skills(jd_text, lookup)

        missing = jd_skills - resume_skills
        matched = resume_skills & jd_skills

        for skill in sorted(missing):
            rows.append({
                "pair_id": pair_id,
                "resume_file": Path(resume_path).name,
                "jd_file": Path(jd_path).name,
                "skill": skill,
                "system_label": "missing",
                "correct_gap": "",       # annotator fill karega: 1 or 0
            })

        for skill in sorted(matched):
            rows.append({
                "pair_id": pair_id,
                "resume_file": Path(resume_path).name,
                "jd_file": Path(jd_path).name,
                "skill": skill,
                "system_label": "matched",
                "correct_gap": "",       # matched ke liye bhi verify: sahi matched hai ya nahi
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pair_id", "resume_file", "jd_file", "skill", "system_label", "correct_gap"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Template saved: {output_path}")
    print(f"Total rows to annotate: {len(rows)}")


if __name__ == "__main__":
    pairs = [
        (f"data/raw/resumes/resume_{i:02d}.pdf" if i not in (11, 12, 13, 14) else f"data/raw/resumes/resume_{i:02d}.docx",
         f"data/raw/jds/jd_{i:02d}.txt")
        for i in range(1, 9)   # pehle 8 pairs
    ]
    generate_template(pairs)