import pandas as pd

combined_df = pd.read_csv("analytics/combined_feature_table.csv")
print("Loaded combined shape:", combined_df.shape)

encoded_df = pd.get_dummies(combined_df, columns=["topic"])
print("After encoding shape:", encoded_df.shape)
X = encoded_df.drop(columns=["student_id", "is_correct", "subject", "is_synthetic", "archetype"])
y = encoded_df["is_correct"]

print("X shape:", X.shape)
print("y shape:", y.shape)

from sklearn.model_selection import train_test_split, cross_val_score
from xgboost import XGBClassifier

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
print("scale_pos_weight:", scale_pos_weight)

model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

model.fit(X_train, y_train)

from sklearn.metrics import accuracy_score, classification_report

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

baseline_accuracy = max(y_test.mean(), 1 - y_test.mean())
print("Baseline accuracy:", baseline_accuracy)

cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print("\nCross-validation scores (5 folds):", cv_scores)
print("Mean CV accuracy:", cv_scores.mean())
print("Std deviation:", cv_scores.std())