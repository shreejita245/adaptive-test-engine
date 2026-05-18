import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jee_data_base import DataBase, Filter
from app.database import SessionLocal
from app import models

db_session = SessionLocal()

# map chapter names to our topic names
CHAPTER_MAP = {
    "probability": "probability",
    "matrices-and-determinants": "matrices",
    "trigonometric-ratio-and-identites": "trigonometry",
    "differentiation": "calculus",
    "differential-equations": "calculus",
    "straight-lines-and-pair-of-straight-lines": "coordinate geometry",
    "mathematical-induction": "binomial theorem",
    "vector-algebra": "vector algebra",
    "height-and-distance": "trigonometry",
    "logarithm": "quadratic equations",
    "complex-numbers": "complex numbers",
    "sequence-and-series": "sequence and series",
    "permutation-and-combination": "permutation and combination",
    "sets-relation-and-function": "sets and relations",
    "binomial-theorem": "binomial theorem",
    "limit-continuity-and-differentiability": "limits continuity and differentiability",
    "application-of-derivatives": "application of derivatives",
    "definite-integration": "definite integration",
    "indefinite-integration": "indefinite integration",
    "quadratic-equation": "quadratic equations",
    "conic-section": "conic sections",
    "3d-geometry": "3d geometry",
    "statistics": "statistics",
}

DIFFICULTY_MAP = {
    "easy": 0.3,
    "medium": 0.6,
    "hard": 0.9
}

jee_db = DataBase()
f = Filter(jee_db.chapters_dict)

inserted = 0
skipped_img = 0
skipped_type = 0
skipped_dup = 0

for chapter_slug, topic_name in CHAPTER_MAP.items():
    try:
        f.reset()
        f.by_chapter(chapter_slug)
        questions = f.current_set
        print(f"\n📚 {chapter_slug} → {topic_name}: {len(questions)} questions")

        for q in questions:
            # skip image questions
            if q.isImgQuestion or any(q.isImgOption):
                skipped_img += 1
                continue

            # skip non-MCQ
            if q.type != "mcq":
                skipped_type += 1
                continue

            # skip if no correct answer
            if not q.correct_options:
                skipped_type += 1
                continue

            # build options dict
            options = {}
            for opt in q.options:
                options[opt["identifier"]] = opt["content"]

            if len(options) != 4:
                skipped_type += 1
                continue

            correct_answer = q.correct_options[0]
            if correct_answer not in ["A", "B", "C", "D"]:
                skipped_type += 1
                continue

            difficulty = DIFFICULTY_MAP.get(q.difficulty, 0.5)
            question_text = q.question.strip()

            # skip duplicates
            exists = db_session.query(models.Question).filter(
                models.Question.question_text == question_text
            ).first()
            if exists:
                skipped_dup += 1
                continue

            question = models.Question(
                subject="mathematics",
                topic=topic_name,
                difficulty=difficulty,
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                explanation=q.explanation if q.explanation else ""
            )
            db_session.add(question)
            inserted += 1

        db_session.commit()
        print(f"  ✅ Inserted so far: {inserted}")

    except Exception as e:
        print(f"  ❌ Error on {chapter_slug}: {e}")

db_session.close()
print(f"\n🎉 Done!")
print(f"✅ Inserted: {inserted}")
print(f"⏭ Skipped (image): {skipped_img}")
print(f"⏭ Skipped (non-MCQ/invalid): {skipped_type}")
print(f"⏭ Skipped (duplicate): {skipped_dup}")