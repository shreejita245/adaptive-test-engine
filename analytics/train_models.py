import pandas as pd

feature_df = pd.read_csv("analytics/feature_table.csv")
print("Loaded shape:", feature_df.shape)

topic_counts = feature_df["topic"].value_counts()
print("\nTopic counts:\n", topic_counts)

rare_topics = topic_counts[topic_counts < 10].index
feature_df["topic_grouped"] = feature_df["topic"].apply(
    lambda t: "other" if t in rare_topics else t
)
print("\nGrouped topic counts:\n", feature_df["topic_grouped"].value_counts())

encoded_df = pd.get_dummies(feature_df, columns=["topic_grouped"])
print("After encoding shape:", encoded_df.shape)
print(encoded_df.columns.tolist())

X = encoded_df.drop(columns=["student_id", "is_correct", "subject", "topic"])
y = encoded_df["is_correct"]

print("X shape:", X.shape)
print("y shape:", y.shape)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)

from xgboost import XGBClassifier

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
print("Model trained successfully")

from sklearn.metrics import accuracy_score, classification_report

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

baseline_accuracy = max(y_test.mean(), 1 - y_test.mean())
print("Baseline accuracy (always predict majority class):", baseline_accuracy)

from sklearn.model_selection import cross_val_score

cv_model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    scale_pos_weight=scale_pos_weight,
    random_state=42
)

cv_scores = cross_val_score(cv_model, X, y, cv=5, scoring="accuracy")

print("\nCross-validation scores (5 folds):", cv_scores)
print("Mean CV accuracy:", cv_scores.mean())
print("Std deviation:", cv_scores.std())