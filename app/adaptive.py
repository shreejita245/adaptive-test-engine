from sqlalchemy.orm import Session
from app import models

def get_skill_state(student_id: int, topic: str, db: Session):
    attempts = db.query(models.Attempt).join(
        models.Question, models.Attempt.question_id == models.Question.id
    ).filter(
        models.Attempt.student_id == student_id,
        models.Question.topic == topic
    ).order_by(models.Attempt.attempted_at).all()

    if not attempts:
        return 0.3

    p_learn = 0.2
    p_guess = 0.25
    p_slip  = 0.1
    p_known = 0.3

    for attempt in attempts:
        if attempt.is_correct:
            p_correct_given_known   = 1 - p_slip
            p_correct_given_unknown = p_guess
        else:
            p_correct_given_known   = p_slip
            p_correct_given_unknown = 1 - p_guess

        p_known = (p_correct_given_known * p_known) / (
            p_correct_given_known * p_known +
            p_correct_given_unknown * (1 - p_known)
        )
        p_known = p_known + (1 - p_known) * p_learn

    return round(p_known, 3)


def get_next_question(student_id: int, subject: str, topic: str, db: Session, standard: str = "JEE"):
    skill = get_skill_state(student_id, topic, db)

    if skill < 0.4:
        target_difficulty = (0.1, 0.4)
    elif skill < 0.7:
        target_difficulty = (0.4, 0.7)
    else:
        target_difficulty = (0.7, 1.0)

    attempted_ids = [
        a.question_id for a in db.query(models.Attempt)
        .filter(models.Attempt.student_id == student_id).all()
    ]

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

    return question, skill
