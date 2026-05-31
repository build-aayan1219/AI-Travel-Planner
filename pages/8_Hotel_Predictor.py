# ============================================================
#  pages/8_Hotel_Predictor.py  —  ML Hotel Price Predictor
# ============================================================
import streamlit as st
import sys, os, joblib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml")

def hotel_model_trained():
    return os.path.exists(os.path.join(ML_DIR, "hotel_model.pkl"))

def predict_hotel(city, hotel_type, rating, stars):
    try:
        model    = joblib.load(os.path.join(ML_DIR, "hotel_model.pkl"))
        encoders = joblib.load(os.path.join(ML_DIR, "hotel_encoders.pkl"))
        features = joblib.load(os.path.join(ML_DIR, "hotel_features.pkl"))

        input_map = {"city": city, "hotel_type": hotel_type, "location": city,
                     "state": city, "category": hotel_type, "type": hotel_type,
                     "rating": rating, "review_score": rating, "stars": stars,
                     "hotel_class": stars, "review_count": 200, "number_of_reviews": 200}
        row = []
        for feat in features:
            val = input_map.get(feat, 0)
            if feat in encoders:
                le = encoders[feat]
                val = int(le.transform([str(val)])[0]) if str(val) in le.classes_ else 0
            row.append(float(val))

        pred = int(model.predict([row])[0])
        return {"price": pred, "range_low": int(pred*0.85), "range_high": int(pred*1.15), "error": None}
    except Exception as e:
        return {"error": str(e)}

st.set_page_config(page_title="Hotel Price Predictor", page_icon="🏨", layout="wide")
st.markdown("## 🏨 ML Hotel Price Predictor")
st.markdown('<span style="background:#e8eaff;color:#3730a3;border-radius:20px;padding:4px 14px;font-size:.8rem;font-weight:600">Random Forest · scikit-learn</span>', unsafe_allow_html=True)
st.markdown("Predict hotel price per night based on city and hotel type.")
st.markdown("---")

if not hotel_model_trained():
    st.error("⚠️ Hotel model not trained yet!")
    st.info("Make sure you have `data/hotel_prices.csv` from Kaggle, then run:")
    st.code("source venv/bin/activate\npython ml/train_hotel_model.py")
    st.markdown("**Download dataset:** [Google Indian Hotel Data — Kaggle](https://www.kaggle.com/datasets/alvinmanojalex/google-indian-hotel-data)")
    st.stop()

CITIES      = ["Mumbai","Delhi","Bangalore","Goa","Jaipur","Chennai","Hyderabad",
               "Kolkata","Pune","Ahmedabad","Kochi","Agra","Varanasi","Manali","Shimla"]
HOTEL_TYPES = ["Budget","Guest House","3 Star","4 Star","5 Star","Resort","Boutique","Hostel"]

col1, col2 = st.columns(2)
with col1:
    city       = st.selectbox("📍 City", CITIES)
    hotel_type = st.selectbox("🏨 Hotel Type", HOTEL_TYPES)
with col2:
    rating     = st.slider("⭐ Guest Rating", 1.0, 5.0, 4.0, 0.1)
    stars      = st.selectbox("🌟 Star Category", [1, 2, 3, 4, 5], index=2)

nights     = st.number_input("🌙 Number of Nights", 1, 30, 3)
group_size = st.number_input("👥 Number of Rooms Needed", 1, 10, 2)

st.markdown("---")

if st.button("🔮 Predict Hotel Price", use_container_width=True, type="primary"):
    with st.spinner("Predicting hotel price..."):
        result = predict_hotel(city, hotel_type, rating, stars)

    if result.get("error"):
        st.error(f"Prediction error: {result['error']}")
    else:
        price_per_night = result["price"]
        total_cost      = price_per_night * nights * group_size

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:16px;
                    padding:2rem;text-align:center;color:white;margin:1rem 0">
            <div style="font-size:1rem;opacity:.85">Predicted Price Per Night</div>
            <div style="font-size:3rem;font-weight:800">₹{price_per_night:,}</div>
            <div style="font-size:.9rem;opacity:.8">{hotel_type} · {city} · {stars} Star</div>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("💚 Minimum", f"₹{result['range_low']:,}/night")
        with c2: st.metric("🎯 Predicted", f"₹{price_per_night:,}/night")
        with c3: st.metric("🔴 Maximum", f"₹{result['range_high']:,}/night")

        st.markdown("---")
        st.markdown("### 📊 Total Stay Cost")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("🌙 Nights", nights)
        with c2: st.metric("🚪 Rooms", group_size)
        with c3: st.metric("💰 Total Stay Cost", f"₹{total_cost:,}")

        st.markdown("---")
        st.markdown("### 💡 Booking Tips")
        if stars >= 4:
            st.info("🏰 Premium hotel — book directly on hotel's website for best rate. Ask for early check-in.")
        elif stars == 3:
            st.info("🏩 Mid-range hotel — compare on MakeMyTrip vs direct booking. Prices vary by 15-20%.")
        else:
            st.info("🏠 Budget stay — OYO and Zostel offer verified budget options. Check reviews before booking.")

st.markdown("---")
st.markdown("### 🔗 Book Now")
c1, c2, c3, c4 = st.columns(4)
with c1: st.link_button("MakeMyTrip 🏨", "https://www.makemytrip.com/hotels/")
with c2: st.link_button("OYO Rooms 🛏️", "https://www.oyorooms.com/")
with c3: st.link_button("Booking.com 🌍", "https://www.booking.com/")
with c4: st.link_button("Agoda 🏩", "https://www.agoda.com/")

with st.expander("🧠 How does this ML model work?"):
    st.markdown("""
**Algorithm:** Random Forest Regressor

**Dataset:** `data/hotel_prices.csv` — Google Indian Hotel Data (Kaggle, 51 cities)

**Features:** City, hotel type/category, star rating, guest rating, number of reviews

**Encoding:** Text features (city, hotel type) converted using `LabelEncoder`

**Output:** Predicted price per night with ±15% confidence range
    """)