# ============================================================
#  pages/6_Flight_Predictor.py  —  ML Flight Price Predictor
# ============================================================
import streamlit as st
import sys, os, joblib
import pandas as pd
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml")

def flight_model_trained():
    return os.path.exists(os.path.join(ML_DIR, "flight_model.pkl"))

def predict_flight(airline, source_city, destination_city, departure_time,
                   stops, travel_class, duration, days_left):
    try:
        model    = joblib.load(os.path.join(ML_DIR, "flight_model.pkl"))
        encoders = joblib.load(os.path.join(ML_DIR, "flight_encoders.pkl"))
        features = joblib.load(os.path.join(ML_DIR, "flight_features.pkl"))

        input_map = {
            "airline": airline, "source_city": source_city,
            "departure_time": departure_time, "stops": stops,
            "arrival_time": "Morning", "destination_city": destination_city,
            "class": travel_class, "duration": duration, "days_left": days_left
        }
        row = []
        for feat in features:
            val = input_map.get(feat, 0)
            if feat in encoders:
                le = encoders[feat]
                val = int(le.transform([str(val)])[0]) if str(val) in le.classes_ else 0
            row.append(float(val))

        pred = int(model.predict([row])[0])
        return {"price": pred, "range_low": int(pred*0.88), "range_high": int(pred*1.12), "error": None}
    except Exception as e:
        return {"error": str(e)}

st.set_page_config(page_title="Flight Predictor", page_icon="✈️", layout="wide")
st.markdown("## ✈️ ML Flight Price Predictor")
st.markdown('<span style="background:#e8eaff;color:#3730a3;border-radius:20px;padding:4px 14px;font-size:.8rem;font-weight:600">Random Forest · scikit-learn</span>', unsafe_allow_html=True)
st.markdown("Predict flight ticket price based on your travel details.")
st.markdown("---")

if not flight_model_trained():
    st.error("⚠️ Flight model not trained yet!")
    st.code("source venv/bin/activate\npython ml/train_flight_model.py")
    st.stop()

AIRLINES   = ["IndiGo", "Air India", "Vistara", "GO_FIRST", "SpiceJet", "AirAsia"]
CITIES     = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
TIMES      = ["Early_Morning", "Morning", "Afternoon", "Evening", "Night", "Late_Night"]
STOPS      = ["zero", "one", "two_or_more"]
CLASSES    = ["Economy", "Business"]

col1, col2 = st.columns(2)
with col1:
    source_city = st.selectbox("🛫 From", CITIES, index=0)
    airline     = st.selectbox("✈️ Airline", AIRLINES)
    departure   = st.selectbox("🕐 Departure Time", TIMES, index=1)
    stops       = st.selectbox("🔄 Stops", STOPS)
with col2:
    dest_city   = st.selectbox("🛬 To", CITIES, index=1)
    travel_class= st.selectbox("💺 Class", CLASSES)
    duration    = st.number_input("⏱️ Duration (hours)", 0.5, 24.0, 2.2, 0.1)
    days_left   = st.number_input("📅 Days Until Travel", 1, 365, 30)

st.markdown("---")

if st.button("🔮 Predict Flight Price", use_container_width=True, type="primary"):
    if source_city == dest_city:
        st.error("Source and destination cities cannot be the same!")
    else:
        with st.spinner("Predicting flight price..."):
            result = predict_flight(airline, source_city, dest_city,
                                    departure, stops, travel_class, duration, days_left)
        if result.get("error"):
            st.error(f"Prediction error: {result['error']}")
        else:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a73e8,#0d47a1);border-radius:16px;
                        padding:2rem;text-align:center;color:white;margin:1rem 0">
                <div style="font-size:1rem;opacity:.85">Predicted Ticket Price</div>
                <div style="font-size:3rem;font-weight:800">₹{result['price']:,}</div>
                <div style="font-size:.9rem;opacity:.8">{airline} · {source_city} → {dest_city} · {travel_class}</div>
            </div>""", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("💚 Best Case", f"₹{result['range_low']:,}")
            with c2: st.metric("🎯 Predicted", f"₹{result['price']:,}")
            with c3: st.metric("🔴 Worst Case", f"₹{result['range_high']:,}")

            st.markdown("---")
            st.markdown("### 💡 Booking Tips")
            tips = {
                "zero": "✅ Non-stop flight — best choice for comfort. Book 3–4 weeks early.",
                "one": "⚠️ One stop — cheaper but longer. Check layover duration before booking.",
                "two_or_more": "💰 Multiple stops — cheapest option but very long journey time.",
            }
            st.info(tips.get(stops, "Book early for best prices."))

            if days_left > 30:
                st.success("🗓️ You're booking early — prices should be lower. Lock in now!")
            elif days_left > 7:
                st.warning("⏰ Moderate lead time — prices may still rise. Book soon.")
            else:
                st.error("🚨 Last minute booking — expect higher prices. Check all airlines.")

st.markdown("---")
st.markdown("### 🔗 Compare & Book")
c1, c2, c3, c4 = st.columns(4)
with c1: st.link_button("Google Flights ✈️", "https://flights.google.com")
with c2: st.link_button("MakeMyTrip ✈️", "https://www.makemytrip.com/flights/")
with c3: st.link_button("EaseMyTrip ✈️", "https://www.easemytrip.com")
with c4: st.link_button("Skyscanner 🌐", "https://www.skyscanner.co.in")

with st.expander("🧠 How does this ML model work?"):
    st.markdown("""
**Algorithm:** Random Forest Regressor

**Dataset:** `data/flight_prices.csv` — EaseMyTrip-style flight data

**Features:** Airline, source city, destination city, departure time, stops, class, duration, days until travel

**Key insight:** `days_left` is the most important feature — prices rise sharply as the travel date approaches.

**Encoding:** All text features (airline, city names) converted to numbers using `LabelEncoder`
    """)