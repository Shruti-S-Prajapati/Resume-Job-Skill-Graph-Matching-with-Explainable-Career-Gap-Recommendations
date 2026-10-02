from src.similarity.tfidf_similarity import compute_tfidf_similarity


def test_identical_text_gives_high_similarity():
    text = "Experienced Python developer with SQL and data analysis skills."
    score = compute_tfidf_similarity(text, text)
    assert score > 95.0


def test_completely_different_text_gives_low_similarity():
    resume = "Python SQL data analysis pandas numpy machine learning"
    jd = "Carpentry woodworking furniture building hand tools craftsmanship"
    score = compute_tfidf_similarity(resume, jd)
    assert score < 20.0


def test_similarity_score_is_within_valid_range():
    resume = "Python developer with data science background"
    jd = "Looking for a data scientist skilled in Python"
    score = compute_tfidf_similarity(resume, jd)
    assert 0.0 <= score <= 100.0