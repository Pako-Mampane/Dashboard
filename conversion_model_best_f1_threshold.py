## 1. Imports
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    f1_score,
)
import matplotlib.pyplot as plt
import seaborn as sns
import json
import joblib

## 2. Load data
df = pd.read_csv("data/cleaned_logs/cleaned6.csv")

## 3. Define the target: conversion = 1 if product was purchased
df["converted"] = (df["Request Type"] == "Product Purchase").astype(int)

## 4. Drop irrelevant or leakage-prone columns
df = df.drop(
    columns=[
        "Revenue",
        "Price",
        "Timestamp",
        "IP Address",
        "Session ID",
        "URL",
        "IP_Session",
        "Response Time (ms)",
        "Status Code",
        "visit_count",
    ]
)

## 5. Encode categorical features
categorical_cols = [
    "Sales Agent",
    "Country",
    "Referrer",
    "Product",
    "visitor_type",
    "Method",
]
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

## 6. Prepare features and target
X = df.drop(columns=["converted", "Request Type"])
y = df["converted"]

## 7. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

## 8. Compute scale_pos_weight to balance classes
neg, pos = np.bincount(y_train)
scale_pos_weight = neg / pos

## 9. Train XGBoost Classifier with class weighting
model = XGBClassifier(
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42,
    scale_pos_weight=scale_pos_weight,
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
)
model.fit(X_train, y_train)

## 10. Evaluate and find best F1 threshold
y_proba = model.predict_proba(X_test)[:, 1]
precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)

f1_scores = [
    2 * (p * r) / (p + r + 1e-10) for p, r in zip(precisions[:-1], recalls[:-1])
]
best_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_idx]

print(f"\n✅ Best Threshold (Max F1): {best_threshold:.4f}")
y_pred = (y_proba >= best_threshold).astype(int)

## 11. Final evaluation
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))
print("ROC AUC Score:", roc_auc_score(y_test, y_proba))

## 12. Save best threshold for dashboard use
with open("best_threshold.json", "w") as f:
    json.dump({"threshold": float(best_threshold)}, f)
joblib.dump(model, "conversion_model.pkl")
joblib.dump(label_encoders, "encoders.pkl")

## 13. Plot Precision-Recall Curve
plt.figure(figsize=(10, 6))
plt.plot(thresholds, precisions[:-1], label="Precision")
plt.plot(thresholds, recalls[:-1], label="Recall")
plt.axvline(
    best_threshold,
    color="red",
    linestyle="--",
    label=f"Best F1 Threshold: {best_threshold:.2f}",
)
plt.xlabel("Threshold")
plt.ylabel("Score")
plt.title("Precision-Recall vs Threshold")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
