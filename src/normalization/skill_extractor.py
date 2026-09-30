import re
import pandas as pd
from pathlib import Path


def load_taxonomy(csv_path: str = "data/skills_taxonomy.csv") -> pd.DataFrame:
    """Skill taxonomy CSV load karta hai."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Taxonomy file nahi mili: {csv_path}")
    return pd.read_csv(path)


def build_skill_lookup(taxonomy: pd.DataFrame) -> dict:
    """
    Har alias/skill name ko canonical skill name se map karta hai.
    e.g. "sklearn" -> "scikit-learn", "py" -> "python"
    Sab lowercase mein rakhte hain taaki matching case-insensitive ho.
    """
    lookup = {}
    for _, row in taxonomy.iterrows():
        canonical = str(row["skill"]).strip().lower()
        lookup[canonical] = canonical

        if pd.notna(row["aliases"]) and str(row["aliases"]).strip():
            aliases = [a.strip().lower() for a in str(row["aliases"]).split(",")]
            for alias in aliases:
                if alias:
                    lookup[alias] = canonical

    return lookup




def extract_skills(text: str, skill_lookup: dict) -> set:
    """
    Text mein se skills dhundta hai — word-boundary regex matching,
    taaki 'r' 'arithmetic' ke andar false-positive match na kare.
    """
    text_lower = text.lower()
    found_skills = set()

    for term, canonical in skill_lookup.items():
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text_lower):
            found_skills.add(canonical)

    return found_skills

if __name__ == "__main__":
    from src.parsing.resume_parser import parse_resume

    taxonomy = load_taxonomy()
    lookup = build_skill_lookup(taxonomy)

    resume_text = parse_resume("data/raw/sample_resume.docx")
    skills_found = extract_skills(resume_text, lookup)

    print("Skills found:", skills_found)