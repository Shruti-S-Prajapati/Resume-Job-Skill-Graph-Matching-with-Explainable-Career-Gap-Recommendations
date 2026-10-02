from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.similarity.compare_approaches import compare_all_approaches

app = FastAPI(title="Resume-JD Skill Gap Matching API")


class MatchRequest(BaseModel):
    resume_path: str
    jd_path: str


@app.get("/")
def root():
    return {"status": "API is running"}


@app.post("/match")
def match(request: MatchRequest):
    try:
        result = compare_all_approaches(request.resume_path, request.jd_path)

        # sets ko list mein convert karna padega, JSON sets support nahi karta
        return {
            "skill_overlap_score": result["skill_overlap_score"],
            "tfidf_score": result["tfidf_score"],
            "avg_gap_distance": result["avg_gap_distance"],
            "matched_skills": sorted(result["matched"]),
            "missing_skills": sorted(result["missing"]),
            "extra_skills": sorted(result["extra"]),
            "gap_explanations": result["gap_explanations"],
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))