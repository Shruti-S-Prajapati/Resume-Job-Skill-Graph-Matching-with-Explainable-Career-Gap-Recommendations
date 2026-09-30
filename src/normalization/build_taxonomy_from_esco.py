import pandas as pd
from pathlib import Path

# Keywords jinke aadhar pe tech/DS related skills filter karenge
TECH_KEYWORDS = [
    "python", "java", "sql", "javascript", "programming", "software",
    "data", "machine learning", "deep learning", "artificial intelligence",
    "algorithm", "database", "cloud computing", "aws", "azure",
    "network", "cyber", "statistics", "statistical", "analytics",
    "visualization", "api", "web development", "devops", "docker",
    "kubernetes", "linux", "git", "testing", "agile", "scrum",
    "computer", "coding", "framework", "model", "neural", "nlp",
    "natural language", "computer vision", "big data", "etl",
    "data warehouse", "data pipeline", "data mining", "excel",
    "tableau", "power bi", "spreadsheet", "information technology",
    "it system", "server", "backend", "frontend", "full stack",
]


def load_esco_skills(csv_path: str = "data/raw/skills_en.csv") -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"ESCO file nahi mili: {csv_path}")
    return pd.read_csv(path)


def filter_tech_skills(df: pd.DataFrame) -> pd.DataFrame:
    """preferredLabel ya altLabels mein tech keyword ho, unhi skills ko rakhta hai."""
    df = df.copy()
    df["preferredLabel"] = df["preferredLabel"].fillna("")
    df["altLabels"] = df["altLabels"].fillna("")

    combined_text = (df["preferredLabel"] + " " + df["altLabels"]).str.lower()

    pattern = "|".join(TECH_KEYWORDS)
    mask = combined_text.str.contains(pattern, regex=True, na=False)

    return df[mask]


def convert_to_taxonomy_format(df: pd.DataFrame) -> pd.DataFrame:
    """ESCO format ko hamari taxonomy format (skill, category, aliases) mein badalta hai."""
    rows = []
    for _, row in df.iterrows():
        skill = str(row["preferredLabel"]).strip().lower()
        if not skill:
            continue

        alt_labels = str(row["altLabels"]).strip()
        if alt_labels and alt_labels.lower() != "nan":
            aliases = [a.strip().lower() for a in alt_labels.split("\n") if a.strip()]
            aliases_str = ", ".join(aliases)
        else:
            aliases_str = ""

        rows.append({"skill": skill, "category": "esco", "aliases": aliases_str})

    taxonomy_df = pd.DataFrame(rows)
    taxonomy_df = taxonomy_df.drop_duplicates(subset="skill")
    return taxonomy_df


if __name__ == "__main__":
    esco_df = load_esco_skills()
    print(f"Total ESCO skills: {len(esco_df)}")

    filtered_df = filter_tech_skills(esco_df)
    print(f"Tech/DS filtered skills: {len(filtered_df)}")

    taxonomy_df = convert_to_taxonomy_format(filtered_df)
    print(f"Final taxonomy rows: {len(taxonomy_df)}")

    output_path = "data/skills_taxonomy_esco.csv"
    taxonomy_df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")