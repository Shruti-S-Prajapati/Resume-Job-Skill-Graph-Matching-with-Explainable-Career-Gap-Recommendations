import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path("data/audit_logs.db")


def init_audit_db():
    """Database aur table banata hai agar pehle se nahi hai."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            resume_name TEXT,
            jd_name TEXT,
            original_matched_skills TEXT,
            corrected_matched_skills TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_correction(resume_name: str, jd_name: str, original_skills: set, corrected_skills: set):
    """Ek correction event ko database mein save karta hai (audit trail)."""
    init_audit_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO skill_corrections
            (timestamp, resume_name, jd_name, original_matched_skills, corrected_matched_skills)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.datetime.now(datetime.timezone.utc).isoformat(),
        resume_name,
        jd_name,
        ", ".join(sorted(original_skills)),
        ", ".join(sorted(corrected_skills)),
    ))
    conn.commit()
    conn.close()


def get_all_corrections() -> list:
    """Saare logged corrections return karta hai (audit review ke liye)."""
    init_audit_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM skill_corrections ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    log_correction(
        resume_name="test_resume.pdf",
        jd_name="test_jd.txt",
        original_skills={"python", "sql"},
        corrected_skills={"python", "sql", "docker"},
    )
    print("Logged test correction. All logs:")
    for row in get_all_corrections():
        print(row)