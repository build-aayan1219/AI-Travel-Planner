# ============================================================
#  ml/train_model.py
#  Trains Trip Cost Predictor on data/trip_data.csv
#  Algorithm: Random Forest Regressor
#
#  HOW TO RUN:
#  cd travel-planner
#  source venv/bin/activate
#  python ml/train_model.py
# ============================================================

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib, os

print("=" * 50)
print("  Trip Cost Predictor — Model Training")
print("=" * 50)

BASE      = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "..", "data", "trip_data.csv")

# ── STEP 1: LOAD DATA ────────────────────────────────────────
print("\n[1/5] Loading dataset...")
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    print(f"❌ File not found: {DATA_PATH}")
    print("   Make sure trip_data.csv is in your data/ folder.")
    exit()
print(f"     Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ── STEP 2: ENCODE CATEGORICAL COLUMNS ───────────────────────
print("\n[2/5] Encoding categorical features...")
cat_cols = ["destination_type", "trip_type", "season", "transport_mode", "hotel_quality"]
encoders = {}
for col in cat_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        print(f"     {col}: {list(le.classes_)}")

# ── STEP 3: SPLIT FEATURES AND TARGET ────────────────────────
print("\n[3/5] Splitting data...")
feature_cols = ["destination_type", "days", "group_size", "trip_type",
                "season", "transport_mode", "hotel_quality"]
feature_cols = [c for c in feature_cols if c in df.columns]

X = df[feature_cols]
y = df["total_cost"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"     Train: {len(X_train)} | Test: {len(X_test)}")

# ── STEP 4: TRAIN MODEL ───────────────────────────────────────
print("\n[4/5] Training Random Forest (200 trees)...")
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    min_samples_split=3,
    random_state=42
)
model.fit(X_train, y_train)
print("     Done!")

# ── STEP 5: EVALUATE ─────────────────────────────────────────
print("\n[5/5] Evaluating model...")
y_pred = model.predict(X_test)
mae    = mean_absolute_error(y_test, y_pred)
r2     = r2_score(y_test, y_pred)
print(f"     MAE      : ₹{mae:,.0f}")
print(f"     R² Score : {r2:.3f}")
print(f"     Accuracy : ~{max(0, r2*100):.1f}%")

print("\n  Feature Importance:")
for feat, imp in sorted(zip(feature_cols, model.feature_importances_), key=lambda x: -x[1]):
    bar = "█" * int(imp * 40)
    print(f"     {feat:<22} {bar} {imp:.3f}")

# ── SAVE MODEL ───────────────────────────────────────────────
joblib.dump(model,        os.path.join(BASE, "cost_predictor_model.pkl"))
joblib.dump(encoders,     os.path.join(BASE, "encoders.pkl"))
joblib.dump(feature_cols, os.path.join(BASE, "feature_columns.pkl"))

print(f"\n✅ Saved: ml/cost_predictor_model.pkl")
print(f"✅ Saved: ml/encoders.pkl")
print(f"✅ Saved: ml/feature_columns.pkl")
print("\n🎉 Training complete! Run: streamlit run app.py")
print("=" * 50)