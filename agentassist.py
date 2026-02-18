import streamlit as st
import requests
import google.generativeai as genai
import time

# --- CONFIGURATION (Safe Mode) ---
try:
    OWM_KEY = st.secrets["OWM_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=GEMINI_KEY)
except Exception:
    st.error("🔑 API Keys not found!")
    st.stop()

# --- HELPER: Get Best Model ---
def get_model_name():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prefer newer flash models
        for pref in ['gemini-2.0-flash', 'gemini-1.5-flash']:
            for m in available:
                if pref in m: return m
        return available[0]
    except:
        return "gemini-1.5-flash"

# --- MAIN UI ---
st.set_page_config(page_title="AI Weather Assistant", page_icon="🌂")
st.title("🌂 AI Umbrella Assistant")
st.write("Enter your destination below to see if you'll need protection from the elements.")

# Destination Input & Button
destination = st.text_input("Destination City:", placeholder="e.g. Paris, Tokyo, New York")
check_btn = st.button("Check Weather", type="primary")

# Create a container for the response so it stays in one place
response_container = st.container(border=True)

if check_btn:
    if not destination:
        st.warning("Please enter a city name first!")
    else:
        # 1. Processing Block (Visible in UI)
        with st.status("Fetching weather data...", expanded=True) as status:
            st.write(f"Contacting OpenWeatherMap for **{destination}**...")
            
            # Fetch Weather
            url = f"https://api.openweathermap.org/data/2.5/weather?q={destination}&appid={OWM_KEY}&units=metric"
            res = requests.get(url)
            
            if res.status_code == 200:
                data = res.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                
                st.write("✅ Weather data received.")
                st.write(f"🤖 Consulting Gemini with the {temp}°C forecast...")
                
                # AI Advice Logic
                try:
                    model_name = get_model_name()
                    model = genai.GenerativeModel(model_name)
                    prompt = f"In {destination}, it's {temp}C and {desc}. Tell me if I need an umbrella in a witty, charismatic way."
                    ai_res = model.generate_content(prompt)
                    advice = ai_res.text
                    status.update(label="Weather Check Complete!", state="complete", expanded=False)
                except Exception as e:
                    advice = "Assistant bro is shy, but it's gray out there. Take it just in case!"
                    status.update(label="AI Error", state="error")
                
                # 2. Response Box (Final Result)
                with response_container:
                    st.subheader(f"Current Weather in {destination.title()}")
                    st.info(f"**Condition:** {desc.capitalize()} | **Temp:** {temp}°C")
                    st.markdown("### ✨ I think:")
                    st.success(advice)
            else:
                status.update(label="City Not Found", state="error")

                st.error(f"Could not find weather for '{destination}'. Check your spelling!")
