import pdfplumber
from docx import Document
from pathlib import Path


def parse_pdf(file_path: str) -> str:
    """PDF se text nikalta hai, page-wise joda hua."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def parse_docx(file_path: str) -> str:
    """DOCX se text nikalta hai, paragraph-wise joda hua."""
    doc = Document(file_path)
    text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    return text.strip()


def parse_resume(file_path: str) -> str:
    """File extension dekh ke sahi parser choose karta hai."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"File nahi mili: {file_path}")

    if extension == ".pdf":
        return parse_pdf(file_path)
    elif extension == ".docx":
        return parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}. Sirf .pdf ya .docx chalega.")


if __name__ == "__main__":
    # quick manual test
    sample_path = "data/raw/sample_resume.docx"
    text = parse_resume(sample_path)
    print(text[:500])  # pehle 500 characters dikhao