"""
SHAP explainability layer on top of the final XGBoost model
(topic-grouped encoding, real attempt data — the model chosen in
train_models.py as the guaranteed-core model for the dashboard).

This script:
  1. Rebuilds the exact same model as train_models.py (same encoding,
     same split, same hyperparameters) so the explanations describe
     the actual model going into the product, not a re-tuned one.
  2. Fits a SHAP TreeExplainer and computes SHAP values for every
     attempt in feature_table.csv (not just the test split) — the
     aggregation layer needs an explanation for every row, since
     faculty need to see "why" for every student/topic, not just a
     20% sample.
  3. Saves three outputs the next steps (aggregation layer, dashboard)
     will consume directly:
       - shap_feature_importance.csv   (global ranking)
       - shap_attempt_explanations.csv (per-attempt top-3 reasons)
       - shap_summary_bar.png          (global importance plot)
  4. Pickles the trained model + explainer so the FastAPI endpoint
     added later doesn't need to retrain on every request.

Run from the analytics/ directory:
    python shap_analysis.py

Requires: pandas, scikit-learn, xgboost, shap, matplotlib
(xgboost and shap are not yet in requirements.txt — see
analytics/requirements.txt added alongside this script.)
"""

import pickle
import pandas as pd
import numpy as np

RANDOM_STATE = 42

# ---------------------------------------------------------------------------
# 1. Rebuild the exact model from train_models.py
# ---------------------------------------------------------------------------
feature_df = pd.read_csv("feature_table.csv")
print("Loaded shape:", feature_df.shape)

topic_counts = feature_df["topic"].value_counts()
rare_topics = topic_counts[topic_counts < 10].index
feature_df["topic_grouped"] = feature_df["topic"].apply(
    lambda t: "other" if t in rare_topics else t
)

encoded_df = pd.get_dummies(feature_df, columns=["topic_grouped"])
X = encoded_df.drop(columns=["student_id", "is_correct", "subject", "topic"])
y = encoded_df["is_correct"]
print("X shape:", X.shape, "| y shape:", y.shape)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)

from xgboost import XGBClassifier

scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    scale_pos_weight=scale_pos_weight,
    random_state=RANDOM_STATE,
)
model.fit(X_train, y_train)

from sklearn.metrics import accuracy_score

print("Sanity-check test accuracy (should match train_models.py):",
      round(accuracy_score(y_test, model.predict(X_test)), 4))

# ---------------------------------------------------------------------------
# 2. SHAP — explain every attempt, not just the test split
# ---------------------------------------------------------------------------
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)  # shape: (n_attempts, n_features)
print("SHAP values shape:", shap_values.shape)

# ---------------------------------------------------------------------------
# 3a. Global feature importance — mean absolute SHAP value per feature
# ---------------------------------------------------------------------------
mean_abs_shap = np.abs(shap_values).mean(axis=0)
importance_df = pd.DataFrame({
    "feature": X.columns,
    "mean_abs_shap": mean_abs_shap,
}).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

print("\n=== Global feature importance (top 10) ===")
print(importance_df.head(10).to_string(index=False))

importance_df.to_csv("shap_feature_importance.csv", index=False)

# ---------------------------------------------------------------------------
# 3b. Per-attempt explanations — top 3 contributing features per row,
# with direction (pushed toward "correct" or toward "incorrect") and the
# feature's actual value for that attempt. This is what the aggregation
# layer will roll up into "why is this student/topic at risk."
# ---------------------------------------------------------------------------
def top_factors_for_row(row_idx, k=3):
    row_shap = shap_values[row_idx]
    row_vals = X.iloc[row_idx]
    order = np.argsort(-np.abs(row_shap))[:k]
    factors = []
    for rank, col_idx in enumerate(order, start=1):
        feat_name = X.columns[col_idx]
        shap_val = row_shap[col_idx]
        feat_val = row_vals.iloc[col_idx]
        direction = "toward correct" if shap_val > 0 else "toward incorrect"
        factors.append((rank, feat_name, feat_val, shap_val, direction))
    return factors

records = []
predicted_prob = model.predict_proba(X)[:, 1]
for i in range(len(X)):
    base = {
        "student_id": feature_df.iloc[i]["student_id"],
        "topic": feature_df.iloc[i]["topic"],
        "subject": feature_df.iloc[i]["subject"],
        "attempt_number": feature_df.iloc[i]["attempt_number"],
        "is_correct": feature_df.iloc[i]["is_correct"],
        "predicted_prob_correct": round(float(predicted_prob[i]), 4),
        "base_value": round(float(explainer.expected_value), 4),
    }
    for rank, feat_name, feat_val, shap_val, direction in top_factors_for_row(i):
        base[f"factor_{rank}_feature"] = feat_name
        base[f"factor_{rank}_value"] = feat_val
        base[f"factor_{rank}_shap"] = round(float(shap_val), 4)
        base[f"factor_{rank}_direction"] = direction
    records.append(base)

explanations_df = pd.DataFrame(records)
explanations_df.to_csv("shap_attempt_explanations.csv", index=False)
print(f"\nSaved per-attempt explanations for {len(explanations_df)} attempts "
      f"to shap_attempt_explanations.csv")
print("\nExample explanation (first row):")
print(explanations_df.iloc[0].to_string())

# ---------------------------------------------------------------------------
# 4. Global summary plot
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

shap.summary_plot(shap_values, X, plot_type="bar", show=False)
plt.tight_layout()
plt.savefig("shap_summary_bar.png", dpi=150)
plt.close()
print("\nSaved shap_summary_bar.png")

# ---------------------------------------------------------------------------
# 5. Persist model + explainer for reuse in the FastAPI endpoint
# ---------------------------------------------------------------------------
with open("xgb_model_final.pkl", "wb") as f:
    pickle.dump({
        "model": model,
        "feature_columns": list(X.columns),
        "rare_topics": list(rare_topics),
    }, f)
print("Saved xgb_model_final.pkl (model + feature schema for the API layer)")

print(
    "\nDone. Outputs ready for the aggregation layer:\n"
    "  - shap_feature_importance.csv   (which features matter most, overall)\n"
    "  - shap_attempt_explanations.csv (why each attempt was predicted "
    "correct/incorrect)\n"
    "  - shap_summary_bar.png          (chart for the dashboard or report)\n"
    "  - xgb_model_final.pkl           (trained model, ready for the API)"
)
