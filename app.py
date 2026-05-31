# ============================================================
#  app.py  —  AI Group Travel Planner
#  Main page: Itinerary, Budget, Voting, Packing, Weather, PDF
#
#  APIs used:
#    - Gemini API (FREE) — AI features
#    - OpenWeatherMap API (FREE) — live weather
#
#  Run: streamlit run app.py
# ============================================================

# ── IMPORTS ──────────────────────────────────────────────────
import streamlit as st
import os
import re
import json
from dotenv import load_dotenv
from datetime import date
from fpdf import FPDF

# AI helper (uses Gemini internally)
from utils.ai_helper import (
    call_ai,
    generate_itinerary,
    generate_packing_list,
    generate_activity_options,
)
from utils.weather import get_current_weather, get_best_travel_months

# ── LOAD ENV ─────────────────────────────────────────────────
load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Group Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown(
    """
    <style>
 
/* ── Global ─────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: #F8F9FB;
}
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #EAEAEA;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}
 
/* ── Sidebar brand block ─────────────────── */
.brand-block {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 1rem 1.2rem;
    border-bottom: 1px solid #EAEAEA;
    margin-bottom: 0.5rem;
}
.brand-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: #534AB7;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: #EEEDFE;
}
.brand-name {
    font-size: 15px; font-weight: 600; color: #1A1A2E;
    line-height: 1.2;
}
.brand-sub {
    font-size: 11px; color: #888; margin-top: 1px;
}
 
/* ── Sidebar labels ──────────────────────── */
.sidebar-label {
    font-size: 11px;
    font-weight: 600;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.8rem 1rem 0.3rem;
}
 
/* ── Member chips ────────────────────────── */
.member-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 8px;
    background: #F4F3FE;
    margin: 3px 1rem;
    font-size: 12px;
    color: #3C3489;
}
.member-avatar {
    width: 22px; height: 22px;
    border-radius: 50%;
    background: #AFA9EC;
    display: flex; align-items: center; justify-content: center;
    font-size: 9px; font-weight: 600; color: #26215C;
}
 
/* ── Generate button ─────────────────────── */
.stButton > button[kind="primary"] {
    background: #534AB7 !important;
    border: none !important;
    color: white !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    height: 44px !important;
    transition: background 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3C3489 !important;
}
 
/* ── Hero section ────────────────────────── */
.hero-destination {
    font-size: 26px;
    font-weight: 700;
    color: #1A1A2E;
    margin-bottom: 4px;
}
.hero-meta {
    font-size: 13px;
    color: #666;
    margin-bottom: 12px;
}
 
/* ── Badges ──────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    margin-right: 4px;
}
.badge-purple { background: #EEEDFE; color: #534AB7; }
.badge-teal   { background: #E1F5EE; color: #0F6E56; }
.badge-amber  { background: #FAEEDA; color: #854F0B; }
.badge-coral  { background: #FAECE7; color: #993C1D; }
.badge-blue   { background: #E6F1FB; color: #185FA5; }
 
/* ── Stat cards row ──────────────────────── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 14px;
}
.stat-card {
    background: #F8F7FF;
    border: 1px solid #EEEDFE;
    border-radius: 10px;
    padding: 10px 14px;
}
.stat-label {
    font-size: 11px;
    color: #888;
    margin-bottom: 2px;
}
.stat-value {
    font-size: 18px;
    font-weight: 600;
    color: #1A1A2E;
}
.stat-sub {
    font-size: 11px;
    color: #999;
}
 
/* ── Tabs ─────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-bottom: 1px solid #EAEAEA;
    gap: 0;
    padding: 0 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px !important;
    font-weight: 400;
    color: #888 !important;
    padding: 12px 16px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #534AB7 !important;
    border-bottom: 2px solid #534AB7 !important;
    font-weight: 500 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.2rem 0.5rem !important;
    background: transparent;
}
 
/* ── Day cards (itinerary) ───────────────── */
.day-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-left: 4px solid #534AB7;
    border-radius: 0 10px 10px 0;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.day-title {
    font-size: 14px;
    font-weight: 600;
    color: #1A1A2E;
    margin-bottom: 8px;
}
.day-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #555;
    margin-bottom: 4px;
}
.day-time {
    font-size: 10px;
    color: #AAA;
    width: 26px;
    flex-shrink: 0;
}
.day-cost {
    background: #E1F5EE;
    color: #0F6E56;
    border-radius: 10px;
    padding: 1px 8px;
    font-size: 11px;
    font-weight: 500;
}
.day-tip {
    background: #FAEEDA;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 11px;
    color: #854F0B;
    margin-top: 8px;
}
 
/* ── Vote cards ──────────────────────────── */
.vote-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 10px;
    padding: 12px;
    cursor: pointer;
    transition: border-color 0.15s;
}
.vote-card.selected {
    border: 2px solid #534AB7;
    background: #EEEDFE;
}
.vote-card-name {
    font-size: 13px;
    font-weight: 500;
    color: #1A1A2E;
}
.vote-card-desc {
    font-size: 11px;
    color: #888;
    margin-top: 3px;
}
.vote-card-cost {
    font-size: 12px;
    color: #534AB7;
    font-weight: 500;
    margin-top: 6px;
}
 
/* ── Budget breakdown ────────────────────── */
.budget-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 10px;
    padding: 12px 14px;
}
.budget-cat {
    font-size: 12px;
    color: #888;
    margin-bottom: 4px;
}
.budget-amount {
    font-size: 20px;
    font-weight: 600;
    color: #1A1A2E;
}
.budget-per {
    font-size: 11px;
    color: #AAA;
}
.budget-bar {
    height: 4px;
    background: #EEE;
    border-radius: 4px;
    margin-top: 8px;
}
.budget-fill {
    height: 4px;
    border-radius: 4px;
    background: #534AB7;
}
 
/* ── Weather card ────────────────────────── */
.weather-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}
.weather-temp {
    font-size: 36px;
    font-weight: 600;
    color: #1A1A2E;
}
.weather-desc {
    font-size: 13px;
    color: #666;
}
.weather-loc {
    font-size: 11px;
    color: #AAA;
    margin-top: 2px;
}
.weather-stat-card {
    background: #F8F9FB;
    border-radius: 8px;
    padding: 8px 12px;
    text-align: center;
}
.weather-stat-val {
    font-size: 15px;
    font-weight: 600;
    color: #1A1A2E;
}
.weather-stat-lbl {
    font-size: 10px;
    color: #AAA;
}
 
/* ── AI tip box ──────────────────────────── */
.ai-tip {
    background: #EEEDFE;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #3C3489;
    margin-top: 10px;
}
 
/* ── Packing list ────────────────────────── */
.pack-card {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 10px;
    padding: 12px 14px;
}
.pack-card-title {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 8px;
}
.pack-item {
    font-size: 12px;
    color: #555;
    padding: 3px 0;
}
.pack-item.must {
    color: #1A1A2E;
    font-weight: 500;
}
 
/* ── Metric card override ────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #EAEAEA;
    border-radius: 10px;
    padding: 12px 14px;
}
 
/* ── Inputs and selects ──────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div {
    border-radius: 8px !important;
    border: 1px solid #EAEAEA !important;
    background: #FAFAFA !important;
    font-size: 13px !important;
}
 
/* ── Info / success / error boxes ───────── */
.stAlert {
    border-radius: 10px !important;
    font-size: 13px !important;
}
 
/* ── Spinner ─────────────────────────────── */
.stSpinner > div {
    border-top-color: #534AB7 !important;
}
 
/* ── Scrollbar ───────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D0CEEE; border-radius: 4px; }
 
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE INIT ────────────────────────────────────────
def init_state():
    defaults = {
        "members":          [],
        "itinerary":        "",
        "packing_list":     "",
        "votes":            {},
        "vote_options":     {},
        "generated":        False,
        "budget_breakdown": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()


# ── PDF EXPORT FUNCTION ───────────────────────────────────────
def export_pdf(destination, start_date, end_date, days, budget,
               group_size, members, itinerary_text, packing_text,
               budget_breakdown, votes):
    def safe_pdf_text(text):
        if not isinstance(text, str):
            text = str(text)
        return text

    def add_unicode_fonts(pdf):
        pdf.add_font(
            "DejaVu",
            "",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        )
        pdf.add_font(
            "DejaVu",
            "B",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        )
        pdf.add_font(
            "Emoji",
            "",
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        )

    def write_text(pdf, text, size=10, line_height=6):
        text = safe_pdf_text(text)
        if not text:
            return

        emoji_pattern = re.compile(
            r"([\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]+)"
        )
        parts = emoji_pattern.split(text)
        pdf.set_font("DejaVu", "", size)
        for part in parts:
            if not part:
                continue
            if emoji_pattern.fullmatch(part):
                pdf.set_font("Emoji", "", size)
                part = part.replace("\ufe0f", "")
            else:
                pdf.set_font("DejaVu", "", size)
            pdf.write(line_height, part)

    pdf = FPDF()
    add_unicode_fonts(pdf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("DejaVu", "B", 20)
    pdf.set_text_color(102, 126, 234)
    pdf.cell(0, 12, safe_pdf_text(f"Trip Plan: {destination}"), ln=True, align="C")

    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8,
             safe_pdf_text(
                 f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}  |  "
                 f"{days} Days  |  {group_size} People  |  Rs.{budget:,}"
             ),
             ln=True, align="C")
    pdf.ln(6)

    # Group Members
    pdf.set_font("DejaVu", "B", 13)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, "Group Members", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(80, 80, 80)
    for m in members:
        write_text(pdf, f"  - {m}", size=11, line_height=7)
        pdf.ln(3)
    pdf.ln(4)

    # Budget Breakdown
    pdf.set_font("DejaVu", "B", 13)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 8, "Budget Breakdown", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(80, 80, 80)
    for category, amount in budget_breakdown.items():
        write_text(
            pdf,
            f"  {category}: Rs.{amount:,}  (Rs.{amount // group_size:,} per person)",
            size=11,
            line_height=7,
        )
        pdf.ln(3)
    pdf.ln(4)

    # Group Votes
    if votes:
        pdf.set_font("DejaVu", "B", 13)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 8, "Group Voted Activities", ln=True)
        pdf.set_font("DejaVu", "", 11)
        pdf.set_text_color(80, 80, 80)
        for day_num, activity in votes.items():
            write_text(pdf, f"  Day {day_num}: {activity}", size=11, line_height=7)
            pdf.ln(3)
        pdf.ln(4)

    # Itinerary
    if itinerary_text:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 13)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 8, "Day-by-Day Itinerary", ln=True)
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(80, 80, 80)
        write_text(pdf, itinerary_text, size=10, line_height=6)
        pdf.ln(4)

    # Packing List
    if packing_text:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 13)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 8, "Packing List", ln=True)
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(80, 80, 80)
        write_text(pdf, packing_text, size=10, line_height=6)

    return bytes(pdf.output())


# ════════════════════════════════════════════════════════════
#  SIDEBAR — Trip Inputs
# ════════════════════════════════════════════════════════════
with st.sidebar:
    # Sidebar brand block (HTML uses classes defined in CSS above)
    st.markdown(
        '''
        <div class="brand-block">
            <div class="brand-icon">✈️</div>
            <div>
                <div class="brand-name">AI Trip Planner</div>
                <div class="brand-sub">Group travel made simple</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("## ✈️ Trip Details")
    st.markdown("---")

    destination = st.text_input("🗺️ Destination",
                                placeholder="e.g. Goa, Manali, Jaipur")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start", value=date.today())
    with col2:
        end_date = st.date_input("📅 End", value=date.today())

    days = max((end_date - start_date).days, 1)
    st.info(f"🗓️ **{days} day(s)** trip")

    budget = st.number_input(
        "💰 Total Budget (₹)",
        min_value=1000, max_value=1000000,
        value=20000, step=1000
    )

    trip_type = st.selectbox("🎯 Trip Type", [
        "Adventure", "Relaxing Beach", "Cultural and Heritage",
        "Hill Station", "Wildlife Safari", "City Exploration"
    ])

    season = st.selectbox("🌤️ Travel Season",
                          ["Winter", "Summer", "Monsoon", "Spring"])

    st.markdown("---")
    st.markdown("### 👥 Group Members")

    new_member = st.text_input("Add member name", placeholder="e.g. Aayan")
    food_pref  = st.selectbox("Food preference",
                               ["Veg", "Non-Veg", "Vegan", "No preference"])

    if st.button("➕ Add Member"):
        if new_member.strip():
            st.session_state.members.append(
                f"{new_member.strip()} ({food_pref})"
            )
            st.rerun()

    for i, m in enumerate(st.session_state.members):
        c1, c2 = st.columns([4, 1])
        with c1:
            # Render member as a styled chip so CSS rules apply
            avatar = (m.split()[0][0] if m else "U")
            st.markdown(
                f"<div class=\"member-chip\">"
                f"<div class=\"member-avatar\">{avatar}</div>"
                f"<div style=\"font-size:13px;color:#26215C;\">{m}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with c2:
            if st.button("✕", key=f"rm_{i}"):
                st.session_state.members.pop(i)
                st.rerun()

    group_size = max(len(st.session_state.members), 1)
    st.markdown(f"**Total: {group_size} people**")
    st.markdown(f"**Per person: ₹{budget // group_size:,}**")

    st.markdown("---")
    generate_btn = st.button(
        "🚀 Generate My Trip Plan!",
        use_container_width=True,
        type="primary"
    )


# ════════════════════════════════════════════════════════════
#  MAIN AREA — Title
# ════════════════════════════════════════════════════════════
st.markdown('<div class="hero-title">✈️ AI Group Travel Planner</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Plan your perfect group trip powered by Gemini AI + Machine Learning</div>',
    unsafe_allow_html=True
)

if not destination:
    st.info("👈 Fill in your trip details in the sidebar and click **Generate My Trip Plan!**")

    # Feature preview cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size:2rem">🤖</div>
            <h4>AI Itinerary</h4>
            <p style="color:#666;font-size:.9rem">Day-by-day plan generated by Gemini AI</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size:2rem">💰</div>
            <h4>Budget Splitter</h4>
            <p style="color:#666;font-size:.9rem">Auto-split costs per person</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div style="font-size:2rem">🗳️</div>
            <h4>Group Voting</h4>
            <p style="color:#666;font-size:.9rem">Vote on activities together</p>
        </div>""", unsafe_allow_html=True)
    st.stop()


