# ============================================================
#  pages/3_Transport.py  —  Transport guide (Groq AI, FREE)
# ============================================================
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_helper import generate_transport_guide

st.set_page_config(page_title="Transport Guide", page_icon="🚆", layout="wide")
st.markdown("## 🚆 Transport Guide")
st.markdown("How to get there and get around")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    origin = st.text_input("📍 Your City", placeholder="e.g. Pune, Mumbai")
with col2:
    destination = st.text_input("🗺️ Destination", placeholder="e.g. Goa, Manali")
with col3:
    group_size = st.number_input("👥 Group Size", 1, 20, 4)

transport_budget = st.number_input("💰 Total Transport Budget (₹)", 500, 200000, 5000, 500)
st.info(f"💡 Per person transport budget: ₹{transport_budget // group_size:,}")

if st.button("🔍 Get Transport Options", use_container_width=True, type="primary"):
    if not origin or not destination:
        st.error("Please enter both your city and destination!")
    else:
        with st.spinner("Finding best transport options..."):
            guide = generate_transport_guide(destination, origin, group_size, transport_budget)
        if guide.startswith("⚠️"):
            st.error(guide)
        else:
            st.markdown(f"### 🗺️ {origin} → {destination}")
            st.markdown(guide)

st.markdown("---")
st.markdown("### 🔗 Quick Booking Links")
c1, c2, c3, c4 = st.columns(4)
with c1: st.link_button("IRCTC Trains 🚆", "https://www.irctc.co.in")
with c2: st.link_button("RedBus Buses 🚌", "https://www.redbus.in")
with c3: st.link_button("IndiGo Flights ✈️", "https://www.goindigo.in")
with c4: st.link_button("Ola Cabs 🚗", "https://www.olacabs.com")

st.markdown("---")
if st.session_state.get("origin") and st.session_state.get("destination"):
    st.link_button("📍 View Route on Google Maps",
        f"https://www.google.com/maps/dir/{origin}/{destination}")
else:
    st.link_button("📍 Open Google Maps", "https://maps.google.com")