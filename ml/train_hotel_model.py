# ============================================================
#  ml/train_hotel_model.py
#  Trains hotel price predictor on hotel_prices.csv
#  (Google Indian Hotel Data — Kaggle)
#
#  HOW TO RUN:
#  python ml/train_hotel_model.py
# ============================================================
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib, os

print("=" * 50)
print("  Hotel Price Predictor — Model Training")
print("=" * 50)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data", "hotel_prices.csv")

print("\n[1/5] Loading dataset...")
try:
    try:
        df = pd.read_csv(DATA)
    except UnicodeDecodeError:
        df = pd.read_csv(DATA, encoding="latin-1")
except FileNotFoundError:
    print(f"❌ File not found: {DATA}")
    print("   Download from: kaggle.com/datasets/alvinmanojalex/google-indian-hotel-data")
    print("   Rename the CSV file to: hotel_prices.csv")
    print("   Place it in your data/ folder")
    exit()

print(f"     Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"     Columns: {list(df.columns)}")

# Standardise column names
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
print(f"\n[2/5] Cleaned columns: {list(df.columns)}")

# Find the price column (handles different Kaggle column names)
price_col = None
for possible in ["price", "rate", "cost", "price_per_night", "avg_price", "minimum_nights","hotel_price"]:
    if possible in df.columns:
        price_col = possible
        break

if not price_col:
    print("❌ Could not find a price column.")
    print(f"   Available columns: {list(df.columns)}")
    print("   Edit train_hotel_model.py and set price_col manually.")
    exit()

print(f"     Price column found: '{price_col}'")
df = df.dropna(subset=[price_col])
df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
df = df.dropna(subset=[price_col])
df = df[df[price_col] > 0]

# Find useful feature columns
possible_features = ["city", "hotel_type", "rating", "stars", "review_score",
                     "review_count", "number_of_reviews", "hotel_class",
                     "location", "state", "category", "type"]
feature_cols = [c for c in possible_features if c in df.columns]

if len(feature_cols) < 2:
    print("⚠️  Very few usable columns found. Using all text columns as features.")
    feature_cols = [c for c in df.columns if c != price_col and
                    df[c].dtype == object][:5]

print(f"\n[3/5] Features: {feature_cols}")

encoders = {}
for col in feature_cols:
    if df[col].dtype == object:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

X = df[feature_cols]
y = df[price_col]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"     Train: {len(X_train)} | Test: {len(X_test)}")

print("\n[4/5] Training Random Forest...")
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

print("\n[5/5] Evaluating...")
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)
print(f"     MAE    : ₹{mae:,.0f}")
print(f"     R²     : {r2:.3f}")
print(f"     Accuracy: ~{max(0, r2*100):.1f}%")

joblib.dump(model,        os.path.join(BASE, "hotel_model.pkl"))
joblib.dump(encoders,     os.path.join(BASE, "hotel_encoders.pkl"))
joblib.dump(feature_cols, os.path.join(BASE, "hotel_features.pkl"))
joblib.dump(price_col,    os.path.join(BASE, "hotel_price_col.pkl"))

print(f"\n✅ Model saved: ml/hotel_model.pkl")
print("=" * 50)