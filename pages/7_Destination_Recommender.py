# ============================================================
#  pages/7_Destination_Recommender.py  —  ML Destination Recommender
# ============================================================
import streamlit as st
import sys, os, joblib
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml")

def dest_model_trained():
    return os.path.exists(os.path.join(ML_DIR, "destination_model.pkl"))

def recommend_destinations(dest_type, season, budget_level,
                            adventure, culture, nature, beach, wildlife):
    try:
        model     = joblib.load(os.path.join(ML_DIR, "destination_model.pkl"))
        encoders  = joblib.load(os.path.join(ML_DIR, "destination_encoders.pkl"))
        target_le = joblib.load(os.path.join(ML_DIR, "destination_target_encoder.pkl"))
        scaler    = joblib.load(os.path.join(ML_DIR, "destination_scaler.pkl"))
        features  = joblib.load(os.path.join(ML_DIR, "destination_features.pkl"))
        dest_info = joblib.load(os.path.join(ML_DIR, "destination_info.pkl"))

        input_map = {
            "destination_type": dest_type, "best_season": season,
            "budget_level": budget_level,
            "adventure_score": adventure, "culture_score": culture,
            "nature_score": nature, "beach_score": beach,
            "wildlife_score": wildlife,
            "avg_hotel_budget": {"Budget":600,"Medium":1600,"High":3000}.get(budget_level,1600),
            "avg_food_budget_per_day": {"Budget":400,"Medium":800,"High":1200}.get(budget_level,800),
            "rating": 4.3
        }
        row = []
        for feat in features:
            val = input_map.get(feat, 0)
            if feat in encoders:
                le = encoders[feat]
                val = int(le.transform([str(val)])[0]) if str(val) in le.classes_ else 0
            row.append(float(val))

        row_scaled = scaler.transform([row])
        # Get top 5 nearest neighbours
        distances, indices = model.kneighbors(row_scaled, n_neighbors=min(5, len(dest_info)))
        top_indices = indices[0]
        results = []
        for idx in top_indices:
            if idx < len(dest_info):
                row_data = dest_info.iloc[idx]
                results.append({
                    "destination": row_data.get("destination","Unknown"),
                    "state":       row_data.get("state","India"),
                    "famous_for":  row_data.get("famous_for",""),
                    "best_season": row_data.get("best_season","All year"),
                    "budget_level":row_data.get("budget_level","Medium"),
                    "rating":      row_data.get("rating", 4.0),
                    "hotel_budget":row_data.get("avg_hotel_budget", 1500),
                    "food_budget": row_data.get("avg_food_budget_per_day", 700),
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]

st.set_page_config(page_title="Destination Recommender", page_icon="🗺️", layout="wide")
st.markdown("## 🗺️ ML Destination Recommender")
st.markdown('<span style="background:#e8eaff;color:#3730a3;border-radius:20px;padding:4px 14px;font-size:.8rem;font-weight:600">K-Nearest Neighbors · scikit-learn</span>', unsafe_allow_html=True)
st.markdown("Tell us your preferences and the ML model recommends your perfect destination.")
st.markdown("---")

if not dest_model_trained():
    st.error("⚠️ Destination model not trained yet!")
    st.code("source venv/bin/activate\npython ml/train_destination_model.py")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🎯 What kind of trip?")
    dest_type   = st.selectbox("Destination Type", ["Beach","Hill Station","Heritage","City","Adventure","Wildlife"])
    season      = st.selectbox("When are you travelling?", ["Winter","Summer","Monsoon","Spring"])
    budget_level= st.selectbox("Budget Level", ["Budget","Medium","High"])

with col2:
    st.markdown("### ⭐ Rate your interests (1-10)")
    adventure = st.slider("🧗 Adventure", 1, 10, 5)
    culture   = st.slider("🏛️ Culture & Heritage", 1, 10, 5)
    nature    = st.slider("🌿 Nature & Scenery", 1, 10, 5)
    beach     = st.slider("🏖️ Beach & Water", 1, 10, 3)
    wildlife  = st.slider("🐯 Wildlife", 1, 10, 3)

st.markdown("---")

if st.button("🔍 Find My Perfect Destination", use_container_width=True, type="primary"):
    with st.spinner("ML model finding best destinations for you..."):
        results = recommend_destinations(dest_type, season, budget_level,
                                         adventure, culture, nature, beach, wildlife)

    if results and "error" in results[0]:
        st.error(f"Error: {results[0]['error']}")
    else:
        st.markdown("### 🏆 Top Recommended Destinations For You")
        st.markdown("*Based on your preferences — ranked by similarity using KNN algorithm*")
        st.markdown("")

        for i, dest in enumerate(results):
            medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
            budget_icon = {"Budget":"💚","Medium":"💛","High":"🔴"}.get(str(dest.get("budget_level","")),"💛")
            rating = float(dest.get("rating", 4.0))
            stars  = "⭐" * int(rating) + ("" if rating == int(rating) else "½")

            with st.container():
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:16px;
                             border:1px solid #e2e8f0;margin:8px 0;
                             border-left:4px solid #667eea">
                    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                        <span style="font-size:1.8rem">{medal}</span>
                        <div>
                            <h3 style="margin:0;color:#1e293b">{dest['destination']}</h3>
                            <p style="margin:2px 0;color:#64748b;font-size:.9rem">
                                📍 {dest['state']}  ·  {stars}  ·  {budget_icon} {dest.get('budget_level','')}
                            </p>
                        </div>
                    </div>
                    <p style="margin:8px 0 0;color:#475569">
                        🌟 <b>Famous for:</b> {dest.get('famous_for','')} &nbsp;|&nbsp;
                        📅 <b>Best season:</b> {dest.get('best_season','')} &nbsp;|&nbsp;
                        🏨 <b>Hotel from:</b> ₹{int(dest.get('hotel_budget',0)):,}/night &nbsp;|&nbsp;
                        🍽️ <b>Food/day:</b> ₹{int(dest.get('food_budget',0)):,}
                    </p>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        top_dest = results[0]["destination"] if results else "your destination"
        c1, c2, c3 = st.columns(3)
        with c1: st.link_button(f"Plan trip to {top_dest} 🗺️", f"https://www.google.com/search?q=travel+guide+{top_dest}+India")
        with c2: st.link_button(f"Hotels in {top_dest} 🏨", f"https://www.makemytrip.com/hotels/{top_dest.lower().replace(' ','-')}-hotels.html")
        with c3: st.link_button("Book Trains 🚆", "https://www.irctc.co.in")

with st.expander("🧠 How does this ML model work?"):
    st.markdown("""
**Algorithm:** K-Nearest Neighbors (KNN) Classifier

**Dataset:** `data/master_travel_dataset.csv` — 87 Indian destinations

**How it works:**
1. Your preferences (adventure, culture, nature etc.) are converted to a numeric vector
2. KNN finds the 5 destinations most *similar* to your vector in the dataset
3. Similarity is measured using Euclidean distance
4. Destinations are ranked closest-first

**Why KNN for recommendations?**
- Simple and interpretable — "find things similar to what you want"
- Works well for small datasets (our 87 destinations)
- No training needed — just measure distances at prediction time
- `StandardScaler` normalises all features so adventure (1-10) and hotel budget (₹) are comparable
    """)