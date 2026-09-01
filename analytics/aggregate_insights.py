"""
Aggregation layer: rolls up attempt-level SHAP explanations and Isolation
Forest anomaly scores into per-student and per-topic (cohort) summaries.

This is the bridge between the ML layer (analytics/shap_analysis.py,
analytics/anomaly_detection.py) and the FastAPI endpoint / React dashboard
— everything downstream reads the two JSON files this script produces
instead of touching the raw attempt-level CSVs directly.

Prerequisites (run these first, in order):
    python shap_analysis.py       -> shap_attempt_explanations.csv
    python anomaly_detection.py   -> anomaly_scores.csv

Run from the analytics/ directory:
    python aggregate_insights.py

Outputs:
    student_insights.json  - per-student risk summary, top weak topics,
                              top factors behind their mistakes, anomaly flags
    topic_insights.json    - per-topic (cohort) summary for the weak-topic
                              heatmap: accuracy, avg risk, top drivers

Requires: pandas (already in analytics/requirements.txt)
"""

import json
from datetime import datetime, timezone

import pandas as pd
import numpy as np

SHAP_FILE = "shap_attempt_explanations.csv"
ANOMALY_FILE = "anomaly_scores.csv"

# ---------------------------------------------------------------------------
# 1. Load + merge the two attempt-level sources
# ---------------------------------------------------------------------------
shap_df = pd.read_csv(SHAP_FILE)
anomaly_df = pd.read_csv(ANOMALY_FILE)

print("SHAP explanations:", shap_df.shape)
print("Anomaly scores:", anomaly_df.shape)

# attempt_number is sequential per student (see build_features.py), so
# (student_id, attempt_number) uniquely identifies an attempt — safer join
# key than topic, since a student can attempt the same topic more than once.
merged = shap_df.merge(
    anomaly_df[["student_id", "attempt_number", "anomaly_score",
                "is_anomaly", "anomaly_reason"]],
    on=["student_id", "attempt_number"],
    how="left",
    validate="one_to_one",
)
if merged["is_anomaly"].isna().any():
    n_missing = merged["is_anomaly"].isna().sum()
    print(f"Warning: {n_missing} attempts have SHAP explanations but no "
          f"matching anomaly score — check that both scripts ran on the "
          f"same feature_table.csv")
merged["is_anomaly"] = merged["is_anomaly"].fillna(False)

merged["predicted_risk"] = 1 - merged["predicted_prob_correct"]

# ---------------------------------------------------------------------------
# 2. Per-student aggregation
# ---------------------------------------------------------------------------
def top_topics_by_risk(group, k=3):
    topic_stats = (
        group.groupby("topic")
        .agg(accuracy=("is_correct", "mean"),
             avg_risk=("predicted_risk", "mean"),
             n_attempts=("is_correct", "count"))
        .reset_index()
        .sort_values("avg_risk", ascending=False)
    )
    return topic_stats.head(k).to_dict(orient="records")


def top_mistake_drivers(group, k=3):
    """Among this student's incorrect attempts, which single factor most
    often pushed the prediction toward 'incorrect'? Frequency-based, not
    magnitude-based, so it answers 'what keeps coming up' rather than
    'what mattered most in one attempt'."""
    wrong = group[group["is_correct"] == 0]
    if wrong.empty:
        return []
    toward_wrong = wrong[wrong["factor_1_direction"] == "toward incorrect"]
    source = toward_wrong if not toward_wrong.empty else wrong
    counts = source["factor_1_feature"].value_counts().head(k)
    return [{"feature": feat, "count": int(cnt)} for feat, cnt in counts.items()]


student_records = []
for student_id, group in merged.groupby("student_id"):
    anomalies = group[group["is_anomaly"]][
        ["topic", "attempt_number", "anomaly_reason"]
    ].to_dict(orient="records")

    student_records.append({
        "student_id": int(student_id),
        "total_attempts": int(len(group)),
        "overall_accuracy": round(float(group["is_correct"].mean()), 4),
        "avg_predicted_risk": round(float(group["predicted_risk"].mean()), 4),
        "top_risk_topics": top_topics_by_risk(group),
        "top_mistake_drivers": top_mistake_drivers(group),
        "anomaly_count": int(group["is_anomaly"].sum()),
        "anomaly_flags": anomalies,
    })

