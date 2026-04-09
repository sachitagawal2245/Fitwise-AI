import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = "sk-or-v1-fc304a289567870eb4dc43824abd0759bef8fe7f42702b22f4da824f5b4ee1f6s"

if not OPENROUTER_API_KEY:
    st.error("❌ API Key not found. Check your .env file.")
    st.stop()

if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "ai_output" not in st.session_state:
    st.session_state.ai_output = None


st.set_page_config(page_title="FITWISE AI", layout="centered")
st.title("💪 FitWise AI")
st.subheader("AI-powered Fitness & Diet Planner")

st.info(
    "This tool provides general fitness and diet guidance. "
    "Not a substitute for medical advice."
)

# ---------------- Form ----------------
with st.form("fitness"):
    st.markdown("### Enter your details")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=100)
    height = st.number_input("Height (cm)", min_value=50, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=200.0)
    country = st.text_input("Country")
    goal = st.selectbox("Fitness Goal", ["Fat loss", "Weight gain", "General fitness"])
    gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female"])
    daily_time = st.number_input("Daily Time (minutes)", min_value=10, max_value=180)
    target_weight = st.number_input("Target Weight (kg)", min_value=10, max_value=200)
    equipments = st.selectbox(
        "Equipment",
        ["None", "Basic", "Medium", "High"]
    )
    diet_preference = st.selectbox("Diet", ["Veg", "Non-veg", "Both"])
    activity_level = st.selectbox(
        "Activity Level",
        ["Sedentary", "Lightly active", "Moderately active"]
    )
    submit_btn = st.form_submit_button("Generate Plan")

# ---------------- Logic ----------------
def derive_workout_intensity(daily_time, activity_level):
    if daily_time < 20:
        base = "light"
    elif daily_time <= 45:
        base = "moderate"
    else:
        base = "high intensity"
    if activity_level == "Sedentary":
        return f"{base}, beginner"
    elif activity_level == "Lightly active":
        return f"{base}, intermediate"
    else:
        return f"{base}, challenging"


def build_prompt(data):
    intensity = derive_workout_intensity(
        data["daily_time"], data["activity_level"]
    )
    return f"""
You are a student fitness assistant.
Generate a personalized fitness and diet plan.
User details:
- Country: {data["country"]}
- Gender: {data["gender"]}
- Age: {data["age"]}
- Height: {data["height"]} cm
- Weight: {data["weight"]} kg
- Goal: {data["goal"]}
- Daily workout time: {data["daily_time"]} minutes
- Activity level: {data["activity_level"]}
- Equipment available: {data["equipment"]}
- Diet preference: {data["diet_preference"]}
Workout rules:
- Workout intensity should be {intensity}
- Avoid unsafe or advanced exercises
- Prefer simple, student-friendly routines
- Create a 7-day weekly workout plan
Diet rules:
- Suggest simple, commonly available meals based on {data["country"]} and {data["diet_preference"]} diet
- No supplements
- No medical advice
- Create a 7-day diet plan
Output format (use EXACT headings):
### WORKOUT PLAN
(Provide a detailed 7-day weekly workout plan with exercises, sets, and reps)
### DIET PLAN
(Provide a detailed 7-day daily diet plan with breakfast, lunch, dinner, and snacks)
### EXPLANATION
(Explain why this plan suits the user's goals, activity level, and available time)
Keep the language simple and clear. Be specific with exercises and meal suggestions.
"""


def call_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3-8b-instruct",  
        "messages": [
            {"role": "system", "content": "You are a fitness assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    data = response.json()
    if response.status_code != 200:
        raise Exception(data)
    if "choices" not in data:
        raise Exception("Invalid response from API")
    return data["choices"][0]["message"]["content"]


def split_ai_output(text):
    sections = {"workout": "", "diet": "", "explanation": ""}
    try:
        parts = text.split("### WORKOUT PLAN")[1]
        workout, rest = parts.split("### DIET PLAN")
        diet, explanation = rest.split("### EXPLANATION")
        sections["workout"] = workout.strip()
        sections["diet"] = diet.strip()
        sections["explanation"] = explanation.strip()
    except:
        sections["workout"] = text  # fallback

    return sections

# ---------------- Submit ----------------
if submit_btn:
    errors = []
    if not name.strip():
        errors.append("Name required")
    if not country.strip():
        errors.append("Country required")
    if goal == "Fat loss" and target_weight >= weight:
        errors.append("Target must be less than current weight")
    if goal == "Weight gain" and target_weight <= weight:
        errors.append("Target must be greater than current weight")
    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Generating plan..."):
            try:
                st.session_state.user_data = {
                    "name": name,
                    "age": age,
                    "height": height,
                    "weight": weight,
                    "goal": goal,
                    "daily_time": daily_time,
                    "activity_level": activity_level,
                    "equipment": equipments,
                    "diet_preference": diet_preference,
                    "country": country,
                    "gender": gender 
                }
                st.session_state.ai_output = call_openrouter(
                    build_prompt(st.session_state.user_data)
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ---------------- Output ----------------
if st.session_state.ai_output:
    sections = split_ai_output(st.session_state.ai_output)
    st.success(f"✅ Plan generated for {st.session_state.user_data['name']}")
    st.markdown("## 🏋️ Workout Plan")
    st.markdown(sections["workout"])
    st.markdown("## 🍽️ Diet Plan")
    st.markdown(sections["diet"])
    st.markdown("## 🧠 Explanation")
    st.markdown(sections["explanation"])
# ---------------- Regenerate ----------------
if st.session_state.user_data:
    if st.button("🔄 Regenerate Plan"):
        with st.spinner("Regenerating..."):
            try:
                st.session_state.ai_output = call_openrouter(
                    build_prompt(st.session_state.user_data)
                )
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
