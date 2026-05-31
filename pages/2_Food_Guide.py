# ============================================================
#  pages/2_Food_Guide.py  —  Local food guide (Groq AI, FREE)
# ============================================================
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_helper import generate_food_guide

st.set_page_config(page_title="Food Guide", page_icon="🍽️", layout="wide")
st.markdown("## 🍽️ Local Food Guide")
st.markdown("Discover the best food your destination has to offer")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    destination = st.text_input("🗺️ Destination", placeholder="e.g. Goa, Jaipur, Kerala")
with col2:
    food_prefs = st.multiselect(
        "🥗 Group Food Preferences",
        ["Vegetarian", "Non-Vegetarian", "Vegan", "Jain Food", "No Seafood", "No Spicy Food", "Halal", "No Restrictions"],
        default=["No Restrictions"]
    )

col3, col4 = st.columns(2)
with col3:
    budget_per_meal = st.slider("💰 Budget per meal per person (₹)", 50, 2000, 300, 50)
with col4:
    people = st.number_input("👥 Number of people", 1, 20, 4)

days = st.number_input("📅 Trip Duration (days)", 1, 30, 3)

if st.button("🍜 Generate Food Guide", use_container_width=True, type="primary"):
    if not destination:
        st.error("Please enter a destination!")
    else:
        prefs_str = ", ".join(food_prefs) if food_prefs else "No specific preferences"
        with st.spinner(f"Finding the best food in {destination}..."):
            guide = generate_food_guide(destination, prefs_str)

        if guide.startswith("⚠️"):
            st.error(guide)
        else:
            col_a, col_b = st.columns([3, 2])
            with col_a:
                st.markdown(f"### 🗺️ Food Guide for {destination}")
                st.markdown(guide)
            with col_b:
                st.markdown("### 💰 Meal Budget Calculator")
                meals_per_day = st.number_input("Meals per day", 1, 5, 3, key="mpd")
                total_food = budget_per_meal * people * meals_per_day * days
                st.metric("Total Food Budget", f"₹{total_food:,}")
                st.metric("Per Person Total", f"₹{total_food // people:,}")
                st.metric("Per Day (group)", f"₹{budget_per_meal * people * meals_per_day:,}")

st.markdown("---")
st.markdown("### 📱 Order Food Locally")
c1, c2, c3 = st.columns(3)
with c1: st.link_button("Zomato 🍕", "https://www.zomato.com")
with c2: st.link_button("Swiggy 🛵", "https://www.swiggy.com")
with c3: st.link_button("EatSure 🥘", "https://www.eatsure.com")