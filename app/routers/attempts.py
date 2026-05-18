from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.adaptive import get_skill_state
from app.explainer import generate_explanation, generate_test_report, generate_question
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/attempts", tags=["attempts"])

class AttemptCreate(BaseModel):
    student_id: int
    question_id: int
    selected_answer: str
    time_taken_seconds: int

class ReportRequest(BaseModel):
    student_id: int
    question_ids: List[int]

@router.post("/")
def submit_attempt(a: AttemptCreate, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == a.question_id).first()
    is_correct = 1 if a.selected_answer == question.correct_answer else 0

    attempt = models.Attempt(
        student_id=a.student_id,
        question_id=a.question_id,
        selected_answer=a.selected_answer,
        is_correct=is_correct,
        time_taken_seconds=a.time_taken_seconds
    )
    db.add(attempt)
    db.commit()

    skill = get_skill_state(a.student_id, question.topic, db)

    return {
        "is_correct": bool(is_correct),
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "skill_level": skill
    }

@router.get("/next-question")
def next_question(
    student_id: int,
    subject: str,
    topic: str,
    standard: str = "JEE",
    exclude_ids: str = "",
    db: Session = Depends(get_db)
):
    db_attempted = [
        a.question_id for a in db.query(models.Attempt)
        .filter(models.Attempt.student_id == student_id).all()
    ]
    extra_excluded = [int(x) for x in exclude_ids.split(",") if x.strip().isdigit()]
    attempted_ids = list(set(db_attempted + extra_excluded))

    if topic == "all":
        question = db.query(models.Question).filter(
            models.Question.subject == subject,
            ~models.Question.id.in_(attempted_ids)
        ).order_by(models.Question.difficulty).first()
        skill = 0.3
        if question:
            skill = get_skill_state(student_id, question.topic, db)
    else:
        skill = get_skill_state(student_id, topic, db)

        if skill < 0.4:
            target_difficulty = (0.1, 0.4)
        elif skill < 0.7:
            target_difficulty = (0.4, 0.7)
        else:
            target_difficulty = (0.7, 1.0)

        question = db.query(models.Question).filter(
            models.Question.subject == subject,
            models.Question.topic == topic,
            models.Question.difficulty >= target_difficulty[0],
            models.Question.difficulty <= target_difficulty[1],
            ~models.Question.id.in_(attempted_ids)
        ).order_by(models.Question.difficulty).first()

        if not question:
            question = db.query(models.Question).filter(
                models.Question.subject == subject,
                models.Question.topic == topic,
                ~models.Question.id.in_(attempted_ids)
            ).first()

        if not question:
            try:
                generated = generate_question(subject, topic, 0.5, standard)
                question = models.Question(
                    subject=subject,
                    topic=topic,
                    difficulty=0.5,
                    question_text=generated["question_text"],
                    options=generated["options"],
                    correct_answer=generated["correct_answer"],
                    explanation=generated["explanation"]
                )
                db.add(question)
                db.commit()
                db.refresh(question)
            except Exception as e:
                print(f"Generation failed: {e}")
                return {"message": "No more questions available", "skill_level": 0.3}

    if not question:
        return {"message": "No more questions available", "skill_level": 0.3}

    return {
        "skill_level": skill,
        "question": {
            "id": question.id,
            "question_text": question.question_text,
            "options": question.options,
            "difficulty": question.difficulty,
            "topic": question.topic
        }
    }

@router.post("/report")
def generate_report(req: ReportRequest, db: Session = Depends(get_db)):
    attempts_data = []
    for qid in req.question_ids:
        attempt = db.query(models.Attempt).filter(
            models.Attempt.student_id == req.student_id,
            models.Attempt.question_id == qid
        ).order_by(models.Attempt.attempted_at.desc()).first()

        question = db.query(models.Question).filter(
            models.Question.id == qid
        ).first()

        if attempt and question:
            attempts_data.append({
                "question_text": question.question_text,
                "selected_answer": attempt.selected_answer,
                "correct_answer": question.correct_answer,
                "is_correct": bool(attempt.is_correct),
                "topic": question.topic,
                "explanation": question.explanation,
                "options": question.options
            })

    if not attempts_data:
        return {"report": "No attempts found.", "questions_data": []}

    report = generate_test_report(attempts_data)
    return {"report": report, "questions_data": attempts_data}