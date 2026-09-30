from pathlib import Path


def parse_jd(file_path: str) -> str:
    """
    JD file se text nikalta hai. Agar .txt hai to seedha padhta hai,
    warna resume parser ke PDF/DOCX functions reuse karta hai.
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"JD file nahi mili: {file_path}")

    if extension == ".txt":
        return path.read_text(encoding="utf-8").strip()
    elif extension in (".pdf", ".docx"):
        from src.parsing.resume_parser import parse_resume
        return parse_resume(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")


if __name__ == "__main__":
    sample_path = "data/raw/sample_jd.txt"
    text = parse_jd(sample_path)
    print(text[:500])