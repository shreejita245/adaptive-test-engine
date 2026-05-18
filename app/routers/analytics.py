from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.adaptive import get_skill_state

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/leaderboard/all")
def get_leaderboard(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()

    leaderboard = []
    for student in students:
        attempts = db.query(models.Attempt).filter(
            models.Attempt.student_id == student.id
        ).all()

        if not attempts:
            continue

        total = len(attempts)
        correct = sum(a.is_correct for a in attempts)
        accuracy = round(correct / total * 100, 1)

        topics = set()
        for a in attempts:
            q = db.query(models.Question).filter(models.Question.id == a.question_id).first()
            if q:
                topics.add(q.topic)

        avg_skill = round(
            sum(get_skill_state(student.id, t, db) for t in topics) / len(topics) * 100, 1
        ) if topics else 0

        leaderboard.append({
            "student_id": student.id,
            "name": student.name,
            "email": student.email,
            "accuracy": accuracy,
            "total_attempts": total,
            "avg_skill": avg_skill,
            "score": round((accuracy * 0.5) + (avg_skill * 0.5), 1)
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1

    return leaderboard


@router.get("/progress/{student_id}")
def get_progress(student_id: int, db: Session = Depends(get_db)):
    attempts = db.query(models.Attempt).filter(
        models.Attempt.student_id == student_id
    ).order_by(models.Attempt.attempted_at).all()

    if not attempts:
        return []

    progress = []
    correct_so_far = 0

    for i, attempt in enumerate(attempts):
        correct_so_far += attempt.is_correct
        question = db.query(models.Question).filter(
            models.Question.id == attempt.question_id
        ).first()
        progress.append({
            "attempt_number": i + 1,
            "is_correct": bool(attempt.is_correct),
            "topic": question.topic if question else "unknown",
            "difficulty": question.difficulty if question else 0,
            "time_taken": attempt.time_taken_seconds,
            "running_accuracy": round(correct_so_far / (i + 1) * 100, 1),
            "attempted_at": str(attempt.attempted_at)
        })

    return progress


@router.get("/{student_id}")
def get_student_analytics(student_id: int, db: Session = Depends(get_db)):
    attempts = db.query(models.Attempt).filter(
        models.Attempt.student_id == student_id
    ).all()

    if not attempts:
        return {"message": "No attempts yet"}

    total = len(attempts)
    correct = sum(a.is_correct for a in attempts)
    accuracy = round(correct / total * 100, 1)

    topic_stats = {}
    for attempt in attempts:
        question = db.query(models.Question).filter(
            models.Question.id == attempt.question_id
        ).first()
        topic = question.topic
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0}
        topic_stats[topic]["total"] += 1
        topic_stats[topic]["correct"] += attempt.is_correct

    topic_breakdown = []
    for topic, stats in topic_stats.items():
        skill = get_skill_state(student_id, topic, db)
        topic_breakdown.append({
            "topic": topic,
            "accuracy": round(stats["correct"] / stats["total"] * 100, 1),
            "attempts": stats["total"],
            "skill_level": skill,
            "mastered": skill >= 0.8
        })

    weak_topics = [t for t in topic_breakdown if t["skill_level"] < 0.5]
    strong_topics = [t for t in topic_breakdown if t["skill_level"] >= 0.8]

    avg_time = round(
        sum(a.time_taken_seconds for a in attempts) / total, 1
    )

    return {
        "student_id": student_id,
        "total_attempts": total,
        "overall_accuracy": accuracy,
        "avg_time_per_question": avg_time,
        "topic_breakdown": topic_breakdown,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics
    }