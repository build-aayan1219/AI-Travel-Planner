# ============================================================
#  ml/predictor.py
#  Loads the trained cost predictor model and makes predictions
#  Used by pages/5_Cost_Predictor.py
# ============================================================

import joblib
import os

BASE = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH    = os.path.join(BASE, "cost_predictor_model.pkl")
ENCODERS_PATH = os.path.join(BASE, "encoders.pkl")
FEATURES_PATH = os.path.join(BASE, "feature_columns.pkl")


def is_model_trained() -> bool:
    """Check if cost predictor model files exist."""
    return (os.path.exists(MODEL_PATH) and
            os.path.exists(ENCODERS_PATH) and
            os.path.exists(FEATURES_PATH))


def get_valid_options() -> dict:
    """Returns valid dropdown choices — must match training data exactly."""
    return {
        "destination_type": ["Beach", "Hill Station", "City", "Heritage", "Wildlife"],
        "trip_type":        ["Adventure", "Relaxing Beach", "Cultural & Heritage",
                             "City Exploration", "Wildlife Safari"],
        "season":           ["Winter", "Summer", "Monsoon", "Spring"],
        "transport_mode":   ["Bus", "Train", "Flight"],
        "hotel_quality":    ["Budget", "Mid-range", "Luxury"],
    }


def predict_cost(destination_type, days, group_size,
                 trip_type, season, transport_mode, hotel_quality) -> dict:
    """
    Predicts total trip cost using the trained Random Forest model.

    Returns dict with:
      predicted, range_low, range_high, per_person, breakdown, confidence, error
    """
    if not is_model_trained():
        return {"error": "Model not trained. Run: python ml/train_model.py"}

    try:
        model    = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODERS_PATH)
        features = joblib.load(FEATURES_PATH)

        def encode(col, value):
            le = encoders.get(col)
            if le is None:
                return 0
            if str(value) in le.classes_:
                return int(le.transform([str(value)])[0])
            return 0

        input_row = [[
            encode("destination_type", destination_type),
            int(days),
            int(group_size),
            encode("trip_type", trip_type),
            encode("season", season),
            encode("transport_mode", transport_mode),
            encode("hotel_quality", hotel_quality),
        ]]

        predicted  = int(model.predict(input_row)[0])
        margin     = int(predicted * 0.15)
        range_low  = max(0, predicted - margin)
        range_high = predicted + margin
        per_person = predicted // group_size if group_size > 0 else predicted

        # Budget breakdown percentages by hotel quality
        pct_map = {
            "Budget":    {"🏨 Hotel": 30, "🚗 Transport": 25, "🍽️ Food": 30, "🎡 Activities": 10, "🛍️ Misc": 5},
            "Mid-range": {"🏨 Hotel": 35, "🚗 Transport": 22, "🍽️ Food": 25, "🎡 Activities": 12, "🛍️ Misc": 6},
            "Luxury":    {"🏨 Hotel": 45, "🚗 Transport": 18, "🍽️ Food": 20, "🎡 Activities": 12, "🛍️ Misc": 5},
        }
        pcts      = pct_map.get(hotel_quality, pct_map["Mid-range"])
        breakdown = {cat: int(predicted * p / 100) for cat, p in pcts.items()}

        confidence = "High" if days <= 10 and group_size <= 12 else \
                     "Medium" if days <= 14 and group_size <= 18 else "Low"

        return {
            "predicted":   predicted,
            "range_low":   range_low,
            "range_high":  range_high,
            "per_person":  per_person,
            "breakdown":   breakdown,
            "confidence":  confidence,
            "error":       None,
        }

    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}