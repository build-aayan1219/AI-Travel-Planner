# ============================================================
#  ml/train_season_model.py
#  Trains Best Season Predictor on master_travel_dataset.csv
#  Algorithm: Decision Tree Classifier
#
#  Predicts: best season to visit a destination
#  based on destination type, state, scores, budget level
#
#  HOW TO RUN:
#  python ml/train_season_model.py
# ============================================================

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib, os

print("=" * 50)
print("  Best Season Predictor — Model Training")
print("=" * 50)

BASE      = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "..", "data", "master_travel_dataset.csv")

# ── STEP 1: LOAD ─────────────────────────────────────────────
print("\n[1/5] Loading dataset...")
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print(f"❌ File not found: {DATA_PATH}")
    print("   Make sure master_travel_dataset.csv is in your data/ folder.")
    exit()
print(f"     Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ── STEP 2: PREPARE FEATURES ─────────────────────────────────
print("\n[2/5] Preparing features...")

# We want to predict best_season from destination characteristics
feature_cols = ["destination_type", "state", "adventure_score", "culture_score",
                "nature_score", "beach_score", "wildlife_score", "budget_level",
                "avg_temp_jan", "avg_temp_may", "avg_temp_oct",
                "annual_tourists_lakhs", "rating"]

feature_cols = [c for c in feature_cols if c in df.columns]
target_col   = "best_season"

if target_col not in df.columns:
    print(f"❌ Column '{target_col}' not found.")
    print(f"   Available: {list(df.columns)}")
    exit()

df = df.dropna(subset=feature_cols + [target_col])
print(f"     Features: {feature_cols}")
print(f"     Seasons  : {df[target_col].unique()}")

# ── STEP 3: ENCODE ───────────────────────────────────────────
print("\n[3/5] Encoding...")
encoders = {}
cat_cols  = ["destination_type", "state", "budget_level"]
for col in [c for c in cat_cols if c in df.columns]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le
    print(f"     {col}: {len(le.classes_)} classes")

target_le = LabelEncoder()
y = target_le.fit_transform(df[target_col].astype(str))
print(f"     Target seasons: {list(target_le.classes_)}")

X = df[feature_cols]

# ── STEP 4: TRAIN ────────────────────────────────────────────
print("\n[4/5] Training Decision Tree...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42
)
print(f"     Train: {len(X_train)} | Test: {len(X_test)}")

model = DecisionTreeClassifier(
    max_depth=8,
    min_samples_split=2,
    random_state=42
)
model.fit(X_train, y_train)
print("     Done!")

# ── STEP 5: EVALUATE ─────────────────────────────────────────
print("\n[5/5] Evaluating...")
y_pred   = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"     Accuracy: {accuracy*100:.1f}%")
print("\n  Classification Report:")
try:
    print(classification_report(
        y_test, y_pred,
        target_names=target_le.classes_,
        zero_division=0
    ))
except Exception:
    pass

print("\n  Feature Importance:")
for feat, imp in sorted(zip(feature_cols, model.feature_importances_), key=lambda x: -x[1]):
    if imp > 0.01:
        bar = "█" * int(imp * 40)
        print(f"     {feat:<25} {bar} {imp:.3f}")

# ── SAVE ─────────────────────────────────────────────────────
joblib.dump(model,        os.path.join(BASE, "season_model.pkl"))
joblib.dump(encoders,     os.path.join(BASE, "season_encoders.pkl"))
joblib.dump(target_le,    os.path.join(BASE, "season_target_encoder.pkl"))
joblib.dump(feature_cols, os.path.join(BASE, "season_features.pkl"))

print(f"\n✅ Saved: ml/season_model.pkl")
print("🎉 Season model training complete!")
print("=" * 50)