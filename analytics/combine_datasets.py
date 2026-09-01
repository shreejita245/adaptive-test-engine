import pandas as pd

real_df = pd.read_csv("analytics/feature_table.csv")
synthetic_df = pd.read_csv("analytics/synthetic_feature_table.csv")

real_df["is_synthetic"] = False
real_df["archetype"] = "real"

print("Real shape:", real_df.shape)
print("Synthetic shape:", synthetic_df.shape)

shared_columns = [
    "student_id", "topic", "subject", "difficulty",
    "current_mastery", "attempt_number", "is_correct",
    "is_synthetic", "archetype"
]

real_subset = real_df[shared_columns]
synthetic_subset = synthetic_df[shared_columns]

combined_df = pd.concat([real_subset, synthetic_subset], ignore_index=True)

print("Combined shape:", combined_df.shape)
print(combined_df["is_synthetic"].value_counts())

combined_df.to_csv("analytics/combined_feature_table.csv", index=False)
print("Saved combined_feature_table.csv")