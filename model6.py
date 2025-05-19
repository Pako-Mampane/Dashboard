import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import xgboost as xgb

# Load the dataset
df = pd.read_csv("data/cleaned_logs/cleaned9.csv")


# Create binary target variable
df["converted"] = (df["Request Type"] == "Product Purchase").astype(int)
print(df["converted"].value_counts())

# Select features
features = [
    "viewed_pricing_after_demo",
    "pages_after_demo",
    "sessions_after_demo",
    "time_to_purchase",
    "visit_count",
    "visitor_type",
    "hour",
    "day_of_week",
    "is_weekend",
    "Method",
    "Request Type",
    "Referrer",
    "Country",
]

X = df[features]
y = df["converted"]

# Encode categorical variables
categorical_cols = X.select_dtypes(include="object").columns
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    X.loc[:, col] = le.fit_transform(X[col]).astype(str)
    label_encoders[col] = le

# Train-test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Train model
model = XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]


xgb.plot_importance(model)
plt.title("Feature Importance")
plt.show()


# Evaluation
print("Classification Report:\n", classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("ROC AUC Score:", roc_auc_score(y_test, y_proba))