student_df = pd.DataFrame(student_records)

# Risk banding: tertiles across the cohort. With ~25 students this is a
# relative ranking within this cohort, not a calibrated absolute risk score
# — re-derive the thresholds if the student count grows meaningfully.
if len(student_df) >= 3:
    low_cut, high_cut = student_df["avg_predicted_risk"].quantile([1 / 3, 2 / 3])
else:
    low_cut = high_cut = student_df["avg_predicted_risk"].median()


def risk_label(x):
    if x >= high_cut:
        return "High"
    elif x >= low_cut:
        return "Medium"
    return "Low"


for rec in student_records:
    rec["risk_level"] = risk_label(rec["avg_predicted_risk"])

student_records.sort(key=lambda r: r["avg_predicted_risk"], reverse=True)

# ---------------------------------------------------------------------------
# 3. Per-topic (cohort) aggregation — feeds the weak-topic heatmap
# ---------------------------------------------------------------------------
def top_topic_drivers(group, k=3):
    wrong = group[group["is_correct"] == 0]
    if wrong.empty:
        return []
    toward_wrong = wrong[wrong["factor_1_direction"] == "toward incorrect"]
    source = toward_wrong if not toward_wrong.empty else wrong
    counts = source["factor_1_feature"].value_counts().head(k)
    return [{"feature": feat, "count": int(cnt)} for feat, cnt in counts.items()]


topic_records = []
for topic, group in merged.groupby("topic"):
    subject = group["subject"].mode().iat[0] if not group["subject"].empty else None
    topic_records.append({
        "topic": topic,
        "subject": subject,
        "n_attempts": int(len(group)),
        "n_students": int(group["student_id"].nunique()),
        "accuracy": round(float(group["is_correct"].mean()), 4),
        "avg_predicted_risk": round(float(group["predicted_risk"].mean()), 4),
        "top_drivers": top_topic_drivers(group),
    })

topic_df = pd.DataFrame(topic_records)
if len(topic_df) >= 3:
    t_low, t_high = topic_df["avg_predicted_risk"].quantile([1 / 3, 2 / 3])
else:
    t_low = t_high = topic_df["avg_predicted_risk"].median()

def topic_risk_label(x):
    if x >= t_high:
        return "High"
    elif x >= t_low:
        return "Medium"
    return "Low"


for rec in topic_records:
    rec["risk_level"] = topic_risk_label(rec["avg_predicted_risk"])

topic_records.sort(key=lambda r: r["avg_predicted_risk"], reverse=True)

# ---------------------------------------------------------------------------
# 4. Cohort-level summary + write outputs
# ---------------------------------------------------------------------------
cohort_summary = {
    "n_students": int(merged["student_id"].nunique()),
    "n_attempts": int(len(merged)),
    "n_topics": int(merged["topic"].nunique()),
    "overall_accuracy": round(float(merged["is_correct"].mean()), 4),
    "overall_avg_risk": round(float(merged["predicted_risk"].mean()), 4),
    "total_anomalies": int(merged["is_anomaly"].sum()),
}

generated_at = datetime.now(timezone.utc).isoformat()

student_output = {"generated_at": generated_at, "cohort_summary": cohort_summary,
                   "students": student_records}
topic_output = {"generated_at": generated_at, "cohort_summary": cohort_summary,
                 "topics": topic_records}

with open("student_insights.json", "w") as f:
    json.dump(student_output, f, indent=2)
with open("topic_insights.json", "w") as f:
    json.dump(topic_output, f, indent=2)

print(f"\nCohort summary: {cohort_summary}")
print(f"\nSaved student_insights.json ({len(student_records)} students)")
print(f"Saved topic_insights.json ({len(topic_records)} topics)")
print("\nTop 5 highest-risk students:")
for rec in student_records[:5]:
    print(f"  student {rec['student_id']}: risk={rec['avg_predicted_risk']} "
          f"({rec['risk_level']}), weakest topic="
          f"{rec['top_risk_topics'][0]['topic'] if rec['top_risk_topics'] else 'n/a'}")
print("\nTop 5 highest-risk topics:")
for rec in topic_records[:5]:
    print(f"  {rec['topic']}: risk={rec['avg_predicted_risk']} "
          f"({rec['risk_level']}), accuracy={rec['accuracy']}")
