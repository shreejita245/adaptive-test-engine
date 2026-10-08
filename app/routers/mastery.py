from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.bkt import update_mastery
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(prefix="/mastery", tags=["mastery"])


class QuestionResult(BaseModel):
    topic: str
    correct: bool


class MasteryUpdateRequest(BaseModel):
    student_id: int
    questions: List[QuestionResult]


@router.post("/update")
def update_mastery_after_test(req: MasteryUpdateRequest, db: Session = Depends(get_db)):
    if not req.questions:
        return {"message": "No questions provided", "mastery": {}}

    topic_results: dict[str, list] = {}
    for q in req.questions:
        topic_results.setdefault(q.topic, []).append(q.correct)

    updated = {}

    for topic, corrects in topic_results.items():
        record = db.query(models.TopicMastery).filter(
            models.TopicMastery.student_id == req.student_id,
            models.TopicMastery.topic == topic
        ).first()

        current_mastery = record.mastery if record else 0.30

        new_mastery = current_mastery
        for correct in corrects:
            new_mastery = update_mastery(new_mastery, correct)

        new_attempts = (record.attempts if record else 0) + len(corrects)

        if record:
            record.mastery = new_mastery
            record.attempts = new_attempts
            record.updated_at = datetime.utcnow()
        else:
            record = models.TopicMastery(
                student_id=req.student_id,
                topic=topic,
                mastery=new_mastery,
                attempts=new_attempts
            )
            db.add(record)

        updated[topic] = round(new_mastery, 4)

    db.commit()
    return {"message": "Mastery updated", "mastery": updated}


@router.get("/{student_id}")
def get_mastery(student_id: int, db: Session = Depends(get_db)):
    records = db.query(models.TopicMastery).filter(
        models.TopicMastery.student_id == student_id
    ).order_by(models.TopicMastery.mastery.asc()).all()

    return [
        {
            "topic": r.topic,
            "mastery": round(r.mastery, 4),
            "attempts": r.attempts,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None
        }
        for r in records
    ]
