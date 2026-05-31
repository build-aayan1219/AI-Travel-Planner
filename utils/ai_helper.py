# ============================================================
#  utils/ai_helper.py
#  All AI functions using GEMINI API (FREE)
#  Model: gemini-1.5-flash
#  Get free key: console.gemini.com
# ============================================================

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)



import time

def call_ai(prompt: str, max_tokens: int = 1024) -> str:
    if not GEMINI_KEY:
        return "⚠️ GEMINI_API_KEY not found in .env file."
    
    for attempt in range(3):          # retry up to 3 times
        try:
            model    = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            err = str(e)
            if "429" in err:          # rate limit hit
                wait = (attempt + 1) * 20   # wait 20s, 40s, 60s
                time.sleep(wait)
                continue
            return f"⚠️ Gemini API error: {err}"
    
    return "⚠️ Rate limit hit. Please wait 1 minute and try again."


def generate_itinerary(destination, days, budget, group_size, trip_type, members_info):
    prompt = f"""
You are an expert Indian travel planner. Create a detailed {days}-day itinerary.
Destination: {destination} | Days: {days} | Budget: Rs.{budget:,} | Group: {group_size} people
Trip type: {trip_type} | Members: {members_info}

Format EXACTLY like this for every day:
DAY [number]: [Creative theme]
Morning: [activity] — Cost: Rs.[amount]
Afternoon: [activity] — Cost: Rs.[amount]
Evening: [activity] — Cost: Rs.[amount]
Local Food: [dish] at [place]
Tip: [one practical tip]

Be realistic and within budget. Give all {days} days.
"""
    return call_ai(prompt, max_tokens=2000)


def generate_packing_list(destination, days, trip_type, season):
    prompt = f"""
Create a packing list for a {days}-day {trip_type} trip to {destination} in {season}.
Sections: 📄 Documents and Money | 👕 Clothing | 🧴 Toiletries and Medicine
📱 Gadgets | 🏕️ Activity-Specific Items | 🆘 Emergency and Safety
Mark must-haves with ⭐. Be specific to {destination} and {season}.
"""
    return call_ai(prompt, max_tokens=1000)


def generate_activity_options(destination, day_number, trip_type):
    prompt = f"""Suggest exactly 3 activity options for Day {day_number} of a {trip_type} trip to {destination}.
Reply ONLY with this JSON, no other text:
{{"options":[{{"name":"Activity name","description":"One sentence","cost":"Rs.XXX per person","duration":"X hours"}},{{"name":"Activity name","description":"One sentence","cost":"Rs.XXX per person","duration":"X hours"}},{{"name":"Activity name","description":"One sentence","cost":"Rs.XXX per person","duration":"X hours"}}]}}"""
    raw = call_ai(prompt, max_tokens=400)
    try:
        raw = raw.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {"options": [
            {"name": "Sightseeing Tour", "description": "Visit top landmarks", "cost": "Rs.500 per person", "duration": "3 hours"},
            {"name": "Local Market Walk", "description": "Explore markets and street food", "cost": "Rs.300 per person", "duration": "2 hours"},
            {"name": "Nature Walk", "description": "Relaxing walk in natural area", "cost": "Free", "duration": "2 hours"},
        ]}


def generate_hotel_suggestions(destination, budget_per_night, group_size, trip_type):
    prompt = f"""Suggest 3 hotels in {destination} for {group_size} people. Budget per night: Rs.{budget_per_night:,}. Trip: {trip_type}.
Reply ONLY with this JSON:
{{"hotels":[{{"name":"Hotel name","type":"Budget","price_per_night":"Rs.XXXX","why":"One reason","area":"Area"}},{{"name":"Hotel name","type":"Mid-range","price_per_night":"Rs.XXXX","why":"One reason","area":"Area"}},{{"name":"Hotel name","type":"Luxury","price_per_night":"Rs.XXXX","why":"One reason","area":"Area"}}]}}"""
    raw = call_ai(prompt, max_tokens=500)
    try:
        raw = raw.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {"hotels": [
            {"name": "Budget Stay", "type": "Budget", "price_per_night": f"Rs.{budget_per_night//2:,}", "why": "Affordable and central", "area": "City Centre"},
            {"name": "Mid-Range Hotel", "type": "Mid-range", "price_per_night": f"Rs.{budget_per_night:,}", "why": "Good value", "area": "Tourist Area"},
            {"name": "Premium Resort", "type": "Luxury", "price_per_night": f"Rs.{budget_per_night*2:,}", "why": "Best comfort", "area": "Prime Location"},
        ]}


def generate_food_guide(destination, food_preferences):
    prompt = f"""Create a food guide for tourists in {destination}, India. Preferences: {food_preferences}.
Include: 🍽️ 5 Must-Try Dishes with price | 🏪 Where to Eat (3 types) | 💡 3 Food Tips | ⚠️ Things to Avoid"""
    return call_ai(prompt, max_tokens=800)


def generate_transport_guide(destination, origin_city, group_size, budget):
    prompt = f"""Transport guide for {group_size} people from {origin_city} to {destination}. Budget: Rs.{budget:,}.
Cover: 🚆 How to reach (train/bus/flight + Rs. cost) | 🚗 Local transport | 💡 3 money-saving tips | 📱 Useful apps"""
    return call_ai(prompt, max_tokens=700)


def generate_emergency_info(destination):
    prompt = f"""Emergency info for tourists in {destination}, India.
Include: 🚨 Emergency numbers | 🏥 Hospital finding tips | 💊 5 medicines to carry | ⚠️ 3 tourist scams | ✅ 3 safety tips"""
    return call_ai(prompt, max_tokens=700)


def generate_weather_tips(destination, weather_desc, temp):
    prompt = f"""Weather in {destination} is {weather_desc} at {temp}°C. Give 3 short travel tips for tourists. One sentence each, start with emoji."""
    return call_ai(prompt, max_tokens=200)