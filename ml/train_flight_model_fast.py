# Quick single-threaded flight trainer (faster)
# Trains flight model with fewer trees and single thread to avoid long parallel jobs
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib, os

print("=" * 50)
print("  Flight Price Predictor (FAST) — Model Training")
print("=" * 50)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data", "flight_prices.csv")

print("\n[1/5] Loading dataset...")
try:
    df = pd.read_csv(DATA)
except FileNotFoundError:
    print(f"❌ File not found: {DATA}")
    exit()

print(f"     Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

print("\n[2/5] Encoding categorical features...")
cat_cols = ["airline", "source_city", "departure_time", "stops",
            "arrival_time", "destination_city", "class"]

available_cats = [c for c in cat_cols if c in df.columns]
encoders = {}
for col in available_cats:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le
    print(f"     {col}: {len(le.classes_)} unique values")

all_features = ["airline", "source_city", "departure_time", "stops",
                "arrival_time", "destination_city", "class", "duration", "days_left"]
feature_cols = [c for c in all_features if c in df.columns]
print(f"\n[3/5] Features selected: {feature_cols}")

# Drop NA and setup data
df = df.dropna(subset=feature_cols + ["price"]) if len(feature_cols)>0 else df.dropna(subset=["price"]) 
X = df[feature_cols]
y = df["price"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"     Train: {len(X_train)} | Test: {len(X_test)}")

print("\n[4/5] Training Random Forest (fast, 50 trees, single-thread)...")
model = RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=1)
model.fit(X_train, y_train)
print("     Done!")

print("\n[5/5] Evaluating...")
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)
print(f"     MAE    : ₹{mae:,.0f}")
print(f"     R²     : {r2:.3f}")

print("\n  Feature Importance:")
for feat, imp in sorted(zip(feature_cols, model.feature_importances_), key=lambda x: -x[1]):
    print(f"     {feat:<20} {'█' * int(imp*40)} {imp:.3f}")

joblib.dump(model,        os.path.join(BASE, "flight_model.pkl"))
joblib.dump(encoders,     os.path.join(BASE, "flight_encoders.pkl"))
joblib.dump(feature_cols, os.path.join(BASE, "flight_features.pkl"))

print(f"\n✅ Model saved: ml/flight_model.pkl")
print("=" * 50)
