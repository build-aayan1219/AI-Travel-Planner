# ============================================================
#  ml/train_destination_model.py
#  Trains destination recommender on master_travel_dataset.csv
#  Algorithm: K-Nearest Neighbors (KNN)
#
#  HOW TO RUN:
#  python ml/train_destination_model.py
# ============================================================
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib, os

print("=" * 50)
print("  Destination Recommender — Model Training")
print("=" * 50)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data", "master_travel_dataset.csv")

print("\n[1/5] Loading dataset...")
try:
    df = pd.read_csv(DATA)
except FileNotFoundError:
    print(f"❌ File not found: {DATA}")
    exit()
print(f"     Loaded: {df.shape[0]} destinations × {df.shape[1]} columns")

print("\n[2/5] Preparing features...")
feature_cols = ["destination_type", "best_season", "adventure_score",
                "culture_score", "nature_score", "beach_score",
                "wildlife_score", "budget_level",
                "avg_hotel_budget", "avg_food_budget_per_day", "rating"]

feature_cols = [c for c in feature_cols if c in df.columns]
print(f"     Using: {feature_cols}")

df = df.dropna(subset=feature_cols + ["destination"])

encoders = {}
cat_cols = ["destination_type", "best_season", "budget_level"]
for col in [c for c in cat_cols if c in df.columns]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le
    print(f"     Encoded {col}: {len(le.classes_)} classes")

target_le = LabelEncoder()
df["destination_encoded"] = target_le.fit_transform(df["destination"])

print("\n[3/5] Splitting data...")
X = df[feature_cols]
y = df["destination_encoded"]

# For small datasets use 70/30 split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print(f"     Train: {len(X_train)} | Test: {len(X_test)}")

print("\n[4/5] Scaling + Training KNN...")
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

# k=5 means find 5 nearest destinations
model = KNeighborsClassifier(n_neighbors=5, metric="euclidean")
model.fit(X_train_s, y_train)
print("     Done!")

print("\n[5/5] Evaluating...")
y_pred = model.predict(X_test_s)
acc = accuracy_score(y_test, y_pred)
print(f"     Accuracy: {acc*100:.1f}%")
print("     (Note: KNN accuracy on small datasets is lower — the model")
print("      still gives good recommendations based on similarity)")

joblib.dump(model,       os.path.join(BASE, "destination_model.pkl"))
joblib.dump(encoders,    os.path.join(BASE, "destination_encoders.pkl"))
joblib.dump(target_le,   os.path.join(BASE, "destination_target_encoder.pkl"))
joblib.dump(scaler,      os.path.join(BASE, "destination_scaler.pkl"))
joblib.dump(feature_cols,os.path.join(BASE, "destination_features.pkl"))

dest_info = df[["destination", "state", "destination_type", "best_season",
                "budget_level", "rating", "famous_for",
                "avg_hotel_budget", "avg_food_budget_per_day"]].copy()
joblib.dump(dest_info, os.path.join(BASE, "destination_info.pkl"))

print(f"\n✅ Model saved: ml/destination_model.pkl")
print(f"✅ Destination info saved for display")
print("=" * 50)