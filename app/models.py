from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)        # e.g. "math"
    topic = Column(String, index=True)          # e.g. "quadratic equations"
    difficulty = Column(Float)                  # 0.0 (easy) to 1.0 (hard)
    question_text = Column(String)
    options = Column(JSON)                      # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer = Column(String)             # "A", "B", "C", or "D"
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    question_id = Column(Integer, index=True)
    selected_answer = Column(String)
    is_correct = Column(Integer)                # 1 = correct, 0 = wrong
    time_taken_seconds = Column(Integer)
    attempted_at = Column(DateTime, default=func.now())


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    exam_name = Column(String)           # "JEE Mains", "NEET", etc.
    mode = Column(String)                # "full", "subject", "topic"
    subject = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    num_questions = Column(Integer)
    correct = Column(Integer)
    wrong = Column(Integer)
    unattempted = Column(Integer)
    score = Column(Integer)              # net score (+4/-1 or +4/-2)
    max_score = Column(Integer)
    duration_mins = Column(Integer)
    question_ids = Column(JSON)          # list of question ids in order
    completed_at = Column(DateTime, default=func.now())