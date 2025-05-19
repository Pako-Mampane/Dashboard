import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    precision_recall_curve,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import make_pipeline
import optuna
import joblib
import matplotlib.pyplot as plt
import json

# 1. Load and prepare data
df = pd.read_csv("cleaned7.csv")

# 2. Create target - ensure no leakage
df["converted"] = (df["Request Type"] == "Product Purchase").astype(int)

# 3. Remove leakage features and weak predictors
df = df.drop(
    columns=[
        "Revenue",
        "Price",
        "Timestamp",
        "IP Address",
        "Session ID",
        "URL",
        "IP_Session",
        "Method",
        "Response Time (ms)",
        "Status Code",
        "visit_count",
        "Request Type",
    ]
)


# 5. Prepare features
X = df.drop(columns=["converted"])
y = df["converted"]

# 6. Train-test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 7. Define preprocessing
categorical_features = ["Sales Agent", "Country", "Product", "visitor_type"]
numeric_features = [
    "Pages per Session",
    "Session Duration",
]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", MinMaxScaler(), numeric_features),
    ]
)


# 8. Custom metric for optimization
def conversion_profit(y_true, y_pred):
    """
    Business-oriented metric that values:
    - High recall (capturing conversions)
    - Moderate precision (avoiding too many false alarms)
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    profit_score = (
        tp * 10 - fp * 1
    )  # Example: $10 value per conversion, $1 cost per false lead
    return profit_score


# 9. Hyperparameter tuning with business focus
def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 9),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "scale_pos_weight": trial.suggest_float("scale_pos_weight", 1, 100),
        "gamma": trial.suggest_float("gamma", 0, 1),
        "reg_alpha": trial.suggest_float("reg_alpha", 0, 10),
        "reg_lambda": trial.suggest_float("reg_lambda", 0, 10),
    }

    model = XGBClassifier(
        **params,
        use_label_encoder=False,
        eval_metric="aucpr",  # Focus on precision-recall
        random_state=42,
    )

    pipeline = make_pipeline(
        preprocessor, SMOTE(sampling_strategy=0.3, random_state=42), model
    )

    # Use stratified CV with our custom metric
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores = []
    for train_idx, val_idx in cv.split(X_train, y_train):
        X_fold_train, y_fold_train = X_train.iloc[train_idx], y_train.iloc[train_idx]
        X_val, y_val = X_train.iloc[val_idx], y_train.iloc[val_idx]

        pipeline.fit(X_fold_train, y_fold_train)
        y_val_pred = pipeline.predict(X_val)
        scores.append(conversion_profit(y_val, y_val_pred))

    return np.mean(scores)


study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=30)

# 10. Train final model
best_params = study.best_params
final_model = make_pipeline(
    preprocessor,
    SMOTE(sampling_strategy=0.3, random_state=42),
    XGBClassifier(
        **best_params, use_label_encoder=False, eval_metric="aucpr", random_state=42
    ),
)

final_model.fit(X_train, y_train)

# 11. Business-optimized threshold selection
y_proba = final_model.predict_proba(X_test)[:, 1]

# Find threshold that maximizes profit
thresholds = np.linspace(0, 1, 100)
profits = []
for thresh in thresholds:
    y_pred = (y_proba >= thresh).astype(int)
    profits.append(conversion_profit(y_test, y_pred))

best_threshold = thresholds[np.argmax(profits)]
print(f"Optimal business threshold: {best_threshold:.3f}")

# 12. Final evaluation
y_pred = (y_proba >= best_threshold).astype(int)

print("\nBusiness Impact Analysis:")
print(f"Estimated Value: ${np.max(profits):.2f} per {len(y_test)} samples")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nROC AUC Score:", roc_auc_score(y_test, y_proba))
print("Average Precision Score:", average_precision_score(y_test, y_proba))

# 13. Save model artifacts
joblib.dump(final_model, "conversion_model2.pkl")
joblib.dump(preprocessor, "preprocessor2.pkl")

# Save threshold with business context
with open("best_threshold2.json", "w") as f:
    json.dump(
        {
            "threshold": float(best_threshold),
            "expected_value": float(np.max(profits) / len(y_test)),
        },
        f,
    )
