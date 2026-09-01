
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

attempts_df = pd.read_sql("SELECT * FROM attempts ORDER BY student_id, attempted_at", engine)
questions_df = pd.read_sql("SELECT id, subject, topic, difficulty FROM questions", engine)

print("Attempts shape:", attempts_df.shape)
print(attempts_df.head())
print("\nColumns:", list(attempts_df.columns))
print("\nQuestions shape:", questions_df.shape)
print(questions_df.head())

merged_df = attempts_df.merge(
    questions_df,
    left_on="question_id",
    right_on="id",
    suffixes=("_attempt", "_question")
)

mastery_tracker = {}
recent_results_tracker = {}   # key: student_id -> list of past 1/0 results, in time order
results = []
recent_results_tracker = {}
time_tracker = {}
attempt_count_tracker = {}
P_LEARN = 0.2
P_GUESS = 0.25
P_SLIP = 0.1
DEFAULT_MASTERY = 0.3

merged_df = merged_df.sort_values(["student_id", "attempted_at"])

for _, row in merged_df.iterrows():
    student_id = row["student_id"]
    topic = row["topic"]
    key = (student_id, topic)
    mastery_before = mastery_tracker.get(key, DEFAULT_MASTERY)
    past_results = recent_results_tracker.get(student_id, [])

    if len(past_results) == 0:
        recent_accuracy = None
    else:
        last_5 = past_results[-5:]
        recent_accuracy = sum(last_5) / len(last_5)
    is_correct = row["is_correct"]

    past_times = time_tracker.get(student_id, [])

    if len(past_times) == 0:
        avg_time_this_student = None
    else:
        avg_time_this_student = sum(past_times) / len(past_times)

    attempt_number = attempt_count_tracker.get(student_id, 0) + 1

    if is_correct:
        numerator = mastery_before * (1 - P_SLIP)
        denominator = numerator + (1 - mastery_before) * P_GUESS
        p_given_evidence = numerator / denominator
    else:
        numerator = mastery_before * P_SLIP
        denominator = numerator + (1 - mastery_before) * (1 - P_GUESS)
        p_given_evidence = numerator / denominator

    mastery_after = p_given_evidence + (1 - p_given_evidence) * P_LEARN

    results.append({
        "student_id": student_id,
        "topic": topic,
        "subject": row["subject"],
        "difficulty": row["difficulty"],
        "current_mastery": mastery_before,
        "recent_accuracy": recent_accuracy,
        "avg_time_this_student": avg_time_this_student,
        "attempt_number": attempt_number,
        "time_taken_seconds": row["time_taken_seconds"],
        "is_correct": is_correct
    })

    mastery_tracker[key] = mastery_after
    past_results.append(1 if is_correct else 0)
    recent_results_tracker[student_id] = past_results
    past_times.append(row["time_taken_seconds"])
    time_tracker[student_id] = past_times
    attempt_count_tracker[student_id] = attempt_number

feature_df = pd.DataFrame(results)
print("Feature table shape:", feature_df.shape)
print(feature_df.head(10))
print(feature_df[["student_id", "attempt_number", "current_mastery", "recent_accuracy", "avg_time_this_student", "is_correct"]].head(10))


feature_df.to_csv("analytics/feature_table.csv", index=False)
print("\nSaved feature_table.csv with shape:", feature_df.shape)