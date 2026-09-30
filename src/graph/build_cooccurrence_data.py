from pathlib import Path
import pandas as pd

from src.parsing.resume_parser import parse_resume
from src.parsing.jd_parser import parse_jd
from src.normalization.skill_extractor import load_taxonomy, build_skill_lookup, extract_skills


def extract_skills_from_folder(folder_path: str, lookup: dict, file_type: str = "resume") -> list:
    """
    Folder ke andar sab files se skills extract karta hai.
    Har file ke liye ek set of skills return hota hai (list of sets).
    """
    folder = Path(folder_path)
    all_skill_sets = []

    for file in sorted(folder.iterdir()):
        if file.suffix.lower() not in (".pdf", ".docx", ".txt"):
            continue

        try:
            if file_type == "resume":
                text = parse_resume(str(file))
            else:
                text = parse_jd(str(file))

            skills = extract_skills(text, lookup)
            if skills:
                all_skill_sets.append(skills)
                print(f"{file.name}: {len(skills)} skills found")
            else:
                print(f"{file.name}: koi skill nahi mili (skip)")

        except Exception as e:
            print(f"{file.name}: ERROR - {e}")

    return all_skill_sets


if __name__ == "__main__":
    taxonomy = load_taxonomy()
    lookup = build_skill_lookup(taxonomy)

    print("=== Resumes ===")
    resume_skill_sets = extract_skills_from_folder("data/raw/resumes", lookup, file_type="resume")

    print("\n=== JDs ===")
    jd_skill_sets = extract_skills_from_folder("data/raw/jds", lookup, file_type="jd")

    all_skill_sets = resume_skill_sets + jd_skill_sets
    print(f"\nTotal documents processed: {len(all_skill_sets)}")

    # Save karte hain taaki baar baar re-parse na karna pade
    import pickle
    with open("data/processed/skill_sets.pkl", "wb") as f:
        pickle.dump(all_skill_sets, f)
    print("Saved to: data/processed/skill_sets.pkl")