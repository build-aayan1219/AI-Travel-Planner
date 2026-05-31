# ============================================================
#  pages/4_Emergency_Info.py  —  Emergency info (Groq AI, FREE)
# ============================================================
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_helper import generate_emergency_info

st.set_page_config(page_title="Emergency Info", page_icon="🆘", layout="wide")
st.markdown("## 🆘 Emergency Info & Safety")
st.markdown("Stay safe during your trip")
st.markdown("---")

# Always-visible national numbers
st.markdown("### 📞 National Emergency Numbers — India")
c1, c2, c3, c4 = st.columns(4)
with c1: st.error("🚨 Police\n# 100")
with c2: st.error("🚑 Ambulance\n# 108")
with c3: st.error("🚒 Fire\n# 101")
with c4: st.warning("📞 All Emergencies\n# 112")

st.markdown("---")
destination = st.text_input("🗺️ Enter your destination for specific info", placeholder="e.g. Goa, Manali, Jaipur")

if st.button("🔍 Get Safety Info", use_container_width=True, type="primary"):
    if not destination:
        st.error("Please enter a destination!")
    else:
        with st.spinner(f"Getting safety info for {destination}..."):
            info = generate_emergency_info(destination)
        if info.startswith("⚠️"):
            st.error(info)
        else:
            st.markdown(f"### 🛡️ Safety Info for {destination}")
            st.markdown(info)

st.markdown("---")
st.markdown("### 🛡️ Travel Insurance")
st.info("""
**Why you need it:** Travel insurance covers medical emergencies, cancellations, and lost baggage.

**Recommended for Indian travelers:**
- **PolicyBazaar** — Compare multiple plans
- **HDFC ERGO** — Good domestic trip coverage
- **ICICI Lombard** — Widely accepted

Even Rs.500–1000 travel insurance can save lakhs in emergencies.
""")
c1, c2 = st.columns(2)
with c1: st.link_button("PolicyBazaar 🛡️", "https://www.policybazaar.com/travel-insurance/")
with c2: st.link_button("HDFC ERGO 🏥", "https://www.hdfcergo.com/travel-insurance")

st.markdown("---")
st.markdown("### 📱 Must-Have Safety Apps")
apps = [
    ("🆘 112 India", "Official emergency app by Govt. of India. Works offline."),
    ("🗺️ Google Maps Offline", "Download maps before travel."),
    ("🏥 Practo", "Find nearby doctors and hospitals."),
    ("💊 1mg", "Order medicines, find pharmacies."),
    ("🚗 Ola / Uber", "Safe, tracked cab rides with driver details."),
    ("📡 Truecaller", "Identify unknown callers, avoid scams."),
]
col_a, col_b = st.columns(2)
for i, (app, desc) in enumerate(apps):
    with col_a if i % 2 == 0 else col_b:
        st.markdown(f"**{app}**  \n{desc}")