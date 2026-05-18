from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from pydantic import BaseModel
from typing import Dict

router = APIRouter(prefix="/questions", tags=["questions"])

class QuestionCreate(BaseModel):
    subject: str
    topic: str
    difficulty: float
    question_text: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str = None

@router.post("/")
def create_question(q: QuestionCreate, db: Session = Depends(get_db)):
    question = models.Question(**q.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.get("/")
def get_questions(subject: str = None, topic: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Question)
    if subject:
        query = query.filter(models.Question.subject == subject)
    if topic:
        query = query.filter(models.Question.topic == topic)
    return query.all()