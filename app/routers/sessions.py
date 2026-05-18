from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionCreate(BaseModel):
    student_id: int
    exam_name: str
    mode: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    num_questions: int
    correct: int
    wrong: int
    unattempted: int
    score: int
    max_score: int
    duration_mins: int
    question_ids: List[int]


@router.post("/")
def create_session(s: SessionCreate, db: Session = Depends(get_db)):
    session = models.TestSession(
        student_id=s.student_id,
        exam_name=s.exam_name,
        mode=s.mode,
        subject=s.subject,
        topic=s.topic,
        num_questions=s.num_questions,
        correct=s.correct,
        wrong=s.wrong,
        unattempted=s.unattempted,
        score=s.score,
        max_score=s.max_score,
        duration_mins=s.duration_mins,
        question_ids=s.question_ids
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id}


@router.get("/{student_id}")
def get_sessions(student_id: int, db: Session = Depends(get_db)):
    sessions = db.query(models.TestSession).filter(
        models.TestSession.student_id == student_id
    ).order_by(models.TestSession.completed_at.desc()).all()

    result = []
    for s in sessions:
        # Fetch per-question details for this session
        questions_detail = []
        for qid in (s.question_ids or []):
            question = db.query(models.Question).filter(models.Question.id == qid).first()
            attempt = db.query(models.Attempt).filter(
                models.Attempt.student_id == student_id,
                models.Attempt.question_id == qid
            ).order_by(models.Attempt.attempted_at.desc()).first()

            if question:
                questions_detail.append({
                    "question_id": qid,
                    "question_text": question.question_text,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "explanation": question.explanation,
                    "topic": question.topic,
                    "difficulty": question.difficulty,
                    "selected_answer": attempt.selected_answer if attempt else None,
                    "is_correct": bool(attempt.is_correct) if attempt else None
                })

        accuracy = round((s.correct / s.num_questions) * 100, 1) if s.num_questions else 0

        result.append({
            "id": s.id,
            "exam_name": s.exam_name,
            "mode": s.mode,
            "subject": s.subject,
            "topic": s.topic,
            "num_questions": s.num_questions,
            "correct": s.correct,
            "wrong": s.wrong,
            "unattempted": s.unattempted,
            "score": s.score,
            "max_score": s.max_score,
            "accuracy": accuracy,
            "duration_mins": s.duration_mins,
            "completed_at": str(s.completed_at),
            "questions": questions_detail
        })

    return result
