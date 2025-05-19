import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import joblib
import json
import os

# 1. Load data
df = pd.read_csv("data/cleaned_logs/cleaned9.csv")

# 2. Target: Predict conversion
df["converted"] = (df["Request Type"] == "Product Purchase").astype(int)

# 3. Drop leakage-prone and redundant features
df = df.drop(
    columns=[
        "Request Type",
        "Revenue",
        "Timestamp",
        "IP Address",
        "Session ID",
        "IP_Session",
        "Method",
        "URL",
        "Status Code",
        "Response Time (ms)",
        "Price",
    ]
)

# 4. Define X, y
X = df.drop(columns=["converted"])
X["viewed_pricing_after_demo"] = X["viewed_pricing_after_demo"].astype(int)
y = df["converted"]

# 5. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)

# 6. Feature categories
num_features = [
    "pages_after_demo",
    "sessions_after_demo",
    "time_to_purchase",
    "visit_count",
    "hour",
    "day_of_week",
    "month",
    "year",
    "is_weekend",
]
cat_features = ["Country", "Sales Agent", "Referrer", "Product", "visitor_type"]
bool_features = ["viewed_pricing_after_demo"]

# 7. Preprocessing
preprocessor = ColumnTransformer(
    [
        (
            "num",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            ),
            num_features,
        ),
        (
            "bool",
            Pipeline([("imputer", SimpleImputer(strategy="most_frequent"))]),
            bool_features,
        ),
        (
            "cat",
            Pipeline(
                [
                    (
                        "imputer",
                        SimpleImputer(strategy="constant", fill_value="missing"),
                    ),
                    (
                        "onehot",
                        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    ),
                ]
            ),
            cat_features,
        ),
    ]
)

# 8. Modeling pipeline
model = Pipeline(
    [
        ("preprocessor", preprocessor),
        (
            "classifier",
            XGBClassifier(
                eval_metric="logloss",
                use_label_encoder=False,
                scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
                random_state=42,
            ),
        ),
    ]
)
# 9. Train
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

# Basic model
model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")

# Define parameter grid
param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [3, 6, 9],
    "learning_rate": [0.01, 0.1, 0.3],
    "subsample": [0.8, 1],
    "colsample_bytree": [0.8, 1],
}

# GridSearchCV setup
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=5,
    scoring="roc_auc",  # or 'accuracy', 'f1', etc.
    verbose=1,
    n_jobs=-1,
)

# Fit
grid_search.fit(X_train, y_train)

# Best params and score
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)


# # 10. Evaluate & find best threshold
# y_proba = model.predict_proba(X_test)[:, 1]
# prec, rec, thresholds = precision_recall_curve(y_test, y_proba)
# f1_scores = [2 * p * r / (p + r + 1e-8) for p, r in zip(prec[:-1], rec[:-1])]
# best_idx = np.argmax(f1_scores)
# best_thresh = thresholds[best_idx]

# print(f"\n✅ Best Threshold (F1): {best_thresh:.4f}")
# print("Classification Report:\n", classification_report(y_test, y_proba >= best_thresh))
# print("ROC AUC Score:", roc_auc_score(y_test, y_proba))

# # 11. Save model and threshold
# os.makedirs("models", exist_ok=True)
# joblib.dump(model, "models/conversion_model_enhanced.pkl")
# with open("models/conversion_threshold_enhanced.json", "w") as f:
#     json.dump({"threshold": float(best_thresh)}, f)

# # 12. Plot
# plt.figure(figsize=(8, 6))
# plt.plot(thresholds, prec[:-1], label="Precision")
# plt.plot(thresholds, rec[:-1], label="Recall")
# plt.axvline(best_thresh, color="red", linestyle="--", label="Best F1 Threshold")
# plt.xlabel("Threshold")
# plt.ylabel("Score")
# plt.title("Precision vs Recall by Threshold")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()
