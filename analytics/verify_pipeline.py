"""
End-to-end sanity check for the Mastery Insights analytics pipeline.

This is not a unit test suite — with 278 real attempts there isn't a lot to
unit-test in the traditional sense. It's a smoke test: run every stage in
order, then check each stage's output actually looks like what the next
stage expects, so a broken pipeline fails loudly here instead of silently
inside the FastAPI endpoint.

Run from the analytics/ directory, AFTER running the pipeline scripts once:
    python build_features.py
    python train_models.py          (optional — sanity check only, not required downstream)
    python shap_analysis.py
    python anomaly_detection.py
    python aggregate_insights.py
    python verify_pipeline.py       <- this script

Exits with a non-zero code and a clear message on the first failed check,
rather than a stack trace three files deep.
"""

import json
import sys
from pathlib import Path

import pandas as pd

FAILURES = []


def check(condition, message):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {message}")
    if not condition:
        FAILURES.append(message)


def require_file(path):
    exists = Path(path).exists()
    check(exists, f"{path} exists")
    return exists


print("=== 1. feature_table.csv (build_features.py) ===")
if require_file("feature_table.csv"):
    df = pd.read_csv("feature_table.csv")
    check(len(df) > 0, "feature_table.csv has at least one row")
    expected_cols = {
        "student_id", "topic", "subject", "difficulty", "current_mastery",
        "recent_accuracy", "avg_time_this_student", "attempt_number",
        "time_taken_seconds", "is_correct",
    }
    check(expected_cols.issubset(df.columns),
          f"feature_table.csv has all expected columns ({expected_cols})")
    check(df["is_correct"].isin([0, 1]).all(),
          "is_correct is always 0 or 1")
    check(df["current_mastery"].between(0, 1).all(),
          "current_mastery is always in [0, 1]")
    check(not df["student_id"].isna().any(),
          "no missing student_id")
    # first attempt per student should have no rolling history yet
    first_attempts = df[df["attempt_number"] == 1]
    check(first_attempts["recent_accuracy"].isna().all(),
          "every student's first attempt has recent_accuracy = NaN (no leakage)")

print("\n=== 2. SHAP explanations (shap_analysis.py) ===")
if require_file("shap_attempt_explanations.csv"):
    shap_df = pd.read_csv("shap_attempt_explanations.csv")
    check(len(shap_df) == len(df) if 'df' in dir() else True,
          "shap_attempt_explanations.csv has one row per attempt in feature_table.csv")
    check(shap_df["predicted_prob_correct"].between(0, 1).all(),
          "predicted_prob_correct is always in [0, 1]")
    check({"factor_1_feature", "factor_2_feature", "factor_3_feature"}.issubset(shap_df.columns),
          "top-3 SHAP factor columns are present")
require_file("shap_feature_importance.csv")
require_file("xgb_model_final.pkl")

print("\n=== 3. Anomaly scores (anomaly_detection.py) ===")
if require_file("anomaly_scores.csv"):
    anomaly_df = pd.read_csv("anomaly_scores.csv")
    check(len(anomaly_df) == len(df) if 'df' in dir() else True,
          "anomaly_scores.csv has one row per attempt in feature_table.csv")
    check(anomaly_df["is_anomaly"].dtype == bool or set(anomaly_df["is_anomaly"].unique()) <= {True, False},
          "is_anomaly is boolean")
    n_flagged = int(anomaly_df["is_anomaly"].sum())
    check(0 < n_flagged < len(anomaly_df),
          f"anomaly detection flagged a non-trivial subset ({n_flagged}/{len(anomaly_df)}, "
          f"not 0 and not everything)")

print("\n=== 4. Aggregated insights (aggregate_insights.py) ===")
if require_file("student_insights.json") and require_file("topic_insights.json"):
    with open("student_insights.json") as f:
        student_data = json.load(f)
    with open("topic_insights.json") as f:
        topic_data = json.load(f)

    check("cohort_summary" in student_data and "students" in student_data,
          "student_insights.json has cohort_summary + students")
    check("cohort_summary" in topic_data and "topics" in topic_data,
          "topic_insights.json has cohort_summary + topics")

    valid_levels = {"High", "Medium", "Low"}
    check(all(s["risk_level"] in valid_levels for s in student_data["students"]),
          "every student has a valid risk_level")
    check(all(t["risk_level"] in valid_levels for t in topic_data["topics"]),
          "every topic has a valid risk_level")
    check(all(0 <= s["avg_predicted_risk"] <= 1 for s in student_data["students"]),
          "avg_predicted_risk is always in [0, 1]")

    # cross-check: every student_id in student_insights should exist in
    # feature_table.csv, and counts should roughly line up
    if 'df' in dir():
        real_students = set(df["student_id"].unique())
        insight_students = {s["student_id"] for s in student_data["students"]}
        check(insight_students == real_students,
              "student_insights.json covers exactly the students in feature_table.csv "
              "(no students silently dropped or invented)")

    n_students = len(student_data["students"])
    n_topics = len(topic_data["topics"])
    print(f"\n  Summary: {n_students} students, {n_topics} topics in the aggregated output.")
    if student_data["students"]:
        top = student_data["students"][0]
        print(f"  Highest-risk student: #{top['student_id']} "
              f"(risk={top['avg_predicted_risk']}, level={top['risk_level']})")
    if topic_data["topics"]:
        top_t = topic_data["topics"][0]
        print(f"  Highest-risk topic: {top_t['topic']} "
              f"(risk={top_t['avg_predicted_risk']}, level={top_t['risk_level']})")

print("\n" + "=" * 60)
if FAILURES:
    print(f"FAILED: {len(FAILURES)} check(s) did not pass:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("All checks passed. Pipeline output is internally consistent.")
    print("Next: start the FastAPI server and hit /insights/students/at-risk "
          "and /insights/topics/heatmap to confirm the API layer serves this "
          "correctly, then check the '🧭 Insights' tab in the frontend.")
    sys.exit(0)
