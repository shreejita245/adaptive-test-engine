from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    topic = Column(String, index=True)
    difficulty = Column(Float)
    question_text = Column(String)
    options = Column(JSON)
    correct_answer = Column(String)
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
    is_correct = Column(Integer)
    time_taken_seconds = Column(Integer)
    attempted_at = Column(DateTime, default=func.now())


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    exam_name = Column(String)
    mode = Column(String)
    subject = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    num_questions = Column(Integer)
    correct = Column(Integer)
    wrong = Column(Integer)
    unattempted = Column(Integer)
    score = Column(Integer)
    max_score = Column(Integer)
    duration_mins = Column(Integer)
    question_ids = Column(JSON)
    completed_at = Column(DateTime, default=func.now())


class TopicMastery(Base):
    __tablename__ = "topic_mastery"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    topic = Column(String, index=True)
    mastery = Column(Float)
    attempts = Column(Integer, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "topic", name="uq_student_topic"),
    )
