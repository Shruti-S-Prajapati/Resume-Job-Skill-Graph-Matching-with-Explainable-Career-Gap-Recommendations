from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.parsing.resume_parser import parse_resume
from src.parsing.jd_parser import parse_jd


def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Resume aur JD ke poore text ko TF-IDF vectors mein convert karta hai,
    aur unke beech cosine similarity nikalta hai (0 to 1 ke beech).
    Ye humara BASELINE approach hai — skill-specific nahi, poora text compare karta hai.
    """
    documents = [resume_text, jd_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    similarity_score = similarity_matrix[0][0]

    return round(float(similarity_score) * 100, 2)


if __name__ == "__main__":
    resume_text = parse_resume("data/raw/sample_resume.docx")
    jd_text = parse_jd("data/raw/sample_jd.txt")

    score = compute_tfidf_similarity(resume_text, jd_text)
    print(f"TF-IDF Cosine Similarity Score: {score}%")