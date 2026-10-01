import re
from pathlib import Path
import pandas as pd


def load_exclude_list(path: str = "data/exclude_skills.txt") -> set:
    p = Path(path)
    if not p.exists():
        return set()
    with open(p, encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())


def clean_skill_name(skill: str) -> str:
    """ESCO ke parenthetical qualifiers hatata hai, e.g. 'python (computer programming)' -> 'python'"""
    cleaned = re.sub(r"\s*\([^)]*\)", "", skill).strip()
    return cleaned


def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["skill"] = df["skill"].str.strip().str.lower().apply(clean_skill_name)
    df["aliases"] = df["aliases"].fillna("")
    return df


def merge_taxonomies(manual_path: str, esco_path: str, output_path: str):
    manual_df = load_csv(manual_path)
    esco_df = load_csv(esco_path)

    combined = pd.concat([manual_df, esco_df], ignore_index=True)

    merged = {}
    for _, row in combined.iterrows():
        skill = row["skill"]
        if not skill:
            continue
        aliases = set(a.strip() for a in str(row["aliases"]).split(",") if a.strip())

        if skill in merged:
            merged[skill]["aliases"].update(aliases)
        else:
            merged[skill] = {
                "category": row["category"],
                "aliases": aliases,
            }

    rows = []
    for skill, data in merged.items():
        rows.append({
            "skill": skill,
            "category": data["category"],
            "aliases": ", ".join(sorted(data["aliases"])),
        })

    final_df = pd.DataFrame(rows)

    exclude_set = load_exclude_list()
    final_df = final_df[~final_df["skill"].isin(exclude_set)]

    final_df = final_df.sort_values("skill").reset_index(drop=True)
    final_df.to_csv(output_path, index=False)

    print(f"Manual skills: {len(manual_df)}")
    print(f"ESCO skills: {len(esco_df)}")
    print(f"Final merged (deduplicated): {len(final_df)}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    merge_taxonomies(
        manual_path="data/skills_taxonomy_manual.csv",
        esco_path="data/skills_taxonomy_esco.csv",
        output_path="data/skills_taxonomy.csv",
    )