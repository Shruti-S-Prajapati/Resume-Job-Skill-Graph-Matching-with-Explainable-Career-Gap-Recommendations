import sys
from pathlib import Path

# taaki src/ modules import ho sakein
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import tempfile
import pandas as pd

from src.similarity.compare_approaches import compare_all_approaches
from src.ranking.gap_ranker import rank_gaps_from_result
from src.evaluation.audit_logger import log_correction

st.set_page_config(page_title="Resume-JD Skill Gap Matcher", layout="wide")

st.title("Resume - JD Skill Gap Matching")
st.caption("Upload a resume and a job description to see match score, missing skills, and personalized recommendations.")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
with col2:
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])

if resume_file and jd_file:
    # uploaded files ko temporarily disk pe save karna padega (parsers file path maangte hain)
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.name).suffix) as tmp_resume:
        tmp_resume.write(resume_file.read())
        resume_path = tmp_resume.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(jd_file.name).suffix) as tmp_jd:
        tmp_jd.write(jd_file.read())
        jd_path = tmp_jd.name

    if st.button("Analyze Match", type="primary"):
        with st.spinner("Analyzing..."):
            try:
                result = compare_all_approaches(resume_path, jd_path)
                ranked = rank_gaps_from_result(result["jd_text"], result["missing"], result["gap_explanations"])

                st.success("Analysis complete")

                # --- Score summary ---
                st.subheader("Match Scores")
                score_col1, score_col2, score_col3 = st.columns(3)
                score_col1.metric("Skill-Overlap Score", f"{result['skill_overlap_score']}%")
                score_col2.metric("TF-IDF Baseline Score", f"{result['tfidf_score']}%")
                score_col3.metric("Avg Gap Distance (Graph)", result['avg_gap_distance'])

                # --- Matched skills ---
                st.subheader(f"Matched Skills ({len(result['matched'])})")
                if result['matched']:
                    st.write(", ".join(sorted(result['matched'])))
                else:
                    st.write("No matched skills found.")

                # --- Ranked gap recommendations ---
                st.subheader("Recommended Skills to Learn (Ranked by Priority)")
                if ranked:
                    rank_df = pd.DataFrame(ranked)
                    rank_df.insert(0, "Rank", range(1, len(rank_df) + 1))
                    rank_df = rank_df.rename(columns={
                        "skill": "Skill",
                        "jd_frequency": "JD Frequency",
                        "graph_distance": "Graph Distance",
                        "nearest_known_skill": "Nearest Known Skill",
                        "priority_score": "Priority Score",
                    })
                    st.dataframe(rank_df, use_container_width=True, hide_index=True)
                else:
                    st.write("No skill gaps found - great match!")

                # --- Manual correction ---
                st.subheader("Manual Correction")
                st.caption("Don't agree with the extracted skills? Adjust them below.")

                all_detected = sorted(result['matched'] | result['missing'])
                corrected_skills = st.multiselect(
                    "Edit matched skills list",
                    options=all_detected,
                    default=sorted(result['matched']),
                )
                if st.button("Save Correction"):
                    log_correction(
                        resume_name=resume_file.name,
                        jd_name=jd_file.name,
                        original_skills=result['matched'],
                        corrected_skills=set(corrected_skills),
                    )
                    st.success(f"Correction saved to audit log: {len(corrected_skills)} skills marked as matched.")

                # --- Extra skills (resume has, JD doesn't need) ---
                with st.expander(f"Extra Skills in Resume ({len(result['extra'])})"):
                    st.write(", ".join(sorted(result['extra'])) if result['extra'] else "None")

            except Exception as e:
                st.error(f"Something went wrong: {e}")
else:
    st.info("Please upload both a resume and a job description to begin.")