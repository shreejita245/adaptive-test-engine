import pandas as pd
import random
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

questions_df = pd.read_sql("SELECT id, subject, topic, difficulty FROM questions", engine)
print("Loaded questions:", questions_df.shape)

ARCHETYPES = {
    "strong": {"p_learn": 0.35, "p_slip": 0.05, "starting_mastery": 0.4},
    "average": {"p_learn": 0.2, "p_slip": 0.1, "starting_mastery": 0.3},
    "struggling": {"p_learn": 0.1, "p_slip": 0.2, "starting_mastery": 0.2},
}
P_GUESS = 0.25

STUDENTS_PER_ARCHETYPE = 15
ATTEMPTS_PER_STUDENT = 35

synthetic_results = []
virtual_student_counter = 1000

for archetype_name, params in ARCHETYPES.items():
    p_learn = params["p_learn"]
    p_slip = params["p_slip"]
    starting_mastery = params["starting_mastery"]

    for _ in range(STUDENTS_PER_ARCHETYPE):
        student_id = virtual_student_counter
        virtual_student_counter += 1

        mastery_tracker = {}

        for attempt_num in range(1, ATTEMPTS_PER_STUDENT + 1):
            question = questions_df.sample(1).iloc[0]
            topic = question["topic"]
            difficulty = question["difficulty"]

            key = topic
            mastery_before = mastery_tracker.get(key, starting_mastery)

            p_correct = (mastery_before * (1 - p_slip)) + ((1 - mastery_before) * P_GUESS)
            is_correct = 1 if random.random() < p_correct else 0

            if is_correct:
                numerator = mastery_before * (1 - p_slip)
                denominator = numerator + (1 - mastery_before) * P_GUESS
                p_given_evidence = numerator / denominator
            else:
                numerator = mastery_before * p_slip
                denominator = numerator + (1 - mastery_before) * (1 - P_GUESS)
                p_given_evidence = numerator / denominator

            mastery_after = p_given_evidence + (1 - p_given_evidence) * p_learn

            synthetic_results.append({
                "student_id": student_id,
                "topic": topic,
                "subject": question["subject"],
                "difficulty": difficulty,
                "current_mastery": mastery_before,
                "attempt_number": attempt_num,
                "time_taken_seconds": None,
                "is_correct": is_correct,
                "is_synthetic": True,
                "archetype": archetype_name
            })

            mastery_tracker[key] = mastery_after

            synthetic_df = pd.DataFrame(synthetic_results)
print("\nSynthetic data shape:", synthetic_df.shape)
print(synthetic_df.groupby("archetype")["is_correct"].mean())

synthetic_df.to_csv("analytics/synthetic_feature_table.csv", index=False)
print("Saved synthetic_feature_table.csv")