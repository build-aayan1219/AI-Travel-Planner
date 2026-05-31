# ============================================================
#  pages/1_Hotels.py  —  Hotel suggestions (GEMINI AI, FREE)
# ============================================================
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_helper import generate_hotel_suggestions, call_ai

st.set_page_config(page_title="Hotel Suggestions", page_icon="🏨", layout="wide")
st.markdown("## 🏨 Hotel & Stay Suggestions")
st.markdown("Find the best places to stay within your budget")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    destination = st.text_input("🗺️ Destination", placeholder="e.g. Goa, Manali")
with col2:
    total_budget = st.number_input("💰 Total Hotel Budget (₹)", min_value=500, max_value=500000, value=8000, step=500)
with col3:
    nights = st.number_input("🌙 Number of Nights", min_value=1, max_value=30, value=3)

col4, col5 = st.columns(2)
with col4:
    group_size = st.number_input("👥 Group Size", min_value=1, max_value=20, value=4)
with col5:
    trip_type = st.selectbox("🎯 Trip Type", ["Adventure", "Relaxing Beach", "Cultural and Heritage", "Hill Station", "City Exploration"])

budget_per_night = total_budget // nights if nights > 0 else total_budget
st.info(f"💡 Per night: ₹{budget_per_night:,} for group  |  ₹{budget_per_night // group_size:,} per person")

if st.button("🔍 Find Hotels", use_container_width=True, type="primary"):
    if not destination:
        st.error("Please enter a destination!")
    else:
        with st.spinner("Finding best stays..."):
            hotel_data = generate_hotel_suggestions(destination, budget_per_night, group_size, trip_type)

        hotels = hotel_data.get("hotels", [])
        if not hotels:
            st.error("Could not load hotel suggestions. Check your GEMINI_API_KEY.")
        else:
            st.markdown(f"### Best Stays in {destination}")
            color_map = {"Budget": "#e8f5e9", "Mid-range": "#e3f2fd", "Luxury": "#fce4ec"}
            icon_map  = {"Budget": "🏠", "Mid-range": "🏩", "Luxury": "🏰"}
            cols = st.columns(len(hotels))
            for i, hotel in enumerate(hotels):
                with cols[i]:
                    htype = hotel.get("type", "Mid-range")
                    st.markdown(f"""
                    <div style="background:{color_map.get(htype,'#f5f5f5')};border-radius:12px;
                                padding:16px;border:1px solid #ddd;text-align:center;min-height:180px">
                        <div style="font-size:2rem">{icon_map.get(htype,'🏨')}</div>
                        <h4 style="margin:8px 0;color:#1e293b">{hotel['name']}</h4>
                        <span style="background:#fff;padding:3px 10px;border-radius:20px;
                             font-size:0.8rem;font-weight:600">{htype}</span>
                        <p style="margin:10px 0;color:#555;font-size:0.9rem">📍 {hotel.get('area','Central')}</p>
                        <p style="font-size:1.2rem;font-weight:700;color:#1e293b">{hotel['price_per_night']}/night</p>
                        <p style="color:#666;font-size:0.85rem">✅ {hotel['why']}</p>
                    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 💡 Booking Tips for " + destination)
        with st.spinner("Getting tips..."):
            tips = call_ai(f"Give 4 practical hotel booking tips for {destination}, group of {group_size}, budget Rs.{total_budget:,} for {nights} nights. Use bullet points.")
        st.info(tips)

st.markdown("---")
st.markdown("### 🔗 Book Now")
c1, c2, c3, c4 = st.columns(4)
with c1: st.link_button("MakeMyTrip 🏨", "https://www.makemytrip.com/hotels/")
with c2: st.link_button("OYO Rooms 🛏️", "https://www.oyorooms.com/")
with c3: st.link_button("Booking.com 🌍", "https://www.booking.com/")
with c4: st.link_button("Goibibo 🏩", "https://www.goibibo.com/hotels/")