# ============================================================
#  pages/5_Cost_Predictor.py  —  ML Trip Cost Predictor
# ============================================================
import streamlit as st
import sys, os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.predictor import predict_cost, is_model_trained, get_valid_options

st.set_page_config(page_title="Cost Predictor", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.predict-card{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;
padding:2rem;text-align:center;color:white;margin:1rem 0}
.predict-card .amount{font-size:3rem;font-weight:800;line-height:1.1}
.predict-card .label{font-size:1rem;opacity:.85;margin-top:4px}
.range-box{background:#f0f4ff;border-radius:10px;padding:14px;text-align:center}
</style>""", unsafe_allow_html=True)

st.markdown("## 🤖 ML Trip Cost Predictor")
st.markdown('<span style="background:#e8eaff;color:#3730a3;border-radius:20px;padding:4px 14px;font-size:.8rem;font-weight:600">Random Forest · scikit-learn</span>', unsafe_allow_html=True)
st.markdown("Enter your trip details and the ML model predicts the total cost.")
st.markdown("---")



if not is_model_trained():
    st.error("⚠️ Model not trained yet!")
    st.code("source venv/bin/activate\npython ml/train_model.py")
    st.stop()

options = get_valid_options()

DESTINATION_MAP = {
    "goa": "Beach", "puri": "Beach", "andaman": "Beach", "kovalam": "Beach",
    "manali": "Hill Station", "shimla": "Hill Station", "ooty": "Hill Station",
    "munnar": "Hill Station", "darjeeling": "Hill Station",
    "jaipur": "Heritage", "agra": "Heritage", "varanasi": "Heritage",
    "hampi": "Heritage", "khajuraho": "Heritage",
    "mumbai": "City", "delhi": "City", "bangalore": "City",
    "hyderabad": "City", "pune": "City", "chennai": "City",
    "ranthambore": "Wildlife", "jim corbett": "Wildlife",
    "kaziranga": "Wildlife", "bandhavgarh": "Wildlife",
}

col1, col2, col3 = st.columns(3)
with col1:
    destination = st.text_input("📍 Destination", placeholder="e.g. Goa, Manali, Jaipur")
    detected_type = DESTINATION_MAP.get(destination.lower().strip(), None)
    if detected_type:
        st.success(f"✅ Detected as: **{detected_type}**")
        destination_type = st.selectbox(
            "🗺️ Destination Type",
            options["destination_type"],
            index=options["destination_type"].index(detected_type),
        )
    else:
        st.info("ℹ️ Could not auto-detect — please select manually.")
        destination_type = st.selectbox("🗺️ Destination Type", options["destination_type"])
    days = st.number_input("📅 Number of Days", 1, 30, 4)
    group_size = st.number_input("👥 Group Size", 1, 20, 4)
with col2:
    trip_type = st.selectbox("🎯 Trip Type", options["trip_type"])
    season = st.selectbox("🌤️ Travel Season", options["season"])
with col3:
    transport_mode = st.selectbox("🚗 Transport Mode", options["transport_mode"])
    hotel_quality = st.selectbox("🏨 Hotel Quality", options["hotel_quality"])

st.markdown("---")

if st.button("🔮 Predict Trip Cost", use_container_width=True, type="primary"):
    with st.spinner("ML model is predicting..."):
        result = predict_cost(
            destination_type=destination_type, days=days,
            group_size=group_size, trip_type=trip_type,
            season=season, transport_mode=transport_mode,
            hotel_quality=hotel_quality
        )

    if result.get("error"):
        st.error(result["error"])
        st.stop()

    st.markdown(f"""
    <div class="predict-card">
        <div class="label">Predicted Total Trip Cost</div>
        <div class="amount">₹{result['predicted']:,}</div>
        <div class="label">for {group_size} people · {days} days · {destination_type}</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="range-box"><div style="font-size:.85rem;color:#666">Lower Estimate</div><div style="font-size:1.6rem;font-weight:700;color:#2e7d32">₹{result["range_low"]:,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="range-box"><div style="font-size:.85rem;color:#666">Per Person</div><div style="font-size:1.6rem;font-weight:700;color:#1565c0">₹{result["per_person"]:,}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="range-box"><div style="font-size:.85rem;color:#666">Upper Estimate</div><div style="font-size:1.6rem;font-weight:700;color:#c62828">₹{result["range_high"]:,}</div></div>', unsafe_allow_html=True)

    conf = result["confidence"]
    conf_color = {"High":"#2e7d32","Medium":"#e65100","Low":"#c62828"}[conf]
    conf_icon  = {"High":"✅","Medium":"⚠️","Low":"❗"}[conf]
    st.markdown(f'<p style="text-align:center;margin-top:8px">Confidence: <b style="color:{conf_color}">{conf_icon} {conf}</b></p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💰 Predicted Budget Breakdown")
    breakdown = result["breakdown"]
    cols = st.columns(len(breakdown))
    for i, (cat, amt) in enumerate(breakdown.items()):
        with cols[i]:
            st.metric(cat, f"₹{amt:,}", f"₹{amt//group_size:,}/person")

    st.markdown("#### Visual Breakdown")
    chart_data = pd.DataFrame({"Category": list(breakdown.keys()), "Amount (₹)": list(breakdown.values())}).set_index("Category")
    st.bar_chart(chart_data)

    st.markdown("---")
    st.markdown("### 📋 Trip Summary")
    st.dataframe(pd.DataFrame({
        "Detail": ["Destination Type","Days","Group Size","Trip Type","Season","Transport","Hotel"],
        "Your Choice": [destination_type, f"{days} days", f"{group_size} people", trip_type, season, transport_mode, hotel_quality]
    }), use_container_width=True, hide_index=True)

with st.expander("🧠 How does this ML model work?"):
    st.markdown("""
**Algorithm:** Random Forest Regressor (200 decision trees)

**Training data:** `data/trip_data.csv` — 180+ rows of Indian trip cost records

**Features used:** Destination type, days, group size, trip type, season, transport mode, hotel quality

**How it works:**
1. Text inputs (like "Beach", "Winter") → converted to numbers using `LabelEncoder`
2. 80% data used for training, 20% for testing
3. Random Forest builds 200 trees and averages their predictions
4. Model saved as `.pkl` file using `joblib`

**Evaluation metrics:** MAE (Mean Absolute Error) + R² Score (target > 0.85)
    """)