# ════════════════════════════════════════════════════════════
#  GENERATE PLAN
# ════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def cached_itinerary(destination, days, budget, group_size, trip_type, members_info):
    return generate_itinerary(destination, days, budget, group_size, trip_type, members_info)

@st.cache_data(show_spinner=False)
def cached_packing(destination, days, trip_type, season):
    return generate_packing_list(destination, days, trip_type, season)

if generate_btn:
    if not destination.strip():
        st.error("Please enter a destination first!")
    else:
        members_info = (", ".join(st.session_state.members)
                        if st.session_state.members else "General group")

        with st.spinner("🤖 Gemini AI is planning your trip... (15–20 seconds)"):
            st.session_state.itinerary = cached_itinerary(
                destination, days, budget, group_size, trip_type, members_info
            )

        with st.spinner("🎒 Generating packing list..."):
            st.session_state.packing_list = cached_packing(
                destination, days, trip_type, season
            )

        # Default budget breakdown
        st.session_state.budget_breakdown = {
            "🏨 Hotels & Stays":   int(budget * 0.40),
            "🚗 Transport":        int(budget * 0.20),
            "🍽️ Food & Dining":   int(budget * 0.25),
            "🎡 Activities":       int(budget * 0.10),
            "🛍️ Shopping & Misc": int(budget * 0.05),
        }
        st.session_state.generated = True


# ════════════════════════════════════════════════════════════
#  RESULTS TABS
# ════════════════════════════════════════════════════════════
if st.session_state.generated:

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Itinerary",
        "💰 Budget",
        "🗳️ Group Vote",
        "🎒 Packing List",
        "🌤️ Weather",
    ])

    # ── TAB 1: ITINERARY ─────────────────────────────────────
    with tab1:
        st.markdown(
            f"### 🗺️ Your {days}-Day {trip_type} Trip to {destination}"
        )
        st.markdown(
            f"*{start_date.strftime('%d %b %Y')} → {end_date.strftime('%d %b %Y')}"
            f"  ·  {group_size} people  ·  ₹{budget:,} total*"
        )
        st.markdown("---")

        if st.session_state.itinerary.startswith("⚠️"):
            st.error(st.session_state.itinerary)
        else:
            chunks = st.session_state.itinerary.split("DAY ")
            for chunk in chunks:
                if chunk.strip():
                    first_line = chunk[:chunk.find("\n")]
                    rest       = chunk[chunk.find("\n"):].strip()
                    st.markdown(
                        f'<div class="day-card"><b>DAY {first_line}</b>'
                        f'<br><small>{rest}</small></div>',
                        unsafe_allow_html=True
                    )

        if st.button("🔄 Regenerate Itinerary"):
            members_info = (", ".join(st.session_state.members)
                            if st.session_state.members else "General group")
            with st.spinner("Regenerating..."):
                st.session_state.itinerary = generate_itinerary(
                    destination, days, budget, group_size, trip_type, members_info
                )
            st.rerun()

    # ── TAB 2: BUDGET ────────────────────────────────────────
    with tab2:
        st.markdown(f"### 💰 Budget Breakdown — ₹{budget:,} Total")
        st.markdown("*Adjust sliders to change how the budget is split*")
        st.markdown("---")

        hotel_pct     = st.slider("🏨 Hotels & Stays (%)",    0, 80, 40)
        transport_pct = st.slider("🚗 Transport (%)",         0, 50, 20)
        food_pct      = st.slider("🍽️ Food & Dining (%)",    0, 50, 25)
        activity_pct  = st.slider("🎡 Activities (%)",        0, 40, 10)
        misc_pct      = 100 - hotel_pct - transport_pct - food_pct - activity_pct

        if hotel_pct + transport_pct + food_pct + activity_pct > 100:
            st.error("⚠️ Total exceeds 100% — reduce some sliders.")
        else:
            st.success(f"✅ Shopping & Misc: {misc_pct}%")

            breakdown = {
                "🏨 Hotels & Stays":   int(budget * hotel_pct / 100),
                "🚗 Transport":        int(budget * transport_pct / 100),
                "🍽️ Food & Dining":   int(budget * food_pct / 100),
                "🎡 Activities":       int(budget * activity_pct / 100),
                "🛍️ Shopping & Misc": int(budget * misc_pct / 100),
            }
            st.session_state.budget_breakdown = breakdown

            cols = st.columns(len(breakdown))
            for i, (cat, amt) in enumerate(breakdown.items()):
                with cols[i]:
                    st.metric(cat, f"₹{amt:,}",
                              f"₹{amt // group_size:,}/person")

            st.markdown("---")
            st.markdown("### 👤 Per Person Split")
            per_person = budget // group_size
            if st.session_state.members:
                for member in st.session_state.members:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{member}**")
                    with c2:
                        st.markdown(
                            f'<span class="budget-pill">₹{per_person:,}</span>',
                            unsafe_allow_html=True
                        )
            else:
                st.info("Add group members in the sidebar to see per-person split.")

    # ── TAB 3: GROUP VOTING ──────────────────────────────────
    with tab3:
        st.markdown("### 🗳️ Group Activity Voting")
        st.markdown("Vote on which activities you prefer for each day")
        st.markdown("---")

        if not st.session_state.vote_options:
            st.info("Generate a trip plan first to see voting options.")
        else:
            for day_num, options_data in st.session_state.vote_options.items():
                st.markdown(f"#### Day {day_num} — Choose Your Activity")
                options      = options_data.get("options", [])
                option_names = [o["name"] for o in options]

                chosen = st.radio(
                    f"Day {day_num}",
                    option_names,
                    key=f"vote_day_{day_num}",
                    label_visibility="collapsed"
                )
                st.session_state.votes[day_num] = chosen

                cols = st.columns(len(options))
                for i, opt in enumerate(options):
                    with cols[i]:
                        is_chosen = opt["name"] == chosen
                        border = "2px solid #667eea" if is_chosen else "1px solid #dee2e6"
                        bg     = "#667eea15"          if is_chosen else "#f8f9fa"
                        st.markdown(f"""
                        <div style="background:{bg};border:{border};border-radius:8px;
                                    padding:12px;text-align:center;min-height:100px">
                            <b>{opt['name']}</b><br>
                            <small style="color:#666">{opt['description']}</small><br>
                            <span style="color:#667eea;font-weight:600">{opt['cost']}</span>
                            {"<br>✅ <b>Selected</b>" if is_chosen else ""}
                        </div>""", unsafe_allow_html=True)
                st.markdown("---")

            if st.session_state.votes:
                st.markdown("### 📊 Your Group's Selections")
                for day_num, activity in st.session_state.votes.items():
                    st.markdown(f"✅ **Day {day_num}:** {activity}")

    # ── TAB 4: PACKING LIST ──────────────────────────────────
    with tab4:
        st.markdown(f"### 🎒 Packing List for {destination}")
        st.markdown(f"*{days} days · {trip_type} · {season}*")
        st.markdown("---")

        if st.session_state.packing_list.startswith("⚠️"):
            st.error(st.session_state.packing_list)
        else:
            sections = st.session_state.packing_list.strip().split("\n\n")
            cols = st.columns(2)
            for i, section in enumerate(sections):
                with cols[i % 2]:
                    st.markdown(section)

        if st.button("🔄 Regenerate Packing List"):
            with st.spinner("Regenerating..."):
                st.session_state.packing_list = generate_packing_list(
                    destination, days, trip_type, season
                )
            st.rerun()

    # ── TAB 5: WEATHER ───────────────────────────────────────
    with tab5:
        st.markdown(f"### 🌤️ Current Weather in {destination}")
        st.markdown("---")

        # Best travel months (static data, no API needed)
        season_info = get_best_travel_months(destination)
        st.info(f"📅 **Best time to visit:** {season_info}")

        st.markdown("")
        if st.button("🔄 Fetch Live Weather"):
            with st.spinner("Fetching weather..."):
                weather = get_current_weather(destination)

            if "error" in weather:
                st.error(f"Could not fetch weather: {weather['error']}")
                st.info("💡 Try the city name in English — e.g. 'Goa', 'Mumbai', 'Manali'")
            else:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(
                        f"{weather['emoji']} Temperature",
                        f"{weather['temp']}°C",
                        f"Feels like {weather['feels_like']}°C"
                    )
                with c2:
                    st.metric("💧 Humidity", f"{weather['humidity']}%")
                with c3:
                    st.metric("🌥️ Condition", weather['description'])

                st.markdown(
                    f"*Live weather for **{weather['city']}, {weather['country']}***"
                )
                st.markdown(weather.get("tip", ""))

                with st.spinner("Getting AI travel tips for this weather..."):
                    from utils.ai_helper import generate_weather_tips
                    tips = generate_weather_tips(
                        destination, weather['description'], weather['temp']
                    )
                st.markdown("#### 💡 AI Travel Tips for Today's Weather")
                st.info(tips)
        else:
            st.info("👆 Click the button to fetch live weather for your destination.")

    # ── PDF EXPORT ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📄 Download Your Complete Trip Plan")

    if st.button("📥 Generate PDF", use_container_width=True):
        with st.spinner("Creating your PDF..."):
            try:
                pdf_bytes = export_pdf(
                    destination   = destination,
                    start_date    = start_date,
                    end_date      = end_date,
                    days          = days,
                    budget        = budget,
                    group_size    = group_size,
                    members       = st.session_state.members or ["Group"],
                    itinerary_text= st.session_state.itinerary,
                    packing_text  = st.session_state.packing_list,
                    budget_breakdown = st.session_state.budget_breakdown,
                    votes         = st.session_state.votes,
                )
                st.download_button(
                    label     = "⬇️ Download PDF Now",
                    data      = pdf_bytes,
                    file_name = f"{destination.replace(' ', '_')}_trip_plan.pdf",
                    mime      = "application/pdf",
                    use_container_width = True,
                )
            except Exception as e:
                st.error(f"PDF error: {str(e)}")

else:
    # Plan not generated yet but destination is entered
    if destination:
        st.markdown(f"### Ready to plan your trip to **{destination}**?")
        st.markdown(
            "Click **🚀 Generate My Trip Plan!** in the sidebar to get started."
        )