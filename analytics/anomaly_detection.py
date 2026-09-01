"""
Isolation Forest anomaly detection on attempt-level data.

This is unsupervised and independent of the XGBoost/SHAP risk model — it
flags attempts that look statistically unusual for a student (e.g. answering
much faster or slower than their own norm, or a result that strongly
contradicts their current mastery level), rather than predicting
correct/incorrect. Faculty use: "this student's last attempt doesn't fit
their usual pattern, worth a look" — separate signal from "this student is
at risk."

Uses feature_table.csv (real data only — same source as the final XGBoost
model in train_models.py / shap_analysis.py), so anomaly flags line up with
the same students and attempts the risk/SHAP layer already covers.

Run from the analytics/ directory:
    python anomaly_detection.py

Requires: pandas, numpy, scikit-learn (already in analytics/requirements.txt)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

RANDOM_STATE = 42
CONTAMINATION = 0.1  # expected anomaly fraction; tune once you see real flags

# ---------------------------------------------------------------------------
# 1. Load + engineer anomaly-detection features
# ---------------------------------------------------------------------------
df = pd.read_csv("feature_table.csv")
print("Loaded shape:", df.shape)

# A student's first attempt has no rolling history yet (recent_accuracy /
# avg_time_this_student are NaN by construction in build_features.py).
# IsolationForest can't take NaNs, so: impute with a neutral value AND keep
# an explicit "no history yet" flag as its own feature, rather than silently
# filling and losing that information.
df["is_first_attempt"] = df["recent_accuracy"].isna().astype(int)

global_median_recent_accuracy = df["recent_accuracy"].median()
df["recent_accuracy_filled"] = df["recent_accuracy"].fillna(
    global_median_recent_accuracy
)

# time_deviation = how much longer/shorter this attempt took vs the
# student's own running average. 0 when there's no prior average yet (first
# attempt), since "deviation from a history that doesn't exist" isn't
# meaningful — is_first_attempt already flags that case separately.
df["time_deviation"] = df["time_taken_seconds"] - df["avg_time_this_student"]
df["time_deviation"] = df["time_deviation"].fillna(0)

# mastery_surprise = actual outcome vs. what current_mastery would predict.
# Large positive: got it right despite low mastery (lucky guess, or mastery
# estimate is stale). Large negative: got it wrong despite high mastery
# (slip, distraction, or something worth a look).
df["mastery_surprise"] = df["is_correct"] - df["current_mastery"]

feature_cols = [
    "difficulty",
    "current_mastery",
    "recent_accuracy_filled",
    "time_taken_seconds",
    "time_deviation",
    "attempt_number",
    "is_correct",
    "mastery_surprise",
    "is_first_attempt",
]
X = df[feature_cols]
print("Feature columns:", feature_cols)

# ---------------------------------------------------------------------------
# 2. Fit Isolation Forest
# ---------------------------------------------------------------------------
iso_forest = IsolationForest(
    n_estimators=200,
    contamination=CONTAMINATION,
    random_state=RANDOM_STATE,
)
iso_forest.fit(X)

# decision_function: higher = more normal, lower/negative = more anomalous.
# predict: -1 = anomaly, 1 = normal.
df["anomaly_score"] = iso_forest.decision_function(X)
df["is_anomaly"] = (iso_forest.predict(X) == -1)

n_flagged = df["is_anomaly"].sum()
print(f"\nFlagged {n_flagged} / {len(df)} attempts as anomalies "
      f"({n_flagged / len(df):.1%})")

# ---------------------------------------------------------------------------
# 3. Human-readable reason per flagged attempt — simple rule-based labels
# layered on top of the ML flag, so faculty don't just see "anomaly=True"
# with no explanation.
# ---------------------------------------------------------------------------
def explain_anomaly(row):
    if not row["is_anomaly"]:
        return ""
    reasons = []
    if row["time_deviation"] > 15:
        reasons.append("much slower than usual for this student")
    elif row["time_deviation"] < -15:
        reasons.append("much faster than usual for this student")
    if row["mastery_surprise"] > 0.5:
        reasons.append("correct despite low current mastery")
    elif row["mastery_surprise"] < -0.5:
        reasons.append("incorrect despite high current mastery")
    if not reasons:
        reasons.append("unusual combination of factors (no single obvious cause)")
    return "; ".join(reasons)

df["anomaly_reason"] = df.apply(explain_anomaly, axis=1)

# ---------------------------------------------------------------------------
# 4. Save outputs for the aggregation layer
# ---------------------------------------------------------------------------
output_cols = [
    "student_id", "topic", "subject", "attempt_number", "difficulty",
    "current_mastery", "recent_accuracy", "avg_time_this_student",
    "time_taken_seconds", "is_correct", "anomaly_score", "is_anomaly",
    "anomaly_reason",
]
df[output_cols].to_csv("anomaly_scores.csv", index=False)
print("Saved anomaly_scores.csv (all attempts, scored)")

flagged = df[df["is_anomaly"]][output_cols].sort_values("anomaly_score")
print(f"\n=== Most anomalous attempts (top {min(10, len(flagged))}) ===")
print(flagged.head(10).to_string(index=False))

per_student = (
    df.groupby("student_id")["is_anomaly"]
    .sum()
    .sort_values(ascending=False)
)
per_student = per_student[per_student > 0]
print("\n=== Anomaly count per student (students with >=1 flag) ===")
print(per_student.to_string())

per_student.to_csv("anomaly_counts_by_student.csv", header=["anomaly_count"])
print("\nSaved anomaly_counts_by_student.csv")

print(
    "\nDone. Outputs ready for the aggregation layer:\n"
    "  - anomaly_scores.csv            (every attempt, scored + flagged + reason)\n"
    "  - anomaly_counts_by_student.csv (how many flags per student)\n"
    "\nNote: contamination=0.1 is a starting assumption, not a measured rate — "
    "with only 278 real attempts there's no ground truth for 'how many "
    "attempts are actually anomalous.' Re-run with a different contamination "
    "value and compare the flagged list against what a faculty member would "
    "actually consider unusual before treating this as final."
)
