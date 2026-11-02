import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import joblib

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("sorting_dataset.csv")

# -----------------------------
# Features and Target
# -----------------------------
X = df.drop(columns=["execution_time"])
y = df["execution_time"]

# -----------------------------
# Train Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# Preprocessing
# -----------------------------
preprocessor = ColumnTransformer(
    transformers=[
        ("algorithm", OneHotEncoder(handle_unknown="ignore"), ["algorithm"])
    ],
    remainder="passthrough"
)

# -----------------------------
# Pipeline
# -----------------------------
pipe = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(
        n_estimators=100,
        random_state=42
    ))
])
pipe.fit(X_train, y_train)

y_pred = pipe.predict(X_test)

print("R² Score :", r2_score(y_test, y_pred))

joblib.dump(pipe, "sorting_model.pkl")

print("\nModel Saved Successfully!